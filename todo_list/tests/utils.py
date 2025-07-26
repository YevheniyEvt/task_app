from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

from todo_list.models import Project, Task



def create_user(number: int) ->User:
    """Create user for test. Number is just for creating unique one"""

    user: User = get_user_model()
    return user.objects.create_user(
            email=f'test{number}@mail.com',
            password='1234',
            username=f'test{number}',
            )

def create_project(number: int, user: User) ->Project:
    """Create project for test. Number is just for creating unique one"""

    return Project.objects.create(owner=user, name=f'Test project1{number}')

def create_task(number: int, project: Project) ->Task:
    """Create task for test. Number is just for creating unique one"""

    return Task.objects.create(
        project=project,
        content=f"Test task number {number}"
    )