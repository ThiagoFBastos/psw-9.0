from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import Categoria, Flashcard, Desafio, FlashcardDesafio
from django.http import HttpResponse, Http404
from django.urls import reverse
from django.contrib import messages
from django.contrib.messages import constants
# Create your views here.


@require_http_methods(['GET', 'POST'])
@login_required(login_url = '/usuarios/login/')
def novo_flashcard(request):
    if request.method == 'GET':
        categoria_filtrar = request.GET.get('categoria', '-1')
        dificuldade_filtrar = request.GET.get('dificuldade', '-1')
 
        categorias = Categoria.objects.all()
        dificuldades = Flashcard.DIFICULDADE_CHOICES

        flashcards = Flashcard.objects.filter(user = request.user)

        if categoria_filtrar != '-1':
            flashcards = flashcards.filter(categoria__id = categoria_filtrar)  

        if dificuldade_filtrar != '-1':
            flashcards = flashcards.filter(dificuldade = dificuldade_filtrar)

        return render(request, 'novo_flashcard.html', {
            'categorias': categorias,
            'dificuldades': dificuldades,
            'flashcards': flashcards
        })
    else:   
        
        pergunta = request.POST.get('pergunta').strip()
        resposta = request.POST.get('resposta').strip()
        categoria = request.POST.get('categoria')
        dificuldade = request.POST.get('dificuldade')

        if len(pergunta) == 0 or len(resposta) == 0:
            messages.add_message(request, constants.ERROR, 'pergunta e/ou resposta vazia')
            return redirect(reverse('flashcard-novo_flashcard'))

        flashcard = Flashcard(user = request.user, pergunta = pergunta, resposta = resposta, categoria_id = categoria, dificuldade = dificuldade)

        flashcard.save()

        messages.add_message(request, constants.SUCCESS, 'flashcard cadastrado com sucesso')

        return redirect(reverse('flashcard-novo_flashcard'))

@require_http_methods(['GET'])
@login_required(login_url = '/usuarios/login/')
def deletar_flashcard(request, id: int):
    flashcard = Flashcard.objects.filter(pk = id).filter(user = request.user).delete()
    return redirect(reverse('flashcard-novo_flashcard'))

@require_http_methods(['GET', 'POST'])
@login_required(login_url = '/usuarios/login/')
def iniciar_desafio(request):
    if request.method == 'GET':
        categorias = Categoria.objects.all()
        dificuldades = Flashcard.DIFICULDADE_CHOICES
        return render(request, 'iniciar_desafio.html', {
            'dificuldades': dificuldades,
            'categorias': categorias
        })
    else:
        titulo = request.POST.get('titulo')
        categorias = request.POST.getlist('categoria')
        dificuldade = request.POST.get('dificuldade')
        qtd_perguntas = int(request.POST.get('qtd_perguntas', 1))

        desafio = Desafio(
            user = request.user,
            titulo = titulo,
            quantidade_perguntas = qtd_perguntas,
            dificuldade = dificuldade
        )

        desafio.save()

        desafio.categoria.add(*categorias)

        flashcards = Flashcard.objects.filter(user = request.user)\
        .filter(dificuldade = dificuldade)\
        .filter(categoria__id__in = categorias)\
        .order_by('?')

        if flashcards.count() < qtd_perguntas:
            messages.add_message(request, constants.ERROR, 'a quantidade de perguntas é superior a quantidade de flashcards')
            return redirect(reverse('flashcard-iniciar_desafio'))

        flashcards = flashcards[:qtd_perguntas]


        for flashcard in flashcards:
            flashcard_desafio = FlashcardDesafio(flashcard = flashcard)
            flashcard_desafio.save()
            desafio.flashcards.add(flashcard_desafio)

        desafio.save()

        return redirect(reverse('flashcard-iniciar_desafio'))

@require_http_methods(['GET'])
@login_required(login_url = '/usuarios/login/')
def listar_desafio(request):
    categoria_filtrar = request.GET.get('categoria')
    dificuldade_filtrar = request.GET.get('dificuldade')

    categorias = Categoria.objects.all()
    dificuldades = Flashcard.DIFICULDADE_CHOICES
    desafios = Desafio.objects.filter(user = request.user)

    if dificuldade_filtrar:
        desafios = desafios.filter(dificuldade = dificuldade_filtrar)
    
    return render(request, 'listar_desafio.html', {
        'categorias': categorias,
        'dificuldades': dificuldades,
        'desafios': desafios
    })

@require_http_methods(['GET'])
@login_required(login_url = '/usuarios/login/')
def desafio(request, id: int):
    desafio = Desafio.objects.get(pk = id)

    if desafio.user != request.user:
        return Http404()

    acertos = desafio.flashcards.filter(respondido=True).filter(acertou=True).count()
    erros = desafio.flashcards.filter(respondido=True).filter(acertou=False).count()
    faltantes = desafio.flashcards.filter(respondido=False).count()
    return render(request, 'desafio.html', {
        'desafio': desafio,
        'acertos': acertos,
        'erros': erros,
        'faltantes': faltantes
        })

@require_http_methods(['GET'])
@login_required(login_url = '/usuarios/login/')
def respondeer_flashcard(request, id: int):
    flashcard_desafio = FlashcardDesafio.objects.get(pk = id)

    if flashcard_desafio.flashcard.user != request.user:
        return Http404()

    acertou = request.GET.get('acertou')
    flashcard_desafio.respondido = True
    flashcard_desafio.acertou = bool(int(acertou))
    flashcard_desafio.save()
    desafio = int(request.GET.get('desafio'))
    return redirect(reverse('flashcard-desafio', args = [desafio]))

@require_http_methods(['GET', 'POST'])
@login_required(login_url = '/usuarios/login/')
def relatorio(request, id : int):
    desafio = Desafio.objects.get(pk = id)
    acertos = desafio.flashcards.filter(respondido=True).filter(acertou=True).count()
    erros = desafio.flashcards.filter(respondido=True).filter(acertou=False).count()

    categorias = desafio.categoria.all()
    categoria_names = [categoria.nome for categoria in categorias]
    
    categoria_acertos = []

    melhores_categorias = []
    piores_categorias = []

    for categoria in categoria_names:
        acertos_categoria = desafio.flashcards.filter(flashcard__categoria__nome = categoria).filter(acertou = True).count()
        erros_categoria = desafio.flashcards.filter(flashcard__categoria__nome = categoria).filter(acertou = False).count()        
        categoria_acertos.append(acertos_categoria)
        melhores_categorias.append((acertos_categoria, erros_categoria, categoria))
        piores_categorias.append((acertos_categoria, erros_categoria, categoria))
   
    melhores_categorias.sort(key = lambda c: c[0], reverse = True)
    piores_categorias.sort(key = lambda c: c[0])

    melhores_categorias = melhores_categorias[:3]
    piores_categorias = piores_categorias[:3]

    return render(request, 'relatorio.html', {
        'desafio': desafio, 
        'acertos': acertos, 
        'erros': erros, 
        'categoria_acertos' : categoria_acertos, 
        'categoria_names': categoria_names,
        'melhores_categorias': melhores_categorias,
        'piores_categorias': piores_categorias
    })
