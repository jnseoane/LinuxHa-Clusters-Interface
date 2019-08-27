from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
import subprocess
import xml.etree.ElementTree as ET
# Create your views here.

def index(request):
    template = loader.get_template('index.html')
    context = {}
    return HttpResponse(template.render(context,request))

def nodes(request):
    template = loader.get_template('nodes.html')
    #Conseguimos la información de los nodos para enviarla a la vista
    #En nodes se almacena la información de los nodos de esta forma:
    #nodes = [{'id': '2130706433', 'name': 'base'}, {'id': '3232249967', 'name': 'servidor1'}]


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

    return HttpResponse(template.render(context,request))

def resources(request):
    return HttpResponse("Resources")

def node_resources(request, node_id):
    return HttpResponse("Resources of node: %s" % node_id)


def agents(request):
    return HttpResponse("Agents")