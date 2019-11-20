from django.urls import path

from . import views

app_name = 'cluster'
urlpatterns = [
    path('', views.index, name='index'),
    path('nodes', views.nodes, name='nodes'),
    path('nodes/<node_name>/online', views.nodes_online, name='nodes_online'),
    path('nodes/<node_name>/standby', views.nodes_standby, name='nodes_standby'),
    path('nodes/<node_name>/maintenance', views.nodes_maintenance, name='nodes_maintenance'),
    path('nodes/<node_name>/ready', views.nodes_ready, name='nodes_ready'),
    path('resources', views.resources, name='resources'),
    path('resources/new', views.resources_new, name='resources_new'),
    path('resources/new/<agent_name>', views.resources_form, name='resources_form'),
    path('resources/new/<agent_name>/created', views.resources_created, name='resources_created'),
    path('resources/details', views.resources_details, name='resources_details'),
    path('agents', views.agents, name='agents'),
    path('agents/<agent_name>/details', views.agent_details, name='agent_details'),
    path('refresh', views.agents_refresh, name='refresh'),

]