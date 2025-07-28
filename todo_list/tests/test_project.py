from django.test import TestCase
from django.urls import reverse

from todo_list.models import Project
from todo_list.tests.utils import create_user, create_project


class ProjectListViewTestCase(TestCase):
    """Test list of projects"""

    @classmethod
    def setUpTestData(cls):
        cls.user = create_user(1)
        user2 = create_user(2)
        create_project(1, cls.user)
        create_project(2, user2)
        cls.users_projects = Project.objects.filter(owner=cls.user)
        
    def test_get_projects_not_login_user(self):
        response = self.client.get(reverse('projects:projects_list'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f'{reverse('account_login', )}?next=/projects/',
            target_status_code=200,
            )
        
    def test_get_projects(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('projects:projects_list'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context['projects'], self.users_projects)
        self.assertTemplateUsed(response, 'todo_list/project_list.html')
        self.assertTemplateUsed(response, 'base.html')
        self.assertTemplateUsed(response, 'navbar.html')
        self.assertTemplateUsed(response, 'todo_list/project_title.html')
        self.assertTemplateUsed(response, 'todo_list/task_form.html')
        

    def test_projects_context(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('projects:projects_list'))
        for project in self.users_projects:
            with self.subTest(project=project):
                self.assertContains(response, project.name)



class ProjectCreateViewTestCase(TestCase):
    """Test create project"""

    @classmethod
    def setUpTestData(cls):
        cls.user = create_user(1)
        cls.headers = [{"HX-Request": 'true'}, {}]

    def test_create_project_not_login_user(self):
        response = self.client.post(
            reverse('projects:projects_create'),
            data={"name": "test text"},
            )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f'{reverse('account_login')}?next=/projects/create/',
            target_status_code=200,
            )

    def test_create_project_login_user(self):
        self.client.force_login(self.user)
        for header in self.headers:
            with self.subTest(header=header):
                response = self.client.post(
                    reverse('projects:projects_create'),
                    data={"name": "test text"},
                    headers=header
                    )
                self.assertIsNotNone(Project.objects.filter(name='test text').first())
                if header:
                    self.assertEqual(response.status_code, 200)
                    self.assertTemplateUsed(response, 'todo_list/project.html')
                else:
                    self.assertRedirects(
                        response,
                        reverse('projects:projects_list'),
                        target_status_code=200,
                        )
        
    def test_get_create_project_login_user(self):
        self.client.force_login(self.user)
        for header in self.headers:
            with self.subTest(header=header):
                response = self.client.get(
                    reverse('projects:projects_create'),
                    headers=header,
                    ) 
                if header:      
                    self.assertTemplateUsed(response, "todo_list/partials/project_form.html")
                else:
                    self.assertRedirects(
                        response,
                        reverse('projects:projects_list'),
                        target_status_code=200,
                        )


class ProjectUpdateViewTestCase(TestCase):
    """Test update project"""
    
    @classmethod
    def setUpTestData(cls):
        cls.user = create_user(1)
        user2 = create_user(2)
        cls.project = create_project(1, cls.user)
        cls.project2 = create_project(2, user2)
        cls.headers = [{"HX-Request": 'true'}, {}]

    def test_update_project_not_login_user(self):
        response = self.client.post(
            reverse('projects:projects_update',
                    kwargs={"pk": self.project.id},
                    ),
            data={"name": "updated text"}
            )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f'{reverse('account_login')}?next=/projects/update/{self.project.id}/',
            target_status_code=200,
            )
    
    def test_update_project_not_owner_user(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('projects:projects_update',
                    kwargs={"pk": self.project2.id},
                    ),
            data={"name": "updated text"},
            )
        self.assertEqual(response.status_code, 404)
        self.assertIsNotNone(Project.objects.filter(name=self.project2.name).first())
        self.assertIsNone(Project.objects.filter(name='updated text').first())

    def test_update_project_owner_user(self):
        self.client.force_login(self.user)
        for i, header in enumerate(self.headers):
            
            project = create_project(i, self.user)
            with self.subTest(header=header, project=project):
                name = f"text #{i}"
                response = self.client.post(
                    reverse('projects:projects_update',
                            kwargs={"pk": project.id},
                            ),
                    data={"name": name},
                    headers=header,
                    )
                self.assertEqual(Project.objects.get(id=project.id).name, name)
                if header:
                    self.assertEqual(response.status_code, 200)
                    self.assertTemplateUsed(response, 'todo_list/project_title.html')
                else:
                    self.assertRedirects(
                        response,
                        reverse('projects:projects_list'),
                        target_status_code=200,
                        )


    def test_get_update_project_owner_user(self):
        self.client.force_login(self.user)
        for header in self.headers:
            with self.subTest(header=header):
                response = self.client.get(
                    reverse('projects:projects_update',
                            kwargs={"pk": self.project.id},
                            ),
                    headers=header,
                    ) 
                if header:      
                    self.assertTemplateUsed(response, 'todo_list/partials/project_update.html')
                else:
                    self.assertRedirects(
                        response,
                        reverse('projects:projects_list'),
                        target_status_code=200,
                        )


class ProjectDeleteViewTestCase(TestCase):
    """Test delete project"""

    @classmethod
    def setUpTestData(cls):
        cls.user = create_user(1)
        user2 = create_user(2)
        cls.project = create_project(1, cls.user)
        cls.project2 = create_project(2, user2)
        cls.headers = [{"HX-Request": 'true'}, {}]

    def test_delete_project_not_login_user(self):
        response = self.client.post(
            reverse('projects:projects_delete',
                    kwargs={"pk": self.project.id},
                    ),
            )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f'{reverse('account_login')}?next=/projects/delete/{self.project.id}/',
            target_status_code=200,
            )
    
    def test_delete_project_not_owner_user(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('projects:projects_delete',
                    kwargs={"pk": self.project2.id},
                    ),
            )
        self.assertEqual(response.status_code, 404)
        self.assertIsNotNone(Project.objects.filter(name=self.project2.name).first())

    def test_delete_project_owner_user(self):
        self.client.force_login(self.user)
        for i, header in enumerate(self.headers):
            project = create_project(i, self.user)
            with self.subTest(header=header, project=project):
                response = self.client.post(
                    reverse('projects:projects_delete',
                            kwargs={"pk": project.id},
                            ),
                    headers=header,
                    )
                self.assertIsNone(Project.objects.filter(id=project.id).first())
                if header:
                    self.assertEqual(response.status_code, 200)
                else:
                    self.assertRedirects(
                        response,
                        reverse('projects:projects_list'),
                        target_status_code=200,
                        )
                