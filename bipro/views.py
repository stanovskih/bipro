
from datetime import datetime
from django.http import HttpResponse
from django.http import JsonResponse, FileResponse
from django.shortcuts import render, redirect
#from telegram import User
from django.contrib.auth.models import User
import json
from django.views.decorators.csrf import csrf_exempt
import base64
import uuid
import logging
from django.db import connection
from django.http import HttpResponseRedirect
from django.contrib.auth import login as auth_login, authenticate
from django.urls import reverse
from django.views import View
from django.contrib.auth.decorators import login_required
import os
from django.contrib.auth import login as auth_login, authenticate, logout as logout_user
from .forms import ExtendedRegisterForm
from django.contrib import messages

def index(request):
    return render(request, 'index2.html')



def logout(request):
    logout_user(request)
    return redirect('login')

def login(request):
    error_message = ""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        u = User.objects.filter(username=username)
        if u and not u[0].is_active:
            error_message = 'Учетная запись не активированна! Обратитесь к Администратору.'
            return render(request, 'lklogin.html', {'error': error_message})
        
        user = authenticate(username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('order_list')
        else:
            error_message = 'Неверный логин или пароль!'
            # No backend authenticated the credentials
        
    return render(request, 'login.html', {'error': error_message})

def signup(request):
    if request.method == 'POST':
        form = ExtendedRegisterForm(request.POST)
        if form.is_valid():
            # Создаем объект пользователя, но не сохраняем в БД
            user = form.save(commit=False)
            # Делаем пользователя неактивным
            user.is_active = False
            # Сохраняем пользователя в базу данных
            user.save()
            
            messages.success(request, 'Регистрация успешна! Ваш аккаунт ожидает активации.')
            return redirect('signup_successfully')
    else:
        form = ExtendedRegisterForm()    
    return render(request, 'signup.html', {'form': form})

def signup_successfully(request):

    return render(request, 'signup_successfully.html')
