from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


# une class c'est comme une table pour model.py
def validate_status(value):
    if value not in ["À faire", "En cours", "Fait"]:
        raise ValidationError("Statut invalide : choisir 'À faire', 'En cours' ou 'Fait'.")
    
class Project(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self): return self.name


class Task(models.Model):
    # existants
    STATUS = (("À faire","À faire"), ("En cours","En cours"),("Fait","Fait"))
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS,default="À faire")
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="tasks")
    # nouveaux
    TASK_TYPES = (("epic","Epic"), ("story","User story"),("feature","Feature"),("task","Tâche"), ("subtask","Sous-tâche"))
    PRIORITY = (("low","Basse"), ("medium","Moyenne"),("high","Haute"), ("urgent","Urgente"))
    task_type = models.CharField(max_length=20, choices=TASK_TYPES,default="task")
    priority = models.CharField(max_length=10, choices=PRIORITY,default="medium")
    project = models.ForeignKey(Project, null=True, blank=True, on_delete=models.SET_NULL, related_name="tasks")
    target_version = models.CharField(max_length=40, blank=True)
    module = models.CharField(max_length=80, blank=True)
    reporter = models.ForeignKey(User, null=True, blank=True,on_delete=models.SET_NULL, related_name="reported_tasks")
    # hiérarchie infinie
    parent = models.ForeignKey("self", null=True, blank=True,on_delete=models.CASCADE, related_name="children")
    # planning / gantt
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    progress = models.PositiveIntegerField(default=0) # 0..100
    description = models.TextField(blank=True)

    def clean(self):
    # anti-cycle (simple) : on interdit de faire d’un nœud son propre ancêtre
        node = self.parent
        while node is not None:
            if node == self:
                raise ValueError("Boucle hiérarchique interdite cycle détecté).")
            node = node.parent
   
    def __str__(self): 
        return f"[{self.task_type}] {self.title}"

class TaskLink(models.Model):
    LINK_TYPES = (("blocks","bloquant"),("depends","dépend de"),("relates","relatif à"))
    src = models.ForeignKey(Task, on_delete=models.CASCADE,related_name="out_links")
    dst = models.ForeignKey(Task, on_delete=models.CASCADE,related_name="in_links")
    link_type = models.CharField(max_length=10, choices=LINK_TYPES)
            
class Meta:
    constraints = [
        models.UniqueConstraint(fields=["src","dst","link_type"],name="unique_task_link")
    ]
    
    def clean(self):
        if self.src_id == self.dst_id:
            raise ValueError("Lien vers soi-même interdit.")

class Attachment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE,related_name="attachments")
    image = models.ImageField(upload_to="attachments/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
