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
        user2 = create_user(2)
        cls.project = create_project(1, cls.user)
        cls.project2 = create_project(1, user2)
        cls.headers = [{"HX-Request": 'true'}, {}]

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
    
    def test_create_task_user_not_owner_project(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('projects:task_create',
                    kwargs={"project_id": self.project2.id},
                    ),
            data={"content": "test text"},
            )
        self.assertEqual(response.status_code, 404)

    def test_create_task_login_and_owner(self):
        self.client.force_login(self.user)
        for i, header in enumerate(self.headers):
            content = f"{i} text create"
            with self.subTest(header=header, content=content):
                response = self.client.post(
                    reverse('projects:task_create',
                            kwargs={"project_id": self.project.id},
                            ),
                    data={"content": content},
                    headers=header,
                    )
                self.assertIsNotNone(Task.objects.filter(content=content).first())
                if header:
                    self.assertEqual(response.status_code, 200)
                    self.assertTemplateUsed(response, "partials/new_task.html")
                else:
                    self.assertRedirects(
                        response,
                        reverse('projects:projects_list'),
                        target_status_code=200,
                        )

    def test_get_create_task(self):
        self.client.force_login(self.user)
        for header in self.headers:
            with self.subTest(header=header):
                response = self.client.get(
                    reverse('projects:task_create',
                            kwargs={"project_id": self.project.id},
                            ),
                    headers=header,
                    ) 
                if header:      
                    self.assertTemplateUsed(response, "partials/full_task_form.html")
                else:
                    self.assertRedirects(
                        response,
                        reverse('projects:projects_list'),
                        target_status_code=200,
                        )
                    

class TaskUpdateViewTestCase(TestCase):
    """Test update task"""
    
    @classmethod
    def setUpTestData(cls):
        cls.user = create_user(1)
        cls.project = create_project(1, cls.user)
        cls.task = create_task(1, cls.project)
        user2 = create_user(2)
        project2 = create_project(2, user2)
        cls.task2 = create_task(2, project2)
        cls.headers = [{"HX-Request": 'true'}, {}]

    def test_update_task_not_login_user(self):
        response = self.client.post(
            reverse('projects:task_update',
                    kwargs={"pk": self.task.id}
                    ),
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
        response = self.client.post(
            reverse('projects:task_update',
                    kwargs={"pk": self.task2.id}
                    ),
            data={"content": "updated text"},
            )
        self.assertEqual(response.status_code, 404)
        self.assertIsNotNone(Task.objects.filter(content=self.task2.content).first())
        self.assertIsNone(Task.objects.filter(content='updated text').first())

    def test_update_task_owner_user(self):
        self.client.force_login(self.user)
        for i, header in enumerate(self.headers):
            task = create_task(i, self.project)
            with self.subTest(header=header, task=task):
                content = f"updated text #{i}"
                response = self.client.post(
                    reverse('projects:task_update',
                            kwargs={"pk": task.id}
                            ),
                    data={"content": content,
                          "deadline": task.deadline},
                    headers=header,
                    )
                self.assertEqual(Task.objects.get(id=task.id).content, content)
                if header:
                    self.assertEqual(response.status_code, 200)
                    self.assertTemplateUsed(response, 'todo_list/task_list.html')
                else:
                    self.assertEqual(response.status_code, 302)
                    self.assertRedirects(
                        response,
                        reverse('projects:projects_list'),
                        target_status_code=200,
                        )
                
    def test_get_update_task_owner_user(self):
        self.client.force_login(self.user)
        for header in self.headers:
            with self.subTest(header=header):
                response = self.client.get(
                    reverse('projects:task_update',
                            kwargs={"pk": self.task.id},
                            ),
                    headers=header,
                    ) 
                if header:
                    self.assertEqual(response.status_code, 200)      
                    self.assertTemplateUsed(response, 'partials/task_update_form.html')
                else:
                    self.assertEqual(response.status_code, 302)
                    self.assertRedirects(
                        response,
                        reverse('projects:projects_list'),
                        target_status_code=200,
                        )

class TaskCompletedUpdateViewTestCase(TestCase):
    """Test update complete task"""
        
    @classmethod
    def setUpTestData(cls):
        cls.user = create_user(1)
        project = create_project(1, cls.user)
        cls.task = create_task(1, project)
        user2 = create_user(2)
        project2 = create_project(2, user2)
        cls.task2 = create_task(2, project2)
        cls.headers = [{"HX-Request": 'true'}, {}]

    def test_update_task_not_login_user(self):
        response = self.client.post(
            reverse('projects:task_completed',
                    kwargs={"pk": self.task.id}
                    ),
            data={"completed": True},
            )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f'{reverse('account_login')}?next=/projects/task/completed/{self.task.id}/',
            target_status_code=200,
            )
    
    def test_update_task_not_owner_user(self):
        self.client.force_login(self.user)
        for header in self.headers:
            with self.subTest(header=header):
                response = self.client.post(
                    reverse('projects:task_completed',
                            kwargs={"pk": self.task2.id}),
                    data={"completed": True},
                    headers=header,
                    )
                self.assertEqual(response.status_code, 404)
                self.assertFalse(self.task2.completed)

    def test_update_task_owner_user(self):
        self.client.force_login(self.user)
        for header in self.headers:
            with self.subTest(header=header):
                response = self.client.post(
                    reverse('projects:task_completed',
                            kwargs={"pk": self.task.id}),
                    data={"completed": True},
                    headers=header,
                    )
                self.task.refresh_from_db()
                if header:
                    self.assertTrue(self.task.completed)
                else:
                    self.assertEqual(response.status_code, 405)
                


class TaskPriorityUpdateViewTestCase(TestCase):
    """Test update priority task"""
        
    @classmethod
    def setUpTestData(cls):
        cls.user = create_user(1)
        project = create_project(1, cls.user)
        cls.task = create_task(1, project)
        user2 = create_user(2)
        project2 = create_project(2, user2)
        cls.task2 = create_task(2, project2)
        cls.headers = [{"HX-Request": 'true'}, {}]

    def test_update_task_not_login_user(self):
        response = self.client.post(
            reverse('projects:task_priority',
                    kwargs={"pk": self.task.id}),
            data={"priority": 1},
            )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f'{reverse('account_login')}?next=/projects/task/priority/{self.task.id}/',
            target_status_code=200,
            )
    
    def test_update_task_not_owner_user(self):
        self.client.force_login(self.user)
        for header in self.headers:
            with self.subTest(header=header):
                response = self.client.post(
                    reverse('projects:task_priority',
                            kwargs={"pk": self.task2.id}),
                    data={"priority": 1},
                    headers=header,
                    )
                self.assertEqual(response.status_code, 404)
                self.assertEqual(self.task2.priority, 0)

    def test_update_task_owner_user(self):
        self.client.force_login(self.user)
        for header in self.headers:
            with self.subTest(header=header):
                response = self.client.post(
                    reverse('projects:task_priority',
                            kwargs={"pk": self.task.id}),
                    data={"priority": 1},
                    headers=header
                    )
                self.task.refresh_from_db()
                if header:
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(self.task.priority, 1)
                    self.assertTemplateUsed(response, 'todo_list/project.html')
                else:
                    self.assertEqual(response.status_code, 405)


class ProjectDeleteViewTestCase(TestCase):
    """Test delete task"""

    @classmethod
    def setUpTestData(cls):
        cls.user = create_user(1)
        cls.project = create_project(1, cls.user)
        cls.task = create_task(1, cls.project)
        user2 = create_user(2)
        project2 = create_project(2, user2)
        cls.task2 = create_task(2, project2)
        cls.headers = [{"HX-Request": 'true'}, {}]

    def test_delete_task_not_login_user(self):
        response = self.client.post(
            reverse('projects:task_delete',
                    kwargs={"pk": self.task.id},
                    ),
            )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f'{reverse('account_login')}?next=/projects/task/delete/{self.task.id}/',
            target_status_code=200,
            )
    
    def test_delete_task_not_owner_user(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('projects:task_delete',
                    kwargs={"pk": self.task2.id},
                    ),
            )
        self.assertEqual(response.status_code, 404)
        self.assertIsNotNone(Task.objects.filter(content=self.task2.content).first())

    def test_delete_task_owner_user(self):
        self.client.force_login(self.user)
        for i, header in enumerate(self.headers):
            task = create_task(i, self.project)
            with self.subTest(header=header, task=task):
                response = self.client.post(
                    reverse('projects:task_delete',
                            kwargs={"pk": task.id},
                            ),
                    headers=header,
                    )
                self.assertIsNone(Task.objects.filter(id=task.id).first())
                if header:
                    self.assertEqual(response.status_code, 200)
                else:
                    self.assertRedirects(
                        response,
                        reverse('projects:projects_list'),
                        target_status_code=200,
                        )
