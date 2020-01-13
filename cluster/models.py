from django.db import models

# Create your models here.

class Agent(models.Model):
    name = models.CharField(max_length=30)
    resource_str = models.CharField(max_length=200)
    title = models.CharField(max_length=100, default="title")
    description = models.TextField(default="description")


class Agent_Param(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    title = models.CharField(max_length=200, default="title")
    description = models.TextField(default="description")
    required = models.BooleanField(default=False)
    unique = models.BooleanField(default=False)
    content_type = models.CharField(max_length=50, default="content-type")
    default_value = models.CharField(max_length=150, default="default", null=True)

