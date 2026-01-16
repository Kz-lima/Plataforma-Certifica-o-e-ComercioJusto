# IMPORTAÇÕES ====================================================================
# render: monta o HTML final
# redirect: manda o usuário para outra URL.
# get_object_or_404: tenta buscar no banco; se não achar, mostra erro 404 (não encontrado) em vez de travar o site.
from django.shortcuts import render, redirect, get_object_or_404
# Ferramentas de segurança nativas do Django 
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
# Sistema de mensagens (Aquelas faixas verdes/vermelhas de feedback)
from django.contrib import messages
# Nossos modelos (As tabelas do Banco de Dados)
from .models import CustomUser, Produtos, Certificacoes, PerfilProduto, PerfilEmpresa
# Nossos formulários (A validação dos dados que entram)
from .forms import ProdutoForm, ProdutoComAutodeclaracaoForm, CadastroUsuarioForm, EditarPerfilProdutorForm
# Utilitários (ferramentas úteis para data e contagem)
from datetime import datetime
from django.db.models import Count

# ==============================================================================
# 1. ÁREA PÚBLICA E AUTENTICAÇÃO
# ==============================================================================

def home_publica(request):
    """
    View da página inicial (Vitrine).
    Acessível para qualquer pessoa (logada ou não)
    """
    # Filtra apenas produtos disponíveis no estoque
    produtos = Produtos.objects.filter(status_estoque='disponivel')
    
    # Filtrando apenas os produtos com selo aprovado pelo ID
    ids_com_selo = Certificacoes.objects.filter(status_certificacao='aprovado').values_list('produto_id', flat=True)
    
    # Marcando os produtos que tem selo antes de enviar para o front
    for p in produtos:
        if p.id_produto in ids_com_selo:
            p.tem_selo = True # Criamos esse atributo na memória (não vai pro banco)
        else:
            p.tem_selo = False
            
    # Entregamos a lista processada para o template desenhar.
    return render(request, 'index.html', {'produtos': produtos})

def redirecionar_por_tipo(user):
    """
    Função auxiliar que decide para onde o usuário vai.
    Centraliza a inteligência de 'Para onde cada um vai?'.
    Evita ter que repetir esses IFs no login e no cadastro.
    """
    if user.tipo_usuario == 'produtor':
        return redirect('home_produtor')
    elif user.tipo_usuario == 'empresa':
        return redirect('home_empresa')
    elif user.tipo_usuario == 'auditor':
        return redirect('home_admin')
    elif user.is_superuser:
        return redirect('/admin/')
    else:
        return redirect('home_publica')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from datetime import datetime

# Importamos a classe Usuarios que acabou de ser criada no models.py
from .models import Usuarios, Produtos, Certificacoes
from .forms import ProdutoComAutodeclaracaoForm, CertificacaoForm

# Função para fazer login no sistema
def login_usuarios(request):
    msg = None
    if request.method == 'POST':
        email_form = request.POST.get('email')
        senha_form = request.POST.get('senha')
        
        # BUSCAR NO BANCO
        try:
            # Procura o usuário que tentou fazer o login no banco de dados
            usuario = Usuarios.objects.get(email=email_form, senha=senha_form)
            
            # Usuário existe: salva os dados da sessão 
            request.session['usuario_id'] = usuario.id_usuario
            request.session['usuario_tipo'] = usuario.tipo
            request.session['usuario_nome'] = usuario.nome
            
            # Lógica para redicionar o usuário de acordo com o seu tipo
            
            if usuario.tipo == 'produtor':
                return redirect('home_produtor')
            elif usuario.tipo == 'empresa':
                return redirect('home_empresa')
            elif usuario.tipo == 'admin':
                return redirect('home_admin')
            else:
                return redirect('home_padrao')
            
        # Caso não encontre ninguém com o email ou senha inseridos    
        except Usuarios.DoesNotExist:
            msg = 'Usuário ou senha inválidos. Tente novamente'
    
    return render(request, 'login.html', {'msg': msg })
           
