from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, filters
from rest_framework.exceptions import APIException
from django_filters.rest_framework import DjangoFilterBackend
from .models import Task, TaskLink, Attachment, Project
from .serializers import TaskSerializer, TaskLinkSerializer, AttachmentSerializer, ProjectSerializer

class BusinessRuleException(APIException):
    status_code = 400
    default_detail = "Règle métier non respectée."

class TaskViewSet(ModelViewSet):
    # Filtres / recherche / tri
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['title', 'status']
    ordering_fields = ['created_at', 'title']
    filterset_fields = ['status']

    queryset = Task.objects.all().order_by('-id')
    serializer_class = TaskSerializer

    # AJOUT ICI : méthode d’instance dans la classe
    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(owner=user)

    # ... queryset, serializer_class, filters, etc.
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status == "En cours":
            raise BusinessRuleException("Impossible de supprimer une tâche 'En cours'.")
        return super().destroy(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({"message": "Tâche créée", "data":serializer.data}, status=status.HTTP_201_CREATED)

    # enfants directs
    @action(detail=True, methods=["get"])
    def children(self, request, pk=None):
        qs = Task.objects.filter(parent_id=pk)
        return Response(TaskSerializer(qs, many=True).data)
    
    # kanban : groupé par statut
    @action(detail=False, methods=["get"])
    def kanban(self, request):
        board = {}
        for st in ["À faire", "En cours", "Fait"]:
            board[st] = TaskSerializer(Task.objects.filter(status=st), many=True).data
        return Response(board)

    # gantt : multi-projet (données brutes)
    @action(detail=False, methods=["get"])
    def gantt(self, request):
        payload = {}
        for p in Project.objects.all():
            items = Task.objects.filter(project=p).only("id","title","start_date","due_date","progress")
            payload[p.name] = [
                {"id": t.id, "text": t.title, "start": t.start_date, "end": t.due_date, "progress": t.progress}
                for t in items
            ]
        return Response(payload)

    # créer un lien entre tâches
    @action(detail=True, methods=["post"])
    def link(self, request, pk=None):
        data = {"src": pk, "dst": request.data.get("dst"), "link_type": request.data.get("link_type")}
        ser = TaskLinkSerializer(data=data)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data, status=201)

    # upload d'image (screenshot)
    @action(detail=True, methods=["post"])
    def upload(self, request, pk=None):
        file_obj = request.FILES.get("image")
        if not file_obj:
            return Response({"error": "paramètre 'image' requis (multipart/form-data)"}, status=400)
        att = Attachment.objects.create(task_id=pk, image=file_obj)
        return Response(AttachmentSerializer(att).data, status=201)

class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer