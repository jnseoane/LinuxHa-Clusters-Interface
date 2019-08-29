from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('nodes', views.nodes, name='nodes'),
    path('nodes/<node_name>/online', views.nodes_online, name='nodes_online'),
    path('nodes/<node_name>/standby', views.nodes_standby, name='nodes_standby'),
    path('nodes/<node_name>/maintenance', views.nodes_maintenance, name='nodes_maintenance'),
    path('nodes/<node_name>/ready', views.nodes_ready, name='nodes_ready'),
    path('resources', views.resources, name='resources'),
    path('nodes/<int:node_id>/resources', views.node_resources, name='node-resources'),
    path('agents', views.agents, name='agents'),
    path('agents/<agent_name>/details', views.agent_details, name='agent_details'),
    path('refresh', views.agents_refresh, name='refresh'),
]