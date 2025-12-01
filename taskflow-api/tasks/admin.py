from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'created_at', 'owner')
    search_fields = ('title', 'status', 'owner__username')

# Personnalisation de l’en-tête et des titres du site d'administration
admin.site.site_header = "TaskFlow – Administration"
admin.site.site_title = "TaskFlow Admin"
