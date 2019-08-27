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
    route = models.CharField(max_length=200)


class Agent_Param(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=100)

    def __str__(self):
        return self.name + ": " + self.value