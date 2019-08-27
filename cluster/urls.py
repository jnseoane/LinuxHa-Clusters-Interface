from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('nodes', views.nodes, name='nodes'),
    path('resources', views.resources, name='resources'),
    path('nodes/<int:node_id>/resources', views.node_resources, name='node-resources'),
    path('agents', views.agents, name='agents'),
]