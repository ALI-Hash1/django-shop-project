from django.test import TestCase
from accounts.models import User


class TestUserModel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(full_name='ali', email='ali@email.com', phone_number='09931234567',
                                             password='ali')

    def test_model_str(self):
        self.assertEqual(str(self.user), 'ali@email.com')

    def test_is_not_admin_user(self):
        self.assertFalse(self.user.is_staff)

    def test_is_admin_user(self):
        user = User.objects.create_user(full_name='ali', email='ali@email.com', phone_number='09931234567',
                                        password='ali', is_admin=True)
        self.assertTrue(user.is_staff)
