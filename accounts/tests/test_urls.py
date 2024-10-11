from django.test import SimpleTestCase
from accounts.views import UserRegisterView, UserRegisterVerifyCodeView, UserLogoutView, UserLoginView
from django.urls import reverse, resolve


class TestUrls(SimpleTestCase):
    def test_user_register(self):
        url = reverse('accounts:user_register')
        self.assertEqual(resolve(url).func.view_class, UserRegisterView)

    def test_user_register_verify_code(self):
        url = reverse('accounts:verify_code')
        self.assertEqual(resolve(url).func.view_class, UserRegisterVerifyCodeView)

    def test_user_login(self):
        url = reverse('accounts:user_login')
        self.assertEqual(resolve(url).func.view_class, UserLoginView)

    def test_user_logout(self):
        url = reverse('accounts:user_logout')
        self.assertEqual(resolve(url).func.view_class, UserLogoutView)
