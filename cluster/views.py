from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
import subprocess
import xml.etree.ElementTree as ET
from cluster.models import Agent, Agent_Param
import os
import json
# Create your views here.

def index(request):
    template = loader.get_template('index.html')
    context = {}
    return HttpResponse(template.render(context,request))


##### NODES

def nodes(request):
    template = loader.get_template('nodes.html')
    #Conseguimos la información de los nodos para enviarla a la vista
    nodes = []
    out = subprocess.run(["crm", "node", "status"], stdout=subprocess.PIPE)
    out = ET.fromstring(out.stdout.decode('utf-8'))

    for node in out:
        status = "online"
        maintenance = False
        for instance_attributes in node:
            for nvpair in instance_attributes:
                if nvpair.get('name') == "standby" and nvpair.get('value') == "on":
                    status = "standby"
                if nvpair.get('name') == "maintenance" and nvpair.get('value') == "on":
                    maintenance = True


        nodes.append({"id": node.get('id'), "name": node.get('uname'), "status": status, "maintenance": maintenance})

    context = {
        'nodes': nodes,
    }

    return HttpResponse(template.render(context, request))

def nodes_online(request, node_name):
    subprocess.run(["crm", "node", "online", node_name], stdout=subprocess.PIPE)
    return redirect('cluster:nodes')

def nodes_standby(request, node_name):
    subprocess.run(["crm", "node", "standby", node_name], stdout=subprocess.PIPE)
    return redirect('cluster:nodes')

def nodes_maintenance(request, node_name):
    subprocess.run(["crm", "node", "maintenance", node_name], stdout=subprocess.PIPE)
    return redirect('cluster:nodes')

def nodes_ready(request, node_name):
    subprocess.run(["crm", "node", "ready", node_name], stdout=subprocess.PIPE)
    return redirect('cluster:nodes')




##### RESOURCES

def resources(request):
    template = loader.get_template('resources.html')
    context = {}
    return HttpResponse(template.render(context, request))

def resources_new(request):
    template = loader.get_template('resources_new.html')

    agents = Agent.objects.all()

    context = {
        'agents': agents,
    }
    return HttpResponse(template.render(context, request))

def resources_form(request, agent_name):
    template = loader.get_template('resources_form.html')

    params = Agent_Param.objects.all().filter(agent__name=agent_name)

    context = {
        'agent_name': agent_name,
        'params': params,
    }
    return HttpResponse(template.render(context, request))