#Função para fazer login no sistema
def login_usuarios(request):
    """
    View de Login Seguro.
    Substitui a lógica manual antiga por 'authenticate()'.
    """
    
    # Se o cara já está logado, não deixa ele ver a tela de login. Joga pro painel.
    if request.user.is_authenticated:
        return redirecionar_por_tipo(request.user)
    
    # Se ele preencheu o formulário e clicou "Entrar"...
    if request.method == 'POST':
        # Django Auth espera 'username' e 'password'. #Pegamos os dados pelos 'names' dos inputs no HTML.
        email_form = request.POST.get('username')
        senha_form = request.POST.get('password')
        
        # Verifica as credenciais: a função authenticate transforma a senha em hash e compara com o hash salvo no banco.
        user = authenticate(request, username=email_form, password=senha_form)
        
        # Se deu certo, cria a Sessão
        if user is not None:
            login(request, user)
            return redirecionar_por_tipo(user)
        else: 
            # Feedback visual de erro
            messages.error(request, 'Usuário ou senha inválidos.')
            
    return render(request, 'registration/login.html')

def cadastro_usuario(request):
    # Se o cara já está logado, chuta ele pro painel (não faz sentido cadastrar de novo)
    if request.user.is_authenticated:
        return redirecionar_por_tipo(request.user)
    
    if request.method == 'POST':
        form = CadastroUsuarioForm(request.POST)
        if form.is_valid():
            # O método save() que criamos no forms.py faz toda a mágica do banco
            user = form.save()
            # Já logamos o usuário automaticamente após o cadastro 
            login(request, user)
            
            messages.success(request, f'Bem-vindo, {user.first_name}! Cadastro realizado.')
            return redirecionar_por_tipo(user)
        else:
            messages.error(request, 'Erro no cadastro. Verifique os campos.')
    else:
        form = CadastroUsuarioForm()
        
    return render(request, 'registration/cadastro.html', {'form': form})

def logout_view(request):
    """
    Encerra a sessão de forma segura.
    Limpa os cookies de autenticação do navegador.
    """
    logout(request)
    return redirect('home_publica')

<<<<<<< HEAD
# ==============================================================================
# 2. ÁREA DO PRODUTOR
# ==============================================================================
=======
    return render(request, 'login.html', {'msg': msg})
>>>>>>> adf9bfd (feat: recupera TODAS as modificações - includes Artefatos, Códigos, PVD, media, forms, templates, migrations)

@login_required # Decorador barra que não está logado
def home_produtor(request):
<<<<<<< HEAD
    # Segurança extra: mesmo logado, verificamos: "Você é realmente um produtor?"
    if request.user.tipo_usuario != 'produtor':
        messages.error(request, 'Área restrita somente para produtores.')
        return redirect('home_publica')
    
    # Filtra produtos que o dono é o usuário logado (request.user)
    produtos = Produtos.objects.filter(usuario=request.user)
    
    # Métricas para o Dashboard:
    total_produtos = produtos.count()
    # Filtro Relacional (__): "Busque certificações onde o produto do usuário é X"
    pendentes = Certificacoes.objects.filter(produto__usuario=request.user, status_certificacao='pendente').count()
    aprovados = Certificacoes.objects.filter(produto__usuario=request.user, status_certificacao='aprovado').count()
        
    # RECUPERAÇÃO DE DADOS EXTRAS DO PERFIL: Tentamos acessar a tabela 'ProdutorPerfil' vinculada.
    try:
        # ATENÇÃO: Certifique-se que no models.py o related_name é 'produtor_perfil'
        # 'produtor_perfil' é o related_name que definimos no models.py
        perfil = request.user.produtor_perfil
        nome_exibicao = perfil.nome  # Pegamos o nome da fazenda/produtor
    except:
        # Fallback caso o perfil não tenha sido criado ou o nome esteja diferente
        nome_exibicao = request.user.first_name or request.user.username
        
    contexto = {
        'produtos': produtos,
        'total_produtos': total_produtos,
        'pendentes': pendentes,
        'aprovados': aprovados,
        'usuario_nome': nome_exibicao,
    }
    
    return render(request, 'home_produtor.html', contexto)
