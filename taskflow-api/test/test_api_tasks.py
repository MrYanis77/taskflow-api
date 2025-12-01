import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from tasks.models import Task

@pytest.mark.django_db
def test_get_tasks_empty():
    client = APIClient()
    resp = client.get('/api/tasks/')
    assert resp.status_code == 200
    assert resp.json() == []

@pytest.mark.django_db
def test_create_task_anonymous_owner_optional():
    client = APIClient()
    resp = client.post('/api/tasks/', {'title': 'T1', 'status': 'À faire'}, format='json')
    assert resp.status_code == 201
    data = resp.json()
    assert data['title'] == 'T1'

@pytest.mark.django_db
def test_create_task_with_user_sets_owner():
    user = User.objects.create_user(username='alice', password='pwd123')
    client = APIClient()
    client.force_authenticate(user=user)
    resp = client.post('/api/tasks/', {'title': 'T2', 'status': 'En cours'}, format='json')
    assert resp.status_code == 201
    t = Task.objects.get(title='T2')
    assert t.owner == user