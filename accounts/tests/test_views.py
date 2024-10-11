from django.test import TestCase, Client, RequestFactory
from accounts.models import User
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser
from accounts.forms import UserRegistrationForm, VerifyCodeForm, UserLoginForm
from accounts.models import OtpCode, User


class TestRegisterView(TestCase):
    def setUp(self):
        self.client = Client()

    def test_user_register_GET(self):
        response = self.client.get(reverse('accounts:user_register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')
        self.failUnless(response.context['form'], UserRegistrationForm)

    def test_user_register_POST_valid(self):
        data = {'full_name': 'ali hashemi', 'email': 'ali@email.com', 'phone': '09931234567', 'password': 'ali'}
        response = self.client.post(reverse('accounts:user_register'), data=data)
        session = response.session
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:verify_code'))
        self.assertEqual(session['user_registration_info'], {
            'phone_number': '09931234567',
            'email': 'ali@email.com',
            'full_name': 'ali hashemi',
            'password': 'ali',
        })

    def test_user_register_POST_invalid(self):
        data = {'full_name': 'ali hashemi', 'email': 'invalid_email', 'phone': '09931234567', 'password': 'ali'}
        response = self.client.post(reverse('accounts:user_register'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')
        self.failIf(response.context['form'].is_valid())
        self.assertFormError(form=response.context['form'], field='email', errors=['Enter a valid email address.'])


class TestRegisterVerifyCodeView(TestCase):
    def setUp(self):
        self.client = Client()

    def test_user_verify_code_GET(self):
        response = self.client.get(reverse('accounts:verify_code'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/verify.html')
        self.failUnless(response.context['form'], VerifyCodeForm)

    def test_user_verify_code_POST_valid(self):
        data = {'full_name': 'ali hashemi', 'email': 'ali@email.com', 'phone': '09931234567', 'password': 'ali'}
        response1 = self.client.post(reverse('accounts:user_register'), data=data)
        session = response1.session
        instance = OtpCode.objects.get(phone_number=session['user_registration_info']['phone_number'])
        response = self.client.post(reverse('accounts:verify_code'), data={'code': instance.code})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home:home'))

    def test_user_verify_code_POST_invalid(self):
        response = self.client.post(reverse('accounts:user_register'), data={'code': 'hello'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/verify.html')
        self.failIf(response.context['form'].is_valid())


class TestLoginView(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(phone_number='09931234567', full_name='ali hash', email='ali@email.com',
                                 password='ali')

    def setUp(self):
        self.client = Client()

    def test_user_login_GET(self):
        response = self.client.get(reverse('accounts:user_login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
        self.failUnless(response.context['form'], UserLoginForm)

    def test_user_login_POST_valid(self):
        data = {'phone': '09931234567', 'password': 'ali'}
        response = self.client.post(reverse('accounts:user_login'), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home:home'))

    def test_user_login_POST_invalid(self):
        data = {'phone': '09937654321', 'password': 'ali'}
        response = self.client.post(reverse('accounts:user_login'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')


class TestLogoutView(TestCase):
    def setUp(self):
        User.objects.create_user(phone_number='09931234567', full_name='ali hash', email='ali@email.com',
                                 password='ali')
        self.client = Client()
        self.client.login(phone_number='09931234567', password='ali')

    def test_user_logout_GET(self):
        response = self.client.get(reverse('accounts:user_logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home:home'))