=======
    # Segurança extra: Garante que só PRODUTOR entra aqui
    if request.session.get('usuario_tipo') != 'produtor':
         return redirect('login')
    
    # Buscar produtos do produtor
    usuario_id = request.session.get('usuario_id')
    produtos = Produtos.objects.filter(usuario_id=usuario_id)
    
    # Buscar certificações do produtor
    certificacoes_pendentes = Certificacoes.objects.filter(
        produto__usuario_id=usuario_id,
        status_certificacao='pendente'
    ).count()
    
    certificacoes_aprovadas = Certificacoes.objects.filter(
        produto__usuario_id=usuario_id,
        status_certificacao='aprovado'
    ).count()
    
    context = {
        'produtos': produtos,
        'total_produtos': produtos.count(),
        'certificacoes_pendentes': certificacoes_pendentes,
        'certificacoes_aprovadas': certificacoes_aprovadas,
        'usuario_nome': request.session.get('usuario_nome'),
    }
    
    return render(request, 'home_produtor.html', context)
>>>>>>> adf9bfd (feat: recupera TODAS as modificações - includes Artefatos, Códigos, PVD, media, forms, templates, migrations)

@login_required
def cadastro_produto(request):
    # Verificação de segurança de novo, o cara tem que ser quem diz ser para poder bagunçar as coisas aqui. Não é assim não, fi!
    if request.user.tipo_usuario != 'produtor':
        return redirect('home_publica') 
    
    if request.method == 'POST':
        # Carregamos o form com os dados (POST) e arquivos de imagem (FILES)
        form = ProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            # Cria o objeto na memória RAM, mas não manda pro banco ainda.
            produto = form.save(commit=False)
            # Vincula ao usuário logado (request.user)
            produto.usuario = request.user
            produto.status_estoque = 'disponivel'
            # Agora que sabemos quem é o usuário, podemos salvar no banco.
            produto.save()
            messages.success(request, f'O produto {produto.nome} foi cadastrado')
            return redirect('home_produtor')
    else:
        # Se for GET (abrir a página), entregamos um form vazio para o cara preencher.
        form = ProdutoForm()
        
    return render(request, 'cadastro_produto.html', {'form': form}) 

@login_required
def editar_perfil_produtor(request):
    if request.user.tipo_usuario != 'produtor':
        return redirect('home_publica')
    
    # Tenta pegar o perfil. Se não existir, cria um vazio na memória (evita crash)
    perfil, created = PerfilProduto.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = EditarPerfilProdutorForm(request.POST, request.FILES, instance=perfil)
        
        if form.is_valid():
            # 1. Salva os dados do Perfil (Bio, Nome, etc)
            form.save()
            
            # 2. Salva os dados do Usuário (Nome, Email) manualmente
            request.user.first_name = form.cleaned_data['first_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('home_produtor')
    else:
        # Carrega o formulário com os dados atuais do banco (Preenchimento automático)
        initial_data = {
            'first_name': request.user.first_name,
            'email': request.user.email
        }
        form = EditarPerfilProdutorForm(instance=perfil, initial=initial_data)

    return render(request, 'editar_perfil_produtor.html', {'form': form})
    
    
@login_required
def enviar_autodeclaracao(request):
    # Garantir é sempre bom =)
    if request.user.tipo_usuario != 'produtor':
        return redirect('home_publica')
    
    # Processando o formulário
    if request.method == 'POST':
        form = ProdutoComAutodeclaracaoForm(request.POST, request.FILES)
        # Filtra o dropdown para mostrar só produtos do usuário logado
        form.fields['produto'].queryset = Produtos.objects.filter(usuario=request.user)
        
        if form.is_valid():
            # Extraímos os dados limpos
            produto_selecionado = form.cleaned_data['produto']
            texto = form.cleaned_data['texto_autodeclaracao']
            arquivo = form.cleaned_data['arquivo_autodeclaracao']
            
            # Criamos manualmente o registro na tabela de Certificações
            nova_certificacao = Certificacoes(
                produto=produto_selecionado,
                texto_autodeclaracao=texto,
                arquivo_autodeclaracao=arquivo,
                status_certificacao='pendente', # Nasce pendente
                admin_responsavel=None, # Ninguém auditou ainda
            )
            
            nova_certificacao.save()
            messages.success(request, 'Documento enviado com sucesso! Aguardo a análise do auditor')            
            return redirect('home_produtor')
    else:
        form = ProdutoComAutodeclaracaoForm()
        # Filtra produtos no GET também
        form.fields['produto'].queryset = Produtos.objects.filter(usuario=request.user)
        
    contexto = {
        'form': form,
        'usuario_nome': request.user.first_name or request.user.username
    }
    
    return render(request, 'enviar_autodeclaracao.html', contexto)

@login_required
def deletar_produto(request, produto_id):
    # Busca o produto ou erro 404 se não existir
    produto = get_object_or_404(Produtos, id_produto=produto_id)
    
    # Verificamos se o dono do produto no banco é IGUAL a quem está tentando apagar.
    if produto.usuario != request.user:
        messages.error(request, 'Tentativa de exclusão falha. Você não é o dono do produto!')
        return redirect('home_produtor') 

    # INTEGRIDADE REFERENCIAL (Cascata Manual):
    # Antes de apagar o Pai (Produto), verificamos se tem Filhos (Certificações).
    certificacoes_vinculadas = Certificacoes.objects.filter(produto_id=produto_id)
    if certificacoes_vinculadas.exists():
        qtde = certificacoes_vinculadas.count()
        certificacoes_vinculadas.delete()
        print(f'Sistema: {qtde} certificações deletadas em cascata')
    
    # Agora é seguro apagar o pai
    nome_produto = produto.nome 
    produto.delete()
    messages.success(request, f'Produto: {nome_produto} removido!')   
    return redirect('home_produtor')

# ==============================================================================
# 3. ÁREA DA EMPRESA
# ==============================================================================

@login_required
def home_empresa(request):
    # Bloqueia quem não é empresa
    if request.user.tipo_usuario != 'empresa':
         return redirect('login')
    # Renderiza o dashboard da empresa 
    return render(request, 'home_empresa.html')

# ==============================================================================
# 4. ÁREA DO AUDITOR (ADMIN)
# ==============================================================================

@login_required
def home_admin(request):
<<<<<<< HEAD
    # Permite apenas 'auditor' 
    if request.user.tipo_usuario != 'auditor' and not request.user.is_superuser:
        messages.error(request, 'Acesso negado!')
        return redirect('home_publica')
    
    # O auditor vê os dados de TODOS os produtores, por isso não filtramos por usuário aqui.
    pendente = Certificacoes.objects.filter(status_certificacao='pendente').count()
    aprovado = Certificacoes.objects.filter(status_certificacao='aprovado').count()
    reprovado = Certificacoes.objects.filter(status_certificacao='reprovado').count()
    
    # Listas as cinco últimas para acesso rápido
    ultimas = Certificacoes.objects.select_related('produto').order_by('-data_envio')[:5]
    
    contexto = {
        'pendente': pendente,
        'aprovado': aprovado,
        'reprovado': reprovado,
        'usuario_nome': request.user.username,
    }
    return render(request, 'home_admin.html', contexto)
=======
    # Segurança extra: Garante que só ADMIN entra aqui
    if request.session.get('usuario_tipo') != 'admin':
         return redirect('login')
    
    # Buscar todas as certificações
    todas_certificacoes = Certificacoes.objects.select_related('produto', 'produto__usuario').all()
    
    # Estatísticas
    total_certificacoes = todas_certificacoes.count()
    pendentes = todas_certificacoes.filter(status_certificacao='pendente').count()
    aprovadas = todas_certificacoes.filter(status_certificacao='aprovado').count()
    rejeitadas = todas_certificacoes.filter(status_certificacao='rejeitado').count()
    
    # Certificações recentes (últimas 10 pendentes)
    certificacoes_recentes = todas_certificacoes.filter(
        status_certificacao='pendente'
    ).order_by('-data_envio')[:10]
    
    context = {
        'total_certificacoes': total_certificacoes,
        'pendentes': pendentes,
        'aprovadas': aprovadas,
        'rejeitadas': rejeitadas,
        'certificacoes_recentes': certificacoes_recentes,
        'usuario_nome': request.session.get('usuario_nome'),
    }
    
    return render(request, 'home_admin.html', context)
>>>>>>> adf9bfd (feat: recupera TODAS as modificações - includes Artefatos, Códigos, PVD, media, forms, templates, migrations)

@login_required
def admin_visualizar_certificados(request):
    # Verificação de Permissão
    if request.user.tipo_usuario != 'auditor' and not request.user.is_superuser:
        return redirect('login')
    # Filtro via URL (ex: ?status=pendente)
    status_filtro = request.GET.get('status')
    # O Django faz um JOIN no SQL para trazer os dados do Produto e do Produtor na mesma consulta.
    consulta = Certificacoes.objects.select_related('produto', 'produto__usuario').all().order_by('-data_envio')
    
    if status_filtro: 
        consulta = consulta.filter(status_certificacao=status_filtro)

<<<<<<< HEAD
    return render(request, 'admin_certificacoes.html', {'certificacoes': consulta, 'status_filtro': status_filtro})

@login_required
def admin_detalhes_certificacao(request, certificacao_id):
    if request.user.tipo_usuario != 'auditor' and not request.user.is_superuser:
        return redirect('home_publica')

    # Busca o certificado pelo ID ou dá erro 404
    certificacao = get_object_or_404(Certificacoes, id_certificacao=certificacao_id)
    
    return render(request, 'admin_detalhes_certificacao.html', {'c': certificacao})

@login_required
def admin_responder_certificacoes(request, certificacao_id):
    # Segurança mais um vez.
    if request.user.tipo_usuario != 'auditor' and not request.user.is_superuser:
        return redirect('home_publica')
    
    certificacao = get_object_or_404(Certificacoes, id_certificacao=certificacao_id)
    
    if request.method == 'POST':
        acao = request.POST.get('acao') # Captura qual botão foi clicado (Aprovar/Rejeitar)
        
        if acao == 'aprovar':
            certificacao.status_certificacao = 'aprovado'
            messages.success(request, f'Certificação APROVADA para o produto {certificacao.produto.nome}!')
        elif acao == 'rejeitar':
            # Usando 'reprovado' conforme seu código anterior
            certificacao.status_certificacao = 'reprovado'
            messages.warning(request, f'Certificação REJEITADA para o produto {certificacao.produto.nome}.')
        
        # Registrando o rastro da auditoria (Quem e Quando)
        certificacao.admin_responsavel = request.user
        certificacao.data_resposta = datetime.now().date()
        certificacao.save()
        
    return redirect('admin_visualizar_certificados') 
    



=======
# Função para deslogar o usuário
def logout_view(request):
    # Limpa a sessão (desloga)
    request.session.flush()
    return redirect('login')

# ===== FUNÇÕES DE UPLOAD DE AUTODECLARAÇÃO =====

@verificar_autenticacao
def enviar_autodeclaracao(request):
    """
    View para o produtor enviar a autodeclaração de um produto.
    Permite upload de arquivo e/ou texto da autodeclaração.
    """
    # Segurança extra: Garante que só PRODUTOR entra aqui
    if request.session.get('usuario_tipo') != 'produtor':
        messages.error(request, 'Acesso negado. Apenas produtores podem enviar autodeclaração.')
        return redirect('login')
    
    usuario_id = request.session.get('usuario_id')
    usuario = get_object_or_404(Usuarios, id_usuario=usuario_id)
    
    # Buscar apenas produtos do produtor logado
    produtos_produtor = Produtos.objects.filter(usuario=usuario)
    
    if request.method == 'POST':
        form = ProdutoComAutodeclaracaoForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                produto = form.cleaned_data['produto']
                texto_autodeclaracao = form.cleaned_data.get('texto_autodeclaracao', '')
                arquivo_autodeclaracao = form.cleaned_data.get('arquivo_autodeclaracao')
                
                # Verificar se o produto pertence ao produtor logado
                if produto.usuario_id != usuario_id:
                    messages.error(request, 'Você não tem permissão para cadastrar certificação neste produto.')
                    return redirect('enviar_autodeclaracao')
                
                # Criar a certificação
                certificacao = Certificacoes.objects.create(
                    produto=produto,
                    texto_autodeclaracao=texto_autodeclaracao,
                    arquivo_autodeclaracao=arquivo_autodeclaracao,
                    documento=arquivo_autodeclaracao.name if arquivo_autodeclaracao else 'texto',
                    status_certificacao='pendente',
                    data_envio=datetime.now().date(),
                    admin_responsavel=None
                )
                
                messages.success(
                    request,
                    f'Autodeclaração enviada com sucesso! Sua solicitação está em análise.'
                )
                return redirect('ver_certificacoes')
                
            except Exception as e:
                messages.error(request, f'Erro ao enviar autodeclaração: {str(e)}')
        else:
            # Exibir erros do formulário
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ProdutoComAutodeclaracaoForm()
        # Filtrar apenas produtos do usuário logado
        form.fields['produto'].queryset = produtos_produtor
    
    context = {
        'form': form,
        'usuario_nome': request.session.get('usuario_nome'),
    }
    return render(request, 'enviar_autodeclaracao.html', context)


@verificar_autenticacao
def ver_certificacoes(request):
    """
    View para o produtor visualizar suas certificações e autodeclarações enviadas.
    """
    # Segurança extra: Garante que só PRODUTOR entra aqui
    if request.session.get('usuario_tipo') != 'produtor':
        messages.error(request, 'Acesso negado. Apenas produtores podem visualizar certificações.')
        return redirect('login')
    
    usuario_id = request.session.get('usuario_id')
    
    # Buscar certificações dos produtos do produtor
    produtos_produtor = Produtos.objects.filter(usuario_id=usuario_id)
    certificacoes = Certificacoes.objects.filter(produto__in=produtos_produtor).order_by('-data_envio')
    
    # Adicionar flag para cada certificação indicando se o arquivo existe
    for cert in certificacoes:
        if cert.arquivo_autodeclaracao:
            try:
                # Verificar se o arquivo físico existe
                cert.arquivo_existe = cert.arquivo_autodeclaracao.storage.exists(cert.arquivo_autodeclaracao.name)
            except:
                cert.arquivo_existe = False
        else:
            cert.arquivo_existe = False
    
    context = {
        'certificacoes': certificacoes,
        'usuario_nome': request.session.get('usuario_nome'),
    }
    return render(request, 'ver_certificacoes.html', context)


@verificar_autenticacao
def baixar_arquivo_certificacao(request, certificacao_id):
    """
    View para permitir o download do arquivo de autodeclaração.
    """
    certificacao = get_object_or_404(Certificacoes, id_certificacao=certificacao_id)
    
    # Verificar permissão: o usuário deve ser o dono do produto
    usuario_id = request.session.get('usuario_id')
    if certificacao.produto.usuario_id != usuario_id and request.session.get('usuario_tipo') != 'admin':
        messages.error(request, 'Você não tem permissão para acessar este arquivo.')
        return redirect('login')
    
    if certificacao.arquivo_autodeclaracao:
        arquivo = certificacao.arquivo_autodeclaracao.open('rb')
        response = HttpResponse(arquivo.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{certificacao.arquivo_autodeclaracao.name}"'
        return response
    else:
        messages.warning(request, 'Esta certificação não possui arquivo anexado.')
        return redirect('ver_certificacoes')


@verificar_autenticacao
def admin_visualizar_certificacoes(request):
    """
    View para admin visualizar todas as certificações enviadas.
    """
    # Segurança: Garante que só ADMIN entra aqui
    if request.session.get('usuario_tipo') != 'admin':
        messages.error(request, 'Acesso negado. Apenas administradores podem acessar esta página.')
        return redirect('login')
    
    # Buscar todas as certificações, ordenadas por data
    certificacoes = Certificacoes.objects.select_related('produto', 'produto__usuario', 'admin_responsavel').order_by('-data_envio')
    
    # Filtro por status se fornecido
    status_filtro = request.GET.get('status')
    if status_filtro:
        certificacoes = certificacoes.filter(status_certificacao=status_filtro)
    
    context = {
        'certificacoes': certificacoes,
        'usuario_nome': request.session.get('usuario_nome'),
        'status_filtro': status_filtro,
    }
    return render(request, 'admin_certificacoes.html', context)


@verificar_autenticacao
def admin_responder_certificacao(request, certificacao_id):
    """
    View para admin aprovar/rejeitar uma certificação.
    Atualiza o status para 'aprovado' ou 'rejeitado' e registra a data e admin.
    """
    # Segurança: Garante que só ADMIN entra aqui
    if request.session.get('usuario_tipo') != 'admin':
        messages.error(request, 'Acesso negado.')
        return redirect('login')
    
    certificacao = get_object_or_404(Certificacoes, id_certificacao=certificacao_id)
    usuario_admin_id = request.session.get('usuario_id')
    
    if request.method == 'POST':
        acao = request.POST.get('acao')
        comentario = request.POST.get('comentario', '')
        
        # Aceitar valores de ação
        if acao in ['aprovar', 'aprovado', 'aprovada']:
            certificacao.status_certificacao = 'aprovado'
            certificacao.data_resposta = datetime.now().date()
            certificacao.admin_responsavel_id = usuario_admin_id
            certificacao.save()
            
            messages.success(
                request, 
                f'✅ Certificação APROVADA com sucesso! Produto: {certificacao.produto.nome}'
            )
            return redirect('admin_visualizar_certificacoes')
            
        elif acao in ['rejeitar', 'rejeitado', 'rejeitada']:
            certificacao.status_certificacao = 'rejeitado'
            certificacao.data_resposta = datetime.now().date()
            certificacao.admin_responsavel_id = usuario_admin_id
            certificacao.save()
            
            messages.warning(
                request,
                f'❌ Certificação REJEITADA. Produto: {certificacao.produto.nome}'
            )
            return redirect('admin_visualizar_certificacoes')
        else:
            messages.error(request, 'Ação inválida.')
    
    context = {
        'certificacao': certificacao,
        'usuario_nome': request.session.get('usuario_nome'),
    }
    return render(request, 'admin_responder_certificacao.html', context)

# Função para cadastrar novo usuário

# Função para adicionar certificação ao produto

# Função para adicionar produtos

# Função para empresa comprar produtos de produtor
>>>>>>> adf9bfd (feat: recupera TODAS as modificações - includes Artefatos, Códigos, PVD, media, forms, templates, migrations)

