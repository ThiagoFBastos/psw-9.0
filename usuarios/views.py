from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.messages import constants
from django.contrib import auth

# Create your views here.

@require_http_methods(['GET'])
def logout(request):
    auth.logout(request)
    return redirect(reverse('usuarios-login'))

@require_http_methods(['GET', 'POST'])
def logar(request): 
    if request.method == 'GET':
        return render(request, 'login.html', {})
    else:
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        user = auth.authenticate(request, username = username, password = senha)

        if user:
            auth.login(request, user)
            messages.add_message(request, constants.SUCCESS, 'Usuário logado')
            return redirect(reverse('flashcard-novo_flashcard'))
        else:
            messages.add_message(request, constants.ERROR, 'Usuário e/ou senha incorretos')
            return redirect(reverse('usuarios-login'))

@require_http_methods(['GET', 'POST'])
def cadastro(request):
    if request.method == 'GET':
        return render(request, 'cadastro.html', {})
    else:
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        
        if senha != confirmar_senha:
            messages.add_message(request, constants.ERROR, 'A senha e a sua confirmação são diferentes')
            return redirect(reverse('usuarios-cadastro'))

        user = User.objects.filter(username = username)

        if user:
            messages.add_message(request, constants.ERROR, 'Usuário já está cadastrado')
            return redirect(reverse('usuarios-cadastro'))
      
        try:
            User.objects.create_user(username = username, password = senha)
            return redirect(reverse('usuarios-login'))
        except:
            messages.add_message(request, constants.ERROR, 'Erro interno')
            return redirect(reverse('usuarios-cadastro'))
