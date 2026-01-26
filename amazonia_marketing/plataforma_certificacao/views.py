from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
# Importamos as classes que criamos no models.py
from .models import (
    UsuariosLegado, Produtos, Certificacoes, UsuarioBase, Produtor, Empresa,
    Carrinho, ItemCarrinho, Pedido, ItemPedido
)
# Importamos as classes de formulário
from .forms import (
    ProdutoForm, 
    ProdutoComAutodeclaracaoForm, 
    CadastroProdutorForm, 
    CadastroEmpresaForm,
    ProdutorConfigForm,
    UsuarioBaseConfigForm,
    EmpresaConfigForm,
    CertificacaoMultiplaForm
)
# Importamos datetime
from datetime import datetime
# Importar modulo de alerta sucesso ou erro
from django.contrib import messages
# Nossos modelos (As tabelas do Banco de Dados)
from .models import CustomUser, Produtos, Certificacoes, PerfilProduto, PerfilEmpresa
# Nossos formulários (A validação dos dados que entram)
from .forms import ProdutoForm, ProdutoComAutodeclaracaoForm, CadastroUsuarioForm, EditarPerfilProdutorForm
# Utilitários (ferramentas úteis para data e contagem)
from datetime import datetime
from django.db.models import Count
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.helpers import complete_social_login
# Importar decoradores customizados de segurança
from .decorators import (
    user_is_produtor, 
    user_is_empresa, 
    user_is_admin,
    owns_produto,
    owns_certificacao,
    get_usuario_session
)# ==============================================================================
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
    """
    Login inteligente com redirecionamento baseado no tipo de usuário.
    Tratamento case insensitive para email e tipo.
    """
    msg = None
    if request.method == 'POST':
        email_form = request.POST.get('email', '').strip().lower()  # Case insensitive
        senha_form = request.POST.get('senha', '')

        # Sempre encerra sessão anterior para evitar usuário "preso"
        auth_logout(request)
        request.session.flush()
        
        # Tenta primeiro no novo sistema (UsuarioBase)
        try:
            usuario = UsuarioBase.objects.get(email__iexact=email_form)
            
            # Verifica senha hashada usando o método check_password
            if usuario.check_password(senha_form):
                # Salva dados na sessão customizada
                request.session['usuario_id'] = usuario.id_usuario
                request.session['usuario_tipo'] = usuario.tipo.lower()  # Case insensitive
                request.session['usuario_nome'] = usuario.nome

                # Garante usuário Django para funcionar com login_required
                UserModel = get_user_model()
                django_user = usuario.user
                if not django_user:
                    django_user = UserModel.objects.filter(username=email_form).first()
                if not django_user:
                    django_user = UserModel(username=email_form, email=usuario.email)
                django_user.set_password(senha_form)
                django_user.save()
                if usuario.user_id != django_user.id:
                    usuario.user = django_user
                    usuario.save(update_fields=['user'])

                # Autentica na stack padrão do Django (para login_required)
                auth_login(request, django_user, backend='django.contrib.auth.backends.ModelBackend')
                
                # Redirecionamento inteligente baseado no tipo
                tipo_normalizado = usuario.tipo.lower()  # Tratamento case insensitive
                
                if tipo_normalizado == 'produtor':
                    return redirect('home_produtor')
                elif tipo_normalizado == 'empresa':
                    return redirect('home_empresa')
                elif tipo_normalizado == 'admin':
                    return redirect('home_admin')
                else:
                    return redirect('home_padrao')
            else:
                msg = 'Usuário ou senha inválidos. Tente novamente'
        
        except UsuarioBase.DoesNotExist:
            # Fallback: tenta no sistema legado
            try:
                usuario = UsuariosLegado.objects.get(email__iexact=email_form, senha=senha_form)
                
                # Seta sessão customizada
                request.session['usuario_id'] = usuario.id_usuario
                request.session['usuario_tipo'] = usuario.tipo.lower()
                request.session['usuario_nome'] = usuario.nome

                # Cria/associa usuário Django para login_required
                UserModel = get_user_model()
                django_user = UserModel.objects.filter(username=email_form).first()
                if not django_user:
                    django_user = UserModel(username=email_form, email=usuario.email)
                django_user.set_password(senha_form)
                django_user.save()
                auth_login(request, django_user, backend='django.contrib.auth.backends.ModelBackend')
                
                tipo_normalizado = usuario.tipo.lower()
                
                if tipo_normalizado == 'produtor':
                    return redirect('home_produtor')
                elif tipo_normalizado == 'empresa':
                    return redirect('home_empresa')
                elif tipo_normalizado == 'admin':
                    return redirect('home_admin')
                else:
                    return redirect('home_padrao')
                    
            except UsuariosLegado.DoesNotExist:
                msg = 'Usuário ou senha inválidos. Tente novamente'
    
    return render(request, 'registration/login.html', {'msg': msg})


