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

def nodes(request):
    template = loader.get_template('nodes.html')
    #Conseguimos la información de los nodos para enviarla a la vista
    #En nodes se almacena la información de los nodos de esta forma:
    #nodes = [{'id': '2130706433', 'name': 'base', 'status': 'online', 'maintenance': False}, {'id': '3232249967', 'name': 'servidor1', 'status': 'online', 'maintenance': False}]


    #Comandos para poner en mantenimiento y en standby para futuro
        # Standby subprocess.run(["crm", "node", "attribute", "servidorX", "set", "standby", "on"], stdout=subprocess.PIPE)
        # Maintenance subprocess.run(["crm", "node", "attribute", "servidorX", "set", "maintenance", "on"], stdout=subprocess.PIPE)

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
    return redirect('nodes')

def nodes_standby(request, node_name):
    subprocess.run(["crm", "node", "standby", node_name], stdout=subprocess.PIPE)
    return redirect('nodes')

def nodes_maintenance(request, node_name):
    subprocess.run(["crm", "node", "maintenance", node_name], stdout=subprocess.PIPE)
    return redirect('nodes')

def nodes_ready(request, node_name):
    subprocess.run(["crm", "node", "ready", node_name], stdout=subprocess.PIPE)
    return redirect('nodes')

def resources(request):
    context = {}
    return render(request, 'resources.html', context)

def node_resources(request, node_id):
    return HttpResponse("Resources of node: %s" % node_id)


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
    return redirect('agents')
    #return HttpResponse(template.render(context, request))


def agent_details(request, agent_name):
    return redirect('agents')

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