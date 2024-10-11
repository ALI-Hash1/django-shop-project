from django.shortcuts import render, redirect
from django.views import View
from .forms import UserRegistrationForm, VerifyCodeForm, UserLoginForm
import random
from utils import send_otp_code, IsNotAuthenticatedMixin
from .models import OtpCode, User
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
import datetime


class UserRegisterView(IsNotAuthenticatedMixin, View):
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            random_code = random.randint(1000, 9999)
            send_otp_code(cd['phone'], random_code)
            OtpCode.objects.create(phone_number=cd['phone'], code=random_code)
            request.session['user_registration_info'] = {
                'phone_number': cd['phone'],
                'email': cd['email'],
                'full_name': cd['full_name'],
                'password': cd['password'],
            }
            messages.success(request, 'we sent you a code', 'success')
            return redirect('accounts:verify_code')
        return render(request, self.template_name, {'form': form})


class UserRegisterVerifyCodeView(IsNotAuthenticatedMixin, View):
    form_class = VerifyCodeForm
    register_form = UserRegistrationForm

    def get(self, request):
        form = self.form_class()
        return render(request, 'accounts/verify.html', {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user_session = request.session['user_registration_info']
            code_instance = OtpCode.objects.get(phone_number=user_session['phone_number'])
            cd = form.cleaned_data
            if cd['code'] == code_instance.code:
                if datetime.datetime.now() <= code_instance.create + datetime.timedelta(minutes=2):
                    User.objects.create_user(phone_number=user_session['phone_number'], email=user_session['email'],
                                             full_name=user_session['full_name'], password=user_session['password'])
                    code_instance.delete()
                    messages.success(request, 'you registered.', 'success')
                    return redirect('home:home')
                else:
                    messages.error(request, 'the code has expired, please try again...')
                    return redirect('accounts:user_register')
            else:
                messages.error(request, 'this code is wrong', 'danger')
                return redirect('accounts:verify_code')
        return render(request, 'accounts/verify.html', {'form': form})


class UserLoginView(IsNotAuthenticatedMixin, View):
    form_class = UserLoginForm
    template_name = 'accounts/login.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, phone_number=cd['phone'], password=cd['password'])
            if user is not None:
                login(request, user)
                messages.success(request, 'you logged in successfully', 'success')
                return redirect('home:home')
            messages.error(request, 'phone or password is wrong', 'danger')
        return render(request, self.template_name, {'form': form})


class UserLogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        messages.success(request, 'you logged out successfully', 'success')
        return redirect('home:home')