# --- View para escolher tipo de cadastro ---
def escolher_tipo_cadastro(request):
    """Tela inicial de cadastro onde o usuário escolhe: Produtor ou Empresa"""
    return render(request, 'registration/escolher_tipo.html')


def escolher_tipo_apos_google(request):
    """
    Permite que usuário escolha tipo (Produtor/Empresa) após login com Google.
    Esta view é chamada quando um novo usuário faz login via Google OAuth.
    """
    adapter = get_adapter(request)
    sociallogin = adapter.unstash_sociallogin(request)

    # Se não houver sociallogin em sessão, fluxo expirou
    if sociallogin is None and 'google_data' not in request.session:
        messages.warning(request, 'Sessão expirada. Por favor, faça login novamente.')
        return redirect('login')

    # Dados para mostrar na tela
    google_data = request.session.get('google_data', {})
    if sociallogin:
        extra = sociallogin.account.extra_data
        google_data = {
            'nome': extra.get('name', google_data.get('nome', 'Usuário')),
            'email': extra.get('email', google_data.get('email', '')),
            'picture': extra.get('picture', google_data.get('picture', '')),
        }

    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        if tipo in ['produtor', 'empresa']:
            request.session['tipo_usuario_social'] = tipo

            # Se temos o sociallogin armazenado, completamos o login
            if sociallogin:
                response = complete_social_login(request, sociallogin)
                adapter.clear_stashed_sociallogin(request)
                return response
            messages.warning(request, 'Sessão expirada. Por favor, tente novamente.')
            return redirect('login')
        messages.error(request, 'Tipo de usuário inválido.')

    return render(request, 'registration/escolher_tipo_google.html', {
        'nome': google_data.get('nome', 'Usuário'),
        'email': google_data.get('email', ''),
        'picture': google_data.get('picture', '')
    })


# --- View para cadastro de Produtor ---
def cadastro_produtor(request):
    """Cadastro específico para produtores"""
    if request.method == 'POST':
        form = CadastroProdutorForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            
            # Garante que o usuário Django foi criado e autenticado
            UserModel = get_user_model()
            django_user = usuario.user
            if not django_user:
                django_user = UserModel.objects.filter(username=usuario.email).first()
            if django_user:
                # Autentica no Django
                auth_login(request, django_user, backend='django.contrib.auth.backends.ModelBackend')
            
            # Salva dados na sessão customizada
            request.session['usuario_id'] = usuario.id_usuario
            request.session['usuario_tipo'] = 'produtor'
            request.session['usuario_nome'] = usuario.nome
            
            messages.success(request, f'Bem-vindo, {usuario.nome}! Cadastro realizado com sucesso.')
            return redirect('home_produtor')
    else:
        form = CadastroProdutorForm()
    
    return render(request, 'registration/cadastro_produtor.html', {'form': form})