def resources_created(request, agent_name):
    template = loader.get_template('resources_sucessful.html')

    # Se crea un diccionario para la entrada de datos del formulario y se guardan todos, si no viene ningun valor se pone None por defecto
    input = dict()
    params = Agent_Param.objects.all().filter(agent__name=agent_name)
    for param in params:
        aux = request.POST.get(param.name, None)
        # Eliminar los campos con Nones
        if aux is not None and aux != '':
            input[param.name] = aux

    #Ahora es necesario crear el recurso mediante crmsh. Comandos
    # crm configure primitive <nombre> ocf:heartbeat:pacemaker:<ra_name> params <name_param>=<value_param>
    nombre = request.POST.get("nombre", None)
    agent = Agent.objects.all().filter(name=agent_name)
    for ag in agent:
        agent = ag
    auxstr = "crm configure primitive " + nombre  + " " +  agent.resource_str

    if len(input) > 0:
        auxstr+= " params"

    for key, value in input.items():
        auxstr +=" " + key + "=" + value

    return_code = subprocess.call(auxstr, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    if return_code != 0:
        msg = "El recurso no se ha creado correctamente, compruebe que ya exista con ese nombre o haya algún parametro incorrecto."
    else:
        msg = "El recurso se ha creado correctamente."
    #Enviar a pantalla de confirmación
    context = {
        'msg' : msg,
    }
    return HttpResponse(template.render(context, request))

def resources_details(request):
    template = loader.get_template('resources_details.html')

    resources =[]
    #Obtener el estado de los recursos y el nodo el que se están ejecutando
    out = subprocess.check_output(["crm", "resource", "show"])
    info = out.decode('ascii')
    if "NO resources configured" not in info:
        result = info.split("\n")
        for item in result:
            if item != "":
                lista = item.split("\t")
                out = subprocess.check_output(["crm", "resource", "show", lista[0][1:]])
                print(out)
                out = out.decode('ascii')
                print(out)
                #Si un recurso esta parado se considera que no esta alojado en ningun nodo
                if out == "":
                    node = "XXXXX"
                else:
                   node = out.split(":")[1].strip()
                resources.append({"nombre": lista[0], "str": lista[1][:-1], "status": lista[2], "node": node})
        # Enviar la informacion a la plantilla
        context = {
            'resources': resources,
        }
    else:
        # Enviar la informacion a la plantilla
        context = {
        }


    return HttpResponse(template.render(context, request))

def resources_stop(request, resource_name):
    subprocess.run(["crm", "resource", "stop", resource_name[1:]], stdout=subprocess.PIPE)
    return redirect('cluster:resources')

def resources_start(request, resource_name):
    subprocess.run(["crm", "resource", "start", resource_name[1:]], stdout=subprocess.PIPE)
    return redirect('cluster:resources')

def resources_delete(request, resource_name):
    subprocess.run(["crm", "configure", "delete", resource_name[1:]], stdout=subprocess.PIPE)
    return redirect('cluster:resources')

def resources_migration(request, resource_name, node_name):
    subprocess.run(["crm", "resource", "unmigrate", resource_name[1:]], stdout=subprocess.PIPE)
    subprocess.run(["crm", "resource", "migrate", resource_name[1:], node_name], stdout=subprocess.PIPE)
    return redirect('cluster:resources')


def resources_migrate(request, resource_name):
    template = loader.get_template('resources_migrate.html')

    out = subprocess.check_output(["crm", "resource", "show", resource_name[1:]])
    info = out.decode('ascii')
    info = info.split(":")[1].strip()

    nodes = []
    out = subprocess.run(["crm", "node", "status"], stdout=subprocess.PIPE)
    out = ET.fromstring(out.stdout.decode('utf-8'))

    for node in out:
        status = "online"
        maintenance = False
        for instance_attributes in node:
            for nvpair in instance_attributes:
                if nvpair.get('name') == "standby" and nvpair.get('value') == "on":
                    status = "standby"
                if nvpair.get('name') == "maintenance" and nvpair.get('value') == "on":
                    maintenance = True
        if status == "online":
            nodes.append(node.get('uname'))

    context = {
        'resource': resource_name,
        'msg': info,
        'nodes': nodes,
    }
    return HttpResponse(template.render(context, request))


##### AGENTS

def agents(request):
    template = loader.get_template('agents.html')

    agents = Agent.objects.all()
    params = Agent_Param.objects.all()

    #Si no detecta ningún agente en la base de datos, carga todos los agentes de los .json a la base de datos
    if not agents:
        agents, params = ra_json_refresh()


    context = {
        'agents': agents,
        'agent_params': params
    }
    return HttpResponse(template.render(context, request))

def agents_refresh(request):
    template = loader.get_template('agents.html')

    agents, params = ra_json_refresh()

    context = {
        'agents': agents,
        'agent_params': params
    }
    return redirect('cluster:agents')

def agent_details(request, agent_name):
    template = loader.get_template('agent_details.html')

    agent = Agent.objects.get(name=agent_name)
    params = Agent_Param.objects.all().filter(agent__name= agent_name)

    context = {
        'agent': agent,
        'params': params,
    }
    return HttpResponse(template.render(context, request))

def ra_json_refresh():
    agents_db = Agent.objects.all()

    files = []
    for r, d, f in os.walk('cluster/json'):
        for file in f:
            if '.json' in file:
                files.append(os.path.join(r, file))

    # Por cada archivo json, lo abriremos y crearemos la entidad en la base de datos
    # Eliminamos la primera linea, que viene con la ruta del ocf
    for file in files:
        with open(file, "r") as f:
            str = f.read().split("\n", 1)[1]
            agent = json.loads(str)

            #Comprobamos que no esté ya en la DB
            new = True
            for agent_db in agents_db:
                if agent_db.name == agent["name"]:
                    new = False
                    break

            #Si es nuevo, se introduce
            if new:
                a = Agent(name=agent["name"], resource_str=agent["resource"], title=agent["title"],
                          description=agent["description"])
                a.save()
                for param in agent["params"]:
                    p = Agent_Param(agent=a, name=param["name"], title=param["title"], description=param["descripion"],
                                    required=param["required"], unique=param["unique"], content_type=param["content_type"],
                                    default_value=param["default_value"])
                    p.save()

    agents = Agent.objects.all()
    params = Agent_Param.objects.all()

    return agents, params