from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.contrib.messages import constants
from .models import Apostila, ViewApostila

# Create your views here.

@require_http_methods(['GET', 'POST'])
@login_required(login_url = '/usuarios/login/')
def adicionar_apostilas(request):
    if request.method == 'GET':
        tags_filter = request.GET.get('tags')
        apostilas = Apostila.objects.filter(user = request.user)
        apostilas_tags = apostilas.filter(tags__startswith = tags_filter) if tags_filter else []
        print(tags_filter)
        views_totais = ViewApostila.objects.filter(apostila__user = request.user).count()
        return render(request, 'adicionar_apostilas.html', {'apostilas': apostilas, 'views_totais': views_totais, 'apostilas_tags': apostilas_tags})
    else:
        titulo = request.POST.get('titulo')
        arquivo = request.FILES.get('arquivo')
        tags = request.POST.get('tags')

        apostila = Apostila(user = request.user, titulo = titulo, arquivo = arquivo, tags = tags)
        apostila.save()

        messages.add_message(request, constants.SUCCESS, 'salvo com sucesso')

        print(titulo, '\n', arquivo)

        return redirect(reverse('adicionar_apostilas'))

@require_http_methods(['GET'])
@login_required(login_url = '/usuarios/login/')
def apostila(request, id: int):
    apostila = Apostila.objects.get(pk = id)
    view = ViewApostila(ip = request.META['REMOTE_ADDR'], apostila = apostila)
    view.save()
    views_totais = ViewApostila.objects.filter(apostila = apostila).count()
    views_unicas = ViewApostila.objects.filter(apostila = apostila).values('ip').distinct().count()
    return render(request, 'apostila.html', {'apostila': apostila, 'views_totais': views_totais, 'views_unicas': views_unicas})