# --- View para cadastro de Empresa ---
def cadastro_empresa(request):
    """Cadastro específico para empresas"""
    if request.method == 'POST':
        form = CadastroEmpresaForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            
            # Garante que o usuário Django foi criado e autenticado
            UserModel = get_user_model()
            django_user = usuario.user
            if not django_user:
                django_user = UserModel.objects.filter(username=usuario.email).first()
            if django_user:
                # Autentica no Django
                auth_login(request, django_user, backend='django.contrib.auth.backends.ModelBackend')
            
            # Salva dados na sessão customizada
            request.session['usuario_id'] = usuario.id_usuario
            request.session['usuario_tipo'] = 'empresa'
            request.session['usuario_nome'] = usuario.nome
            
            messages.success(request, f'Bem-vindo, {usuario.nome}! Cadastro realizado com sucesso.')
            return redirect('home_empresa')
    else:
        form = CadastroEmpresaForm()
    
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
    """
    Dashboard do produtor com seus produtos e certificações.
    PROTEÇÃO: @login_required + @user_is_produtor garante acesso apenas a produtores autenticados.
    IDOR Prevention: Filtra produtos apenas do usuário logado.
    """
    # Identifica quem é o produtor logado
    usuario = get_usuario_session(request)
    if not usuario:
        return redirect('login')
    
    # PROTEÇÃO CONTRA IDOR: Filtra APENAS produtos do usuário logado
    produtos = Produtos.objects.filter(usuario=usuario)
    
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
    """
    Envio de autodeclaração para certificação.
    PROTEÇÃO: @login_required + @user_is_produtor garante acesso apenas a produtores autenticados.
    IDOR Prevention: Filtra produtos apenas do usuário logado.
    """
    usuario = get_usuario_session(request)
    if not usuario:
        return redirect('login')
    
    # PROTEÇÃO CONTRA IDOR: Filtra APENAS produtos do produtor logado
    if request.method == 'POST':
        form = ProdutoComAutodeclaracaoForm(request.POST, request.FILES)
        # Filtra o dropdown para mostrar só produtos do usuário logado
        form.fields['produto'].queryset = Produtos.objects.filter(usuario=request.user)
        
        if form.is_valid():
            # Extraímos os dados limpos
            produto_selecionado = form.cleaned_data['produto']
            
            # Validação extra: Garantir que o produto pertence ao usuário
            if produto_selecionado.usuario != usuario:
                messages.error(request, 'Acesso negado. Este produto não pertence a você.')
                return redirect('home_produtor')
            
            texto = form.cleaned_data['texto_autodeclaracao']
            arquivo = form.cleaned_data['arquivo_autodeclaracao']
            
            # Regra de Negócio: Criação da Certificação
            nova_certificacao = Certificacoes(
                produto=produto_selecionado,
                texto_autodeclaracao=texto,
                documento=arquivo,
                status_certificacao='pendente',
                data_envio=datetime.now().date(),
                admin_responsavel=None,
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

# ---  Função para o produtor adicionar produtos ---
@verificar_autenticacao
@login_required(login_url='login')
@user_is_produtor
def cadastro_produto(request):
    """
    Cadastro de novo produto.
    PROTEÇÃO: @login_required + @user_is_produtor garante acesso apenas a produtores autenticados.
    IDOR Prevention: Atribui automaticamente o dono do produto ao usuário logado.
    """
    usuario = get_usuario_session(request)
    if not usuario:
        return redirect('login')
    
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            produto = form.save(commit=False)
            
            # PROTEÇÃO CONTRA IDOR: Define automaticamente o dono como usuário logado
            produto.usuario = usuario
            produto.status_estoque = 'disponivel'
            
            produto.save()
            messages.success(request, f'Produto "{produto.nome}" cadastrado com sucesso!')
            return redirect('home_produtor')
    else:
        form = ProdutoForm()
    
    return render(request, 'cadastro_produto.html', {'form': form})


@login_required(login_url='login')
@user_is_produtor
def deletar_produto(request, produto_id):
    """
    Deletar produto (apenas o dono pode deletar).
    PROTEÇÃO: @login_required + @user_is_produtor
    IDOR Prevention: Valida que o usuário é o dono do produto.
    """
    usuario = get_usuario_session(request)
    if not usuario:
        return redirect('login')
    
    # PROTEÇÃO CONTRA IDOR: Filtra apenas produtos do usuário logado
    produto = get_object_or_404(Produtos, id_produto=produto_id, usuario=usuario)
    
    # Deletar certificações vinculadas em cascata
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


@login_required(login_url='login')
@user_is_empresa
def home_empresa(request):
    """
    Dashboard da empresa com foco em dados jurídicos e status de certificações.
    Mostra resumo de produtos, selos e verificação cadastral.
    """
    usuario = get_usuario_session(request)
    if not usuario:
        return redirect('login')

    # Perfil de empresa (dados jurídicos) - cria automaticamente se não existir
    try:
        empresa_profile = usuario.empresa_profile
    except Empresa.DoesNotExist:
        # Se o perfil não existe, tenta criar um vazio
        try:
            empresa_profile = Empresa.objects.create(usuario=usuario)
        except Exception as e:
            messages.error(request, f'Erro ao criar perfil de empresa: {str(e)}')
            return redirect('login')

    # Métricas de produtos e certificações
    produtos = Produtos.objects.filter(usuario=usuario)
    certificacoes = Certificacoes.objects.filter(produto__usuario=usuario)
    pendentes = certificacoes.filter(status_certificacao='pendente').count()
    aprovados = certificacoes.filter(status_certificacao='aprovado').count()
    reprovados = certificacoes.filter(status_certificacao='reprovado').count()

    # Documentação faltante (para evitar perfis falsos)
    docs_faltando = []
    if not empresa_profile.documento_contrato_social:
        docs_faltando.append('Contrato Social/Estatuto')
    if not empresa_profile.documento_cnpj:
        docs_faltando.append('Comprovante de CNPJ')
    if not empresa_profile.documento_alvara:
        docs_faltando.append('Alvará de Funcionamento')

    # Pedidos recentes (caso a empresa atue como compradora)
    pedidos_recentes = Pedido.objects.filter(usuario=usuario).order_by('-data_pedido')[:5]

    context = {
        'usuario_nome': usuario.nome or 'Empresa',
        'status_verificacao': empresa_profile.status_verificacao,
        'produtos_total': produtos.count(),
        'cert_pendentes': pendentes,
        'cert_aprovados': aprovados,
        'cert_reprovados': reprovados,
        'docs_faltando': docs_faltando,
        'pedidos_recentes': pedidos_recentes,
        'empresa': empresa_profile,
    }
    return render(request, 'home_empresa.html', context)


@login_required(login_url='login')
@user_is_admin
def home_admin(request):
    """
    Dashboard do administrador/auditor.
    PROTEÇÃO: @login_required + @user_is_admin garante acesso apenas a auditores.
    """
    # Métricas para exibir no dashboard
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
    # Limpa sessão e autenticação Django
    auth_logout(request)
    request.session.flush()
    return redirect('login')


# ============================================================================
# VIEWS DE CONFIGURAÇÃO DE PERFIL
# ============================================================================

@login_required(login_url='login')
@user_is_produtor
def config_perfil_produtor(request):
    """
    View para configuração de perfil do produtor.
    Permite editar biografia, foto, contatos e redes sociais.
    """
    usuario = get_usuario_session(request)
    if not usuario:
        return redirect('login')
    
    try:
        produtor = usuario.produtor_profile
    except Produtor.DoesNotExist:
        messages.error(request, 'Perfil de produtor não encontrado.')
        return redirect('home_produtor')
    
    if request.method == 'POST':
        form_usuario = UsuarioBaseConfigForm(request.POST, instance=usuario)
        form_produtor = ProdutorConfigForm(request.POST, request.FILES, instance=produtor)
        
        if form_usuario.is_valid() and form_produtor.is_valid():
            form_usuario.save()
            form_produtor.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('config_perfil_produtor')
    else:
        form_usuario = UsuarioBaseConfigForm(instance=usuario)
        form_produtor = ProdutorConfigForm(instance=produtor)
    
    context = {
        'form_usuario': form_usuario,
        'form_produtor': form_produtor,
        'usuario': usuario,
        'produtor': produtor,
    }
    return render(request, 'produtor_config_perfil.html', context)


@login_required(login_url='login')
@user_is_empresa
def config_perfil_empresa(request):
    """
    View para configuração de perfil da empresa.
    Permite editar dados jurídicos, documentação e informações comerciais.
    Inclui validação rigorosa e integração com API de CNPJ.
    """
    usuario = get_usuario_session(request)
    if not usuario:
        return redirect('login')
    
    try:
        empresa = usuario.empresa_profile
    except Empresa.DoesNotExist:
        messages.error(request, 'Perfil de empresa não encontrado.')
        return redirect('home_empresa')
    
    if request.method == 'POST':
        form_usuario = UsuarioBaseConfigForm(request.POST, instance=usuario)
        form_empresa = EmpresaConfigForm(request.POST, request.FILES, instance=empresa)
        
        if form_usuario.is_valid() and form_empresa.is_valid():
            form_usuario.save()
            empresa_obj = form_empresa.save(commit=False)
            
            # Se CNPJ foi alterado e empresa tem documentos, marca como pendente verificação
            if 'cnpj' in form_empresa.changed_data and empresa.status_verificacao == 'verificado':
                empresa_obj.status_verificacao = 'pendente'
                messages.info(request, 'CNPJ alterado. Sua empresa será reverificada.')
            
            empresa_obj.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('config_perfil_empresa')
    else:
        form_usuario = UsuarioBaseConfigForm(instance=usuario)
        form_empresa = EmpresaConfigForm(instance=empresa)
    
    context = {
        'form_usuario': form_usuario,
        'form_empresa': form_empresa,
        'usuario': usuario,
        'empresa': empresa,
    }
    return render(request, 'empresa_config_perfil.html', context)


# ============================================================================
# VIEWS DE DETALHAMENTO PARA ADMIN (AUDITOR)
# ============================================================================

@login_required(login_url='login')
@user_is_admin
def detalhe_certificacao(request, certificacao_id):
    """
    DetailView para certificação específica.
    Mostra todas as informações detalhadas para análise do auditor.
    """
    certificacao = get_object_or_404(Certificacoes, id_certificacao=certificacao_id)
    
    # Informações do produto e produtor
    produto = certificacao.produto
    produtor = produto.usuario
    
    context = {
        'certificacao': certificacao,
        'produto': produto,
        'produtor': produtor,
    }
    return render(request, 'admin_detalhe_certificacao.html', context)


@login_required(login_url='login')
@user_is_admin
def lista_certificacoes_aprovadas(request):
    """
    Lista detalhada de todas as certificações aprovadas.
    """
    certificacoes = Certificacoes.objects.filter(
        status_certificacao='aprovado'
    ).select_related('produto', 'produto__usuario', 'admin_responsavel').order_by('-data_resposta')
    
    context = {
        'certificacoes': certificacoes,
        'titulo': 'Selos Emitidos',
        'status_filtro': 'aprovado'
    }
    return render(request, 'admin_lista_certificacoes.html', context)


@login_required(login_url='login')
@user_is_admin
def lista_certificacoes_reprovadas(request):
    """
    Lista detalhada de todas as certificações reprovadas.
    """
    certificacoes = Certificacoes.objects.filter(
        status_certificacao='reprovado'
    ).select_related('produto', 'produto__usuario', 'admin_responsavel').order_by('-data_resposta')
    
    context = {
        'certificacoes': certificacoes,
        'titulo': 'Selos Reprovados',
        'status_filtro': 'reprovado'
    }
    return render(request, 'admin_lista_certificacoes.html', context)


@login_required(login_url='login')
@user_is_admin
def lista_certificacoes_pendentes(request):
    """
    Lista detalhada de todas as certificações pendentes (fila de análise).
    """
    certificacoes = Certificacoes.objects.filter(
        status_certificacao='pendente'
    ).select_related('produto', 'produto__usuario').order_by('data_envio')
    
    context = {
        'certificacoes': certificacoes,
        'titulo': 'Fila de Análise',
        'status_filtro': 'pendente'
    }
    return render(request, 'admin_lista_certificacoes.html', context)


# ============================================================================
# ATUALIZAÇÃO DA VIEW DE ENVIO DE AUTODECLARAÇÃO (UPLOAD MÚLTIPLO)
# ============================================================================

@login_required(login_url='login')
@user_is_produtor
def enviar_autodeclaracao_multipla(request):
    """
    View atualizada para permitir upload de até 3 documentos.
    Substitui a view antiga enviar_autodeclaracao.
    """
    usuario = get_usuario_session(request)
    if not usuario:
        return redirect('login')
    
    if request.method == 'POST':
        form = CertificacaoMultiplaForm(request.POST, request.FILES)
        form.fields['produto'].queryset = Produtos.objects.filter(usuario=usuario)
        
        if form.is_valid():
            produto_selecionado = form.cleaned_data['produto']
            texto = form.cleaned_data['texto_autodeclaracao']
            doc1 = form.cleaned_data.get('documento_1')
            doc2 = form.cleaned_data.get('documento_2')
            doc3 = form.cleaned_data.get('documento_3')
            
            # Cria a certificação
            certificacao = Certificacoes.objects.create(
                produto=produto_selecionado,
                texto_autodeclaracao=texto,
                documento=doc1,
                documento_2=doc2,
                documento_3=doc3,
                data_envio=datetime.now().date(),
                status_certificacao='pendente'
            )
            
            messages.success(request, f'Certificação enviada com sucesso para o produto "{produto_selecionado.nome}"!')
            return redirect('home_produtor')
    else:
        form = CertificacaoMultiplaForm()
        form.fields['produto'].queryset = Produtos.objects.filter(usuario=usuario)
    
    context = {
        'form': form,
        'usuario': usuario,
    }
    return render(request, 'enviar_autodeclaracao_multipla.html', context)


# ============================================================================
# VALIDADOR DE CNPJ COM API PÚBLICA
# ============================================================================

import requests
from django.http import JsonResponse

def validar_cnpj_api(request):
    """
    API endpoint para validar CNPJ usando API pública (ReceitaWS).
    Retorna dados da empresa se CNPJ for válido.
    """
    cnpj = request.GET.get('cnpj', '')
    
    if not cnpj:
        return JsonResponse({'erro': 'CNPJ não fornecido'}, status=400)
    
    # Remove formatação
    cnpj_numeros = ''.join(filter(str.isdigit, cnpj))
    
    if len(cnpj_numeros) != 14:
        return JsonResponse({'erro': 'CNPJ deve ter 14 dígitos'}, status=400)
    
    try:
        # Consulta API pública da Receita Federal
        url = f'https://www.receitaws.com.br/v1/cnpj/{cnpj_numeros}'
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            dados = response.json()
            
            if dados.get('status') == 'ERROR':
                return JsonResponse({
                    'valido': False,
                    'erro': dados.get('message', 'CNPJ inválido')
                }, status=400)
            
            return JsonResponse({
                'valido': True,
                'razao_social': dados.get('nome', ''),
                'nome_fantasia': dados.get('fantasia', ''),
                'cnpj': dados.get('cnpj', ''),
                'situacao': dados.get('situacao', ''),
                'logradouro': dados.get('logradouro', ''),
                'numero': dados.get('numero', ''),
                'municipio': dados.get('municipio', ''),
                'uf': dados.get('uf', ''),
                'cep': dados.get('cep', ''),
                'telefone': dados.get('telefone', ''),
            })
        else:
            return JsonResponse({
                'erro': 'Erro ao consultar API da Receita Federal'
            }, status=500)
            
    except requests.RequestException as e:
        return JsonResponse({
            'erro': f'Erro de conexão: {str(e)}'
        }, status=500)


# ============================================================================
# VIEWS DE CARRINHO E CHECKOUT
# ============================================================================

@login_required(login_url='login')
def ver_carrinho(request):
    """View para visualizar o carrinho de compras"""
    usuario = get_usuario_session(request)
    if not usuario:
        return redirect('login')
    
    carrinho, created = Carrinho.objects.get_or_create(usuario=usuario, ativo=True)
    itens = carrinho.itens.all().select_related('produto')
    total = carrinho.get_total()
    quantidade_itens = carrinho.get_quantidade_itens()
    
    context = {
        'carrinho': carrinho,
        'itens': itens,
        'total': total,
        'quantidade_itens': quantidade_itens,
    }
    
    return render(request, 'carrinho.html', context)


@login_required(login_url='login')
def adicionar_ao_carrinho(request, produto_id):
    """View para adicionar produto ao carrinho"""
    usuario = get_usuario_session(request)
    if not usuario:
        return redirect('login')
    
    produto = get_object_or_404(Produtos, id_produto=produto_id)
    
    if produto.status_estoque != 'disponivel':
        messages.error(request, 'Este produto não está disponível no momento.')
        return redirect('home_publica')
    
    carrinho, created = Carrinho.objects.get_or_create(usuario=usuario, ativo=True)
    
    item, created = ItemCarrinho.objects.get_or_create(
        carrinho=carrinho,
        produto=produto,
        defaults={'preco_unitario': produto.preco, 'quantidade': 1}
    )
    
    if not created:
        item.quantidade += 1
        item.save()
        messages.success(request, f'Quantidade de {produto.nome} atualizada no carrinho!')
    else:
        messages.success(request, f'{produto.nome} adicionado ao carrinho!')
    
    return redirect('ver_carrinho')


@login_required(login_url='login')
def remover_do_carrinho(request, item_id):
    """View para remover item do carrinho"""
    usuario = get_usuario_session(request)
    if not usuario:
        return redirect('login')
    
    item = get_object_or_404(ItemCarrinho, pk=item_id, carrinho__usuario=usuario)
    produto_nome = item.produto.nome
    item.delete()
    
    messages.success(request, f'{produto_nome} removido do carrinho!')
    return redirect('ver_carrinho')


@login_required(login_url='login')
def atualizar_quantidade_carrinho(request, item_id):
    """View para atualizar quantidade de um item no carrinho"""
    if request.method == 'POST':
        usuario = get_usuario_session(request)
        if not usuario:
            return redirect('login')
        
        item = get_object_or_404(ItemCarrinho, pk=item_id, carrinho__usuario=usuario)
        nova_quantidade = int(request.POST.get('quantidade', 1))
        
        if nova_quantidade > 0:
            item.quantidade = nova_quantidade
            item.save()
            messages.success(request, 'Quantidade atualizada!')
        else:
            item.delete()
            messages.success(request, 'Item removido do carrinho!')
    
    return redirect('ver_carrinho')


@login_required(login_url='login')
def checkout(request):
    """View para página de checkout"""
    usuario = get_usuario_session(request)
    if not usuario:
        return redirect('login')
    
    carrinho = get_object_or_404(Carrinho, usuario=usuario, ativo=True)
    itens = carrinho.itens.all().select_related('produto')
    
    if not itens:
        messages.warning(request, 'Seu carrinho está vazio!')
        return redirect('home_publica')
    
    total = carrinho.get_total()
    
    if request.method == 'POST':
        # Criar pedido
        pedido = Pedido.objects.create(
            usuario=usuario,
            total=total,
            endereco_entrega=request.POST.get('endereco'),
            cidade_entrega=request.POST.get('cidade'),
            estado_entrega=request.POST.get('estado'),
            cep_entrega=request.POST.get('cep'),
            telefone_contato=request.POST.get('telefone'),
            metodo_pagamento=request.POST.get('metodo_pagamento'),
            observacoes=request.POST.get('observacoes', '')
        )
        
        # Criar itens do pedido
        for item in itens:
            ItemPedido.objects.create(
                pedido=pedido,
                produto=item.produto,
                quantidade=item.quantidade,
                preco_unitario=item.preco_unitario,
                subtotal=item.get_subtotal()
            )
        
        # Limpar carrinho
        carrinho.ativo = False
        carrinho.save()
        
        messages.success(request, f'Pedido #{pedido.pk} realizado com sucesso!')
        return redirect('detalhes_pedido', pedido_id=pedido.pk)
    
    context = {
        'carrinho': carrinho,
        'itens': itens,
        'total': total,
        'usuario': usuario,
    }
    
    return render(request, 'checkout.html', context)


@login_required(login_url='login')
def meus_pedidos(request):
    """View para listar pedidos do usuário"""
    usuario = get_usuario_session(request)
    if not usuario:
        return redirect('login')
    
    pedidos = Pedido.objects.filter(usuario=usuario).prefetch_related('itens__produto')
    
    context = {
        'pedidos': pedidos,
    }
    
    return render(request, 'meus_pedidos.html', context)


@login_required(login_url='login')
def detalhes_pedido(request, pedido_id):
    """View para ver detalhes de um pedido específico"""
    usuario = get_usuario_session(request)
    if not usuario:
        return redirect('login')
    
    pedido = get_object_or_404(Pedido, pk=pedido_id, usuario=usuario)
    itens = pedido.itens.all().select_related('produto')
    
    context = {
        'pedido': pedido,
        'itens': itens,
    }
    
    return render(request, 'detalhes_pedido.html', context)


# ============================================================================
# VIEWS DE MARKETPLACE EXTERNO
# ============================================================================

@login_required(login_url='login')
@user_is_produtor
def gerar_anuncio_marketplace(request, produto_id):
    """View para gerar anúncio para marketplace externo"""
    usuario = get_usuario_session(request)
    if not usuario:
        return redirect('login')
    
    produto = get_object_or_404(Produtos, id_produto=produto_id, usuario=usuario)
    
    if request.method == 'POST':
        plataforma = request.POST.get('plataforma')
        
        # Verificar se produto tem certificação aprovada
        tem_certificacao = Certificacoes.objects.filter(
            produto=produto,
            status_certificacao='aprovado'
        ).exists()
        
        # Gerar conteúdo do anúncio
        conteudo = f"""
📦 {produto.nome}
💰 R$ {produto.preco}
📂 Categoria: {produto.categoria}

📝 Descrição:
{produto.descricao}

{'✅ PRODUTO CERTIFICADO - Comércio Justo e Sustentável' if tem_certificacao else ''}

🌿 Amazônia Marketing - Produtos Autênticos da Amazônia

#ComercioJusto #Sustentabilidade #ProdutosNaturais #Amazonia
        """
        
        # Salvar anúncio
        marketplace = Marketplace.objects.create(
            produto=produto,
            plataforma=plataforma,
            conteudo_gerado=conteudo,
            data_geracao=datetime.now().date()
        )
        
        messages.success(request, f'Anúncio gerado para {plataforma}!')
        return redirect('visualizar_anuncio', anuncio_id=marketplace.id_anuncio)
    
    context = {
        'produto': produto,
    }
    
    return render(request, 'gerar_anuncio.html', context)


@login_required(login_url='login')
@user_is_produtor
def visualizar_anuncio(request, anuncio_id):
    """View para visualizar anúncio gerado"""
    usuario = get_usuario_session(request)
    if not usuario:
        return redirect('login')
    
    anuncio = get_object_or_404(Marketplace, id_anuncio=anuncio_id, produto__usuario=usuario)
    
    context = {
        'anuncio': anuncio,
    }
    
    return render(request, 'visualizar_anuncio.html', context)


@login_required(login_url='login')
@user_is_produtor
def meus_anuncios(request):
    """View para listar todos os anúncios do produtor"""
    usuario = get_usuario_session(request)
    if not usuario:
        return redirect('login')
    
    anuncios = Marketplace.objects.filter(produto__usuario=usuario).select_related('produto').order_by('-data_geracao')
    
    context = {
        'anuncios': anuncios,
    }
    
    return render(request, 'meus_anuncios.html', context)


# --- Função para deslogar o usuário --- (mantida por compatibilidade)
# Movida para cima no código
  
# --- Função para cadastrar novo usuário ---

# ---  Função para adicionar certificação ao produto ---

# ---  Função para empresa comprar produtos de produtor ---
