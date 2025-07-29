from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from todo_list.tests.utils import create_user


class LoginTestCase(TestCase):
    """Test login"""

    @classmethod
    def setUpTestData(cls):
        cls.user = create_user(1)
        
    def test_login(self):
        response = self.client.get(reverse('account_login'), headers={"HX-Request": 'true'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/login.html')

    def test_login_success(self):
        response = self.client.post(
            reverse('account_login'),
            data={'email': self.user.email,
                  'password': '1234'},
            headers={"HX-Request": 'true'}
            )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/login.html')


class LogoutTestCase(TestCase):
    """Test logout"""

    @classmethod
    def setUpTestData(cls):
        cls.user = create_user(1)
        
    def test_logout_success(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('account_logout'),
            headers={"HX-Request": 'true'}
            )
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed(response, 'account/messages/logged_out.txt')


class RegisterTestCase(TestCase):
    """Test registration"""

    def test_registration_get(self):
        response = self.client.get(reverse('account_signup'), headers={"HX-Request": 'true'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/signup.html')

    def test_registration(self):
        response = self.client.post(
            reverse('account_signup'),
            headers={"HX-Request": 'true'},
            data={"email": 'test@mail.com',
                  "password1": 'Qwer12345679',
                  "password2": 'Qwer12345679',
                  }
            )
        user_exists = User.objects.filter(email='test@mail.com').exists()
        self.assertTrue(user_exists)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed(response, 'account/messages/logged_in.txt')


class ChangePasswordTestCase(TestCase):
    """Test change password"""

    @classmethod
    def setUpTestData(cls):
        cls.user = create_user(1)

    def test_password_change_get(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('account_change_password'), headers={"HX-Request": 'true'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/password_change.html')

    def test_password_change(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('account_change_password'),
            headers={"HX-Request": 'true'},
            data={"oldpassword": 'Qwer12345679Qwer',
                  "password1": 'Qwer12345679',
                  "password2": 'Qwer12345679',
                  }
            )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/password_change.html')

