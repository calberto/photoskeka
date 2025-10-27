# core/views.py
# views.py
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from .models import Cidade, Fotografia
from .forms import CidadeForm, MediaForm, BuscarFotosForm

def home(request):
    """View principal com busca e listagem de fotografias"""
    
    # Processa cadastro de mídia
    if request.method == 'POST' and 'cadastrar_media' in request.POST:
        print("=" * 50)
        print("Processando upload de mídia...")
        print("POST:", request.POST)
        print("FILES:", request.FILES)
        print("=" * 50)
        
        foto_form = MediaForm(request.POST, request.FILES)
        
        if foto_form.is_valid():
            media = foto_form.save()
            tipo = "vídeo" if media.is_video() else "fotografia"
            messages.success(request, f'{tipo.title()} "{media.titulo}" cadastrada com sucesso!')
            return redirect('core:home')
        else:
            print("ERROS:", foto_form.errors)
            messages.error(request, f'Erro ao cadastrar mídia: {foto_form.errors}')
            for field, errors in foto_form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    
    # Inicializa formulários vazios para GET
    foto_form = MediaForm()
    buscar_form = BuscarFotosForm(request.GET)
    cidade_form = CidadeForm()
    
    # Processa busca de fotos
    fotografias = Fotografia.objects.filter(ativa=True).select_related('cidade')
    cidade_selecionada = None
    
    if request.method == 'POST' and 'buscar_fotos' in request.POST:
        buscar_form = BuscarFotosForm(request.POST)
        if buscar_form.is_valid() and buscar_form.cleaned_data.get('cidade'):
            cidade_busca = buscar_form.cleaned_data['cidade']
            fotografias = fotografias.filter(
                Q(cidade__nome__icontains=cidade_busca) |
                Q(titulo__icontains=cidade_busca) |
                Q(descricao__icontains=cidade_busca)
            )
            try:
                cidade_selecionada = Cidade.objects.get(nome__iexact=cidade_busca, ativa=True)
            except Cidade.DoesNotExist:
                pass
    
    # Lista de cidades ativas
    cidades = Cidade.objects.filter(ativa=True).order_by('nome')
    
    # Atualiza o queryset do formulário de foto
    foto_form.fields['cidade'].queryset = cidades
    
    context = {
        'buscar_form': buscar_form,
        'cidade_form': cidade_form,
        'foto_form': foto_form,
        'fotografias': fotografias,
        'cidades': cidades,
        'cidade_selecionada': cidade_selecionada,
        'total_fotos': fotografias.count(),
        'total_cidades': cidades.count(),
    }
    
    return render(request, 'core/home.html', context)

def cadastrar_cidade(request):
    """View para adicionar nova cidade via AJAX"""
    if request.method == 'POST':
        print("=" * 50)
        print("POST data:", request.POST)
        print("FILES:", request.FILES)
        print("=" * 50)
        
        form = CidadeForm(request.POST)
        
        if form.is_valid():
            nome = form.cleaned_data.get('nome').strip()
            estado = form.cleaned_data.get('estado').strip()
            pais = form.cleaned_data.get('pais').strip()
            
            # Verifica se a cidade já existe (ativa ou inativa)
            cidade_existe = Cidade.objects.filter(
                nome__iexact=nome,
                estado__iexact=estado,
                pais__iexact=pais
            ).first()
            
            if cidade_existe:
                # Se existe e está inativa, ativa novamente
                if not cidade_existe.ativa:
                    cidade_existe.ativa = True
                    cidade_existe.save()
                    mensagem = f'Cidade "{cidade_existe.nome}" reativada com sucesso!'
                else:
                    mensagem = f'Cidade "{cidade_existe.nome}" já estava ativa.'
                
                cidade = cidade_existe
            else:
                # Se não existe, cria nova
                cidade = form.save()
                mensagem = f'Cidade "{cidade.nome}" adicionada com sucesso!'
            
            messages.success(request, mensagem)
            
            return JsonResponse({
                'success': True,
                'message': mensagem,
                'cidade': {
                    'id': cidade.id,
                    'nome': cidade.nome,
                    'estado': cidade.estado,
                    'pais': cidade.pais
                }
            })
        else:
            print("ERROS DO FORMULÁRIO:", form.errors)
            print("Dados recebidos:", form.data)
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'})

def deletar_media_confirm(request, fotografia_pk):
    """Deleta uma mídia e redireciona para a página anterior ou home"""
    try:
        media = Fotografia.objects.get(pk=fotografia_pk)
        titulo_media = media.titulo
        tipo = "vídeo" if media.is_video() else "fotografia"
        media.delete()
        
        messages.success(request, f'{tipo.title()} "{titulo_media}" deletada com sucesso!')
        
    except Fotografia.DoesNotExist:
        messages.error(request, 'Mídia não encontrada.')
    
    # Redireciona para a home
    return redirect('core:home')

# ... resto do código continua igual

def listar_cidades(request):
    """View para listar todas as cidades cadastradas"""
    cidades = Cidade.objects.filter(ativa=True).order_by('nome')
    
    # Conta quantas mídias cada cidade tem
    for cidade in cidades:
        cidade.total_medias = Fotografia.objects.filter(cidade=cidade, ativa=True).count()
    
    context = {
        'cidades': cidades,
        'total_cidades': cidades.count()
        
    }
    
    return render(request, 'core/listar_cidades.html', context)

def cadastrar_media(request):
    """View para cadastrar nova mídia (foto ou vídeo)"""
    if request.method == 'POST':
        form = MediaForm(request.POST, request.FILES)
        if form.is_valid():
            media = form.save()
            tipo = "vídeo" if media.is_video() else "fotografia"
            messages.success(request, f'{tipo.title()} "{media.titulo}" cadastrada com sucesso!')
            return redirect('cadastrar_media')
    else:
        form = MediaForm()
    
    # Lista apenas cidades ativas no formulário
    form.fields['cidade'].queryset = Cidade.objects.filter(ativa=True).order_by('nome')
    
    return render(request, 'cadastrar_media.html', {'form': form})

def listar_medias_cidade(request):
    """View para listar todas as cidades cadastradas"""
    cidades = Cidade.objects.filter(ativa=True).order_by('nome')
    
    # Conta quantas mídias cada cidade tem
    for cidade in cidades:
        cidade.total_medias = Fotografia.objects.filter(cidade=cidade, ativa=True).count()
    
    context = {
        'cidades': cidades,
        'total_cidades': cidades.count()
    }
    
    return render(request, 'core/listar_cidades.html', context)

def detalhe_media(request, media_id):
    """View para exibir detalhes de uma mídia específica"""
    media = get_object_or_404(Fotografia, id=media_id, ativa=True)
    
    # Mídias relacionadas da mesma cidade
    medias_relacionadas = Fotografia.objects.filter(
        cidade=media.cidade, 
        ativa=True
    ).exclude(id=media.id)[:6]
    
    context = {
        'media': media,
        'medias_relacionadas': medias_relacionadas
    }
    
    return render(request, 'detalhe_media.html', context)

def carrousel_cidade(request, cidade_id):
    """View para exibir carrossel de mídias de uma cidade"""
    cidade = get_object_or_404(Cidade, id=cidade_id, ativa=True)
    medias = Fotografia.objects.filter(cidade=cidade, ativa=True).order_by('-data_upload')
    
    if not medias.exists():
        messages.warning(request, f'Não há mídias disponíveis para {cidade.nome}.')
        return redirect('home')
    
    context = {
        'cidade': cidade,
        'medias': medias
    }
    
    return render(request, 'carrousel.html', context)

def deletar_media_confirm(request, fotografia_pk):
    """Deleta uma mídia e redireciona para a página anterior ou home"""
    try:
        media = Fotografia.objects.get(pk=fotografia_pk)
        cidade = media.cidade  # Armazena a cidade antes de deletar
        media.delete()
        
        # Conta quantas fotos ainda existem para esta cidade
        fotos_restantes = Fotografia.objects.filter(cidade=cidade, ativa=True).count()
        
        # Mensagem de sucesso
        tipo = "vídeo" if media.is_video() else "fotografia"
        messages.success(request, f'{tipo.title()} "{media.titulo}" deletada com sucesso!')
        
    except Fotografia.DoesNotExist:
        messages.error(request, 'Mídia não encontrada.')
    
    # Redireciona para a home (nome correto da view)
    # Se veio de uma página anterior (Referer), pode usar:
    # return redirect(request.META.get('HTTP_REFERER', 'core:home'))
    
    return redirect('core:home')

# Create your views here.
