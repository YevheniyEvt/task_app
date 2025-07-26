from django.test import TestCase
from django.urls import reverse

from todo_list.models import Project, Task
from todo_list.tests.utils import create_user, create_project, create_task


class TaskListTestCase(TestCase):
    """Test list of tasks"""

    @classmethod
    def setUpTestData(cls):
        cls.user = create_user(1)
        project = create_project(1, cls.user)
        for i in range(3):
            create_task(i, project)
        cls.users_projects = Project.objects.filter(owner=cls.user)
        
    def test_task_context(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('projects:projects_list'))
        for project in self.users_projects:
            tasks = project.tasks.all()
            for task in tasks:
                with self.subTest(task=task):
                    self.assertContains(response, task.content)


class TaskCreateViewTestCase(TestCase):
    """Test create task"""

    @classmethod
    def setUpTestData(cls):
        cls.user = create_user(1)
        cls.project = create_project(1, cls.user)

    def test_create_task_not_login_user(self):
        response = self.client.post(
            reverse('projects:task_create',
                    kwargs={"project_id": self.project.id},
                    ),
            data={"content": "test text"},
            )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f'{reverse('account_login')}?next=/projects/{self.project.id}/task/create/',
            target_status_code=200,
            )

    def test_create_task_login_user(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('projects:task_create',
                    kwargs={"project_id": self.project.id},
                    ),
            data={"content": "test text"},
            )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('projects:projects_list'), target_status_code=200)
        self.assertIsNotNone(Task.objects.filter(content='test text').first())


class TaskUpdateViewTestCase(TestCase):
    """Test update task"""
    
    @classmethod
    def setUpTestData(cls):
        cls.user = create_user(1)
        project = create_project(1, cls.user)
        cls.task = create_task(1, project)
        user2 = create_user(2)
        project2 = create_project(2, user2)
        cls.task2 = create_task(2, project2)

    def test_update_task_not_login_user(self):
        response = self.client.post(reverse('projects:task_update',
                                            kwargs={"pk": self.task.id}),
                                            data={"content": "updated text"},
                                            )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f'{reverse('account_login')}?next=/projects/task/update/{self.task.id}/',
            target_status_code=200,
            )
    
    def test_update_task_not_owner_user(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('projects:task_update',
                                            kwargs={"pk": self.task2.id}),
                                            data={"content": "updated text"},
                                            )
        self.assertEqual(response.status_code, 404)
        self.assertIsNotNone(Task.objects.filter(content=self.task2.content).first())
        self.assertIsNone(Task.objects.filter(content='updated text').first())

    def test_update_task_owner_user(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('projects:task_update',
                                            kwargs={"pk": self.task.id}),
                                            data={"content": "updated text"},
                                            )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('projects:projects_list'), target_status_code=200)
        self.assertIsNotNone(Task.objects.filter(content='updated text').first())
        self.assertIsNone(Task.objects.filter(content=self.task.content).first())


class ProjectDeleteViewTestCase(TestCase):
    """Test delete task"""

    @classmethod
    def setUpTestData(cls):
        cls.user = create_user(1)
        project = create_project(1, cls.user)
        cls.task = create_task(1, project)
        user2 = create_user(2)
        project2 = create_project(2, user2)
        cls.task2 = create_task(2, project2)

    def test_delete_task_not_login_user(self):
        response = self.client.post(reverse('projects:task_delete',kwargs={"pk": self.task.id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f'{reverse('account_login')}?next=/projects/task/delete/{self.task.id}/',
            target_status_code=200,
            )
    
    def test_delete_task_not_owner_user(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('projects:task_delete',kwargs={"pk": self.task2.id}))
        self.assertEqual(response.status_code, 404)
        self.assertIsNotNone(Task.objects.filter(content=self.task2.content).first())

    def test_delete_task_owner_user(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('projects:task_delete',kwargs={"pk": self.task.id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('projects:projects_list'), target_status_code=200)
        self.assertIsNone(Task.objects.filter(content=self.task.content).first())