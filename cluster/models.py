from django.db import models

# Create your models here.
class Node(models.Model):
    id = models.CharField(max_length=40, primary_key=True)
    ip = models.CharField(max_length = 20)
    name = models.CharField(max_length = 30)

    def __str__(self):
        return self.name + "(" + self.ip + ")"

class Resource(models.Model):
    dependencies = models.ManyToManyField("self")
    node = models.ForeignKey(Node, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length = 30)
    def __str__(self):
        return self.name + "running on: " + self.node.__str__() + "\nDependencies:\n\t" + self.dependencies.__str__()


class Resource_Param(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    value = models.CharField(max_length=30)

    def __str__(self):
        return self.name + ": " + self.value


class Agent(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.SET_NULL, blank=True, null=True)
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

