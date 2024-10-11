from django.test import TestCase
from accounts.forms import UserCreationForm, UserChangeForm, UserRegistrationForm
from accounts.models import User


class TestCreateUser(TestCase):
    def test_valid_data(self):
        form = UserCreationForm(
            data={'full_name': 'ali hashemi', 'email': 'ali@email.com', 'phone_number': '09931234567',
                  'password1': 'ali', 'password2': 'ali'})
        self.assertTrue(form.is_valid())

    def test_empty_data(self):
        form = UserCreationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 5)

    def test_unmatched_password(self):
        form = UserCreationForm(
            data={'full_name': 'ali hashemi', 'email': 'ali@email.com', 'phone_number': '09931234567',
                  'password1': 'ali', 'password2': 'alii'})
        self.assertTrue(form.has_error('password2'))
        self.assertEqual(len(form.errors), 1)


class TestRegistrationUser(TestCase):

    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(full_name='ali hashemi', email='ali@email.com', phone_number='09931234567',
                                 password='ali')

    def test_valid_data(self):
        form = UserRegistrationForm(
            data={'full_name': 'ali hashemi', 'email': 'ali@email.com', 'phone_number': '09931234567',
                  'password': 'ali'})
        self.assertTrue(form.is_valid())

    def test_empty_data(self):
        form = UserRegistrationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 4)

    def test_exist_email(self):
        form = UserRegistrationForm(
            data={'full_name': 'not ali hashemi', 'email': 'ali@email.com', 'phone_number': '09937654321',
                  'password': 'not ali'})
        self.assertEqual(len(form.errors), 1)
        self.assertTrue(form.has_error('email'))

    def test_exist_phone(self):
        form = UserRegistrationForm(
            data={'full_name': 'not ali hashemi', 'email': 'notali@email.com', 'phone_number': '09931234567',
                  'password': 'not ali'})
        self.assertEqual(len(form.errors), 1)
        self.assertTrue(form.has_error('phone'))
