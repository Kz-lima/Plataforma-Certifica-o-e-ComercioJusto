# 🔐 Guia Completo - Login Social com Google (django-allauth)

## 📋 Checklist de Implementação

- [ ] 1. Instalar django-allauth
- [ ] 2. Configurar settings.py
- [ ] 3. Configurar URLs
- [ ] 4. Criar credenciais no Google Cloud Console
- [ ] 5. Executar migrações
- [ ] 6. Adicionar Site e Social App no Django Admin
- [ ] 7. Criar adapter customizado
- [ ] 8. Atualizar templates
- [ ] 9. Testar o fluxo completo

---

## 🚀 Passo 1: Instalar django-allauth

Abra o terminal no diretório do projeto e execute:

```bash
cd amazonia_marketing
.\venv\Scripts\Activate.ps1
pip install django-allauth
```

Ou adicione ao `requirements.txt`:
```
django-allauth==0.57.0
```

E depois:
```bash
pip install -r requirements.txt
```

---

## ⚙️ Passo 2: Configurar settings.py COMPLETO

Você já adicionou os apps, mas faltam algumas configurações. Vou atualizar:

```python
# amazonia_marketing/settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # ADICIONAR ESTA LINHA
    
    'plataforma_certificacao',
    
    # Django Allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

# ID do site (necessário para allauth)
SITE_ID = 1

# Configurações do django-allauth
AUTHENTICATION_BACKENDS = [
    # Backend padrão do Django
    'django.contrib.auth.backends.ModelBackend',
    
    # Backend do allauth para social login
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Configurações de autenticação
LOGIN_REDIRECT_URL = '/'  # Para onde redirecionar após login
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'optional'  # 'mandatory' para obrigar verificação

# Configurações do provedor Google
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'APP': {
            'client_id': 'SEU_CLIENT_ID_AQUI',  # Substituir depois
            'secret': 'SEU_CLIENT_SECRET_AQUI',  # Substituir depois
            'key': ''
        }
    }
}

# Adapter customizado (criaremos depois)
SOCIALACCOUNT_ADAPTER = 'plataforma_certificacao.adapters.CustomSocialAccountAdapter'
```

---

## 🔗 Passo 3: Configurar URLs

Atualize o arquivo `amazonia_marketing/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('plataforma_certificacao.urls')),
    
    # URLs do django-allauth
    path('accounts/', include('allauth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## 🌐 Passo 4: Criar Credenciais no Google Cloud Console

### 4.1 Acessar Google Cloud Console

1. Acesse: https://console.cloud.google.com/
2. Faça login com sua conta Google
3. Crie um novo projeto ou selecione um existente

### 4.2 Ativar Google+ API

1. No menu lateral, vá em **APIs e Serviços** > **Biblioteca**
2. Procure por "Google+ API"
3. Clique em **Ativar**

### 4.3 Criar Credenciais OAuth 2.0

1. Vá em **APIs e Serviços** > **Credenciais**
2. Clique em **+ CRIAR CREDENCIAIS**
3. Escolha **ID do cliente OAuth**
4. Tipo de aplicativo: **Aplicativo da Web**
5. Preencha:
   - **Nome**: Amazônia Marketing
   - **Origens JavaScript autorizadas**:
     ```
     http://localhost:8000
     http://127.0.0.1:8000
     ```
   - **URIs de redirecionamento autorizados**:
     ```
     http://localhost:8000/accounts/google/login/callback/
     http://127.0.0.1:8000/accounts/google/login/callback/
     ```
6. Clique em **CRIAR**
7. **COPIE** o **Client ID** e o **Client Secret**

### 4.4 Configurar Tela de Consentimento

1. Vá em **APIs e Serviços** > **Tela de consentimento OAuth**
2. Escolha **Externo** (para testes)
3. Preencha:
   - **Nome do app**: Amazônia Marketing
   - **Email de suporte do usuário**: seu@email.com
   - **Domínios autorizados**: localhost
   - **Email do desenvolvedor**: seu@email.com
4. Salve

---

## 🗄️ Passo 5: Executar Migrações

```bash
python manage.py migrate
```

Isso criará as tabelas necessárias para o django-allauth.

---

## 🔑 Passo 6: Configurar no Django Admin

### 6.1 Criar Superusuário (se ainda não tiver)

```bash
python manage.py createsuperuser
```

### 6.2 Acessar o Admin

1. Execute o servidor: `python manage.py runserver`
2. Acesse: http://localhost:8000/admin
3. Faça login com o superusuário

### 6.3 Adicionar Site

1. Vá em **Sites**
2. Edite o site existente ou adicione um novo:
   - **Domain name**: `localhost:8000`
   - **Display name**: `Amazônia Marketing`
3. Salve

### 6.4 Adicionar Social Application

1. Vá em **Social applications** (dentro de "Social accounts")
2. Clique em **Add Social Application**
3. Preencha:
   - **Provider**: Google
   - **Name**: Google OAuth
   - **Client id**: (cole o Client ID do Google)
   - **Secret key**: (cole o Client Secret do Google)
   - **Sites**: Selecione "localhost:8000" e mova para "Chosen sites"
4. Salve

---

## 🎯 Passo 7: Criar Adapter Customizado

Crie o arquivo `plataforma_certificacao/adapters.py`:

```python
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import perform_login
from django.shortcuts import redirect
from .models import UsuarioBase, Produtor, Empresa


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Adapter customizado para mapear dados do Google para UsuarioBase.
    Permite que o usuário escolha se é Produtor ou Empresa após login social.
    """
    
    def pre_social_login(self, request, sociallogin):
        """
        Chamado antes do login social ser completado.
        Aqui podemos fazer mapeamento de dados.
        """
        # Se o usuário já está conectado, não faz nada
        if sociallogin.is_existing:
            return
        
        # Pega dados do Google
        email = sociallogin.account.extra_data.get('email')
        
        # Verifica se já existe usuário com esse email
        try:
            usuario = UsuarioBase.objects.get(email__iexact=email)
            # Conecta a conta social ao usuário existente
            sociallogin.connect(request, usuario)
        except UsuarioBase.DoesNotExist:
            # Novo usuário - vamos criar depois do login
            pass
    
    def save_user(self, request, sociallogin, form=None):
        """
        Salva o usuário após login social.
        Aqui criamos o UsuarioBase com dados do Google.
        """
        # Pega dados do Google
        google_data = sociallogin.account.extra_data
        email = google_data.get('email')
        nome = google_data.get('name')
        
        # Verifica se precisa escolher tipo
        tipo = request.session.get('tipo_usuario_social', None)
        
        if not tipo:
            # Redireciona para escolher tipo
            request.session['google_data'] = {
                'email': email,
                'nome': nome,
                'sociallogin': sociallogin.serialize()
            }
            return None  # Não cria usuário ainda
        
        # Cria UsuarioBase
        usuario = UsuarioBase.objects.create(
            nome=nome,
            email=email.lower(),
            tipo=tipo.lower()
        )
        
        # Cria perfil específico
        if tipo.lower() == 'produtor':
            Produtor.objects.create(usuario=usuario)
        elif tipo.lower() == 'empresa':
            Empresa.objects.create(usuario=usuario)
        
        # Limpa sessão
        if 'tipo_usuario_social' in request.session:
            del request.session['tipo_usuario_social']
        if 'google_data' in request.session:
            del request.session['google_data']
        
        return usuario
    
    def populate_user(self, request, sociallogin, data):
        """
        Popula o objeto de usuário com dados do provider social.
        """
        user = super().populate_user(request, sociallogin, data)
        
        # Pega dados extras do Google
        extra_data = sociallogin.account.extra_data
        
        # Podemos adicionar mais campos aqui se necessário
        # user.first_name = extra_data.get('given_name', '')
        # user.last_name = extra_data.get('family_name', '')
        
        return user
```

---

## 🎨 Passo 8: Atualizar Templates

### 8.1 Adicionar botão no login

Atualize `templates/registration/login.html`, adicione antes do botão "Entrar":

```html
<!-- Botão Login com Google -->
<div style="margin-bottom: 20px; text-align: center;">
    <a href="{% url 'google_login' %}" 
       style="display: inline-block; 
              background-color: #fff; 
              color: #333; 
              padding: 12px 20px; 
              border-radius: 5px; 
              text-decoration: none; 
              border: 1px solid #ddd;
              width: 100%;
              box-sizing: border-box;
              font-weight: bold;">
        <img src="https://developers.google.com/identity/images/g-logo.png" 
             alt="Google" 
             style="width: 20px; vertical-align: middle; margin-right: 10px;">
        Entrar com Google
    </a>
</div>

<div style="text-align: center; margin: 15px 0; color: #666;">
    <span style="background: #f5f5f5; padding: 0 10px;">OU</span>
</div>
```

### 8.2 Criar view para escolher tipo após Google login

Atualize `views.py`:

```python
def escolher_tipo_apos_google(request):
    """
    Permite que usuário escolha tipo (Produtor/Empresa) após login com Google.
    """
    if 'google_data' not in request.session:
        return redirect('login')
    
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        request.session['tipo_usuario_social'] = tipo
        
        # Redireciona de volta para completar o login
        return redirect('google_callback')
    
    google_data = request.session.get('google_data')
    return render(request, 'registration/escolher_tipo_google.html', {
        'nome': google_data.get('nome'),
        'email': google_data.get('email')
    })
```

Adicione a rota em `urls.py`:

```python
path('registration/escolher-tipo-google/', views.escolher_tipo_apos_google, name='escolher_tipo_google'),
```

### 8.3 Criar template escolher_tipo_google.html

```html
{% extends 'base.html' %}

{% block content %}
<div class="container" style="max-width: 600px; margin: 50px auto; text-align: center;">
    <h2>Bem-vindo, {{ nome }}!</h2>
    <p>Email: {{ email }}</p>
    <p style="margin: 30px 0;">Como você deseja usar a plataforma?</p>
    
    <form method="POST">
        {% csrf_token %}
        
        <div style="display: flex; gap: 20px; justify-content: center; margin-bottom: 30px;">
            <button type="submit" name="tipo" value="produtor" 
                    style="padding: 20px 40px; font-size: 18px; background: #28a745; color: white; border: none; border-radius: 10px; cursor: pointer;">
                🌱 Sou Produtor
            </button>
            
            <button type="submit" name="tipo" value="empresa" 
                    style="padding: 20px 40px; font-size: 18px; background: #007bff; color: white; border: none; border-radius: 10px; cursor: pointer;">
                🏢 Sou Empresa
            </button>
        </div>
    </form>
</div>
{% endblock %}
```

---

## ✅ Passo 9: Testar o Fluxo

### Teste 1: Login com Google (usuário novo)
1. Acesse: http://localhost:8000/registration/login/
2. Clique em "Entrar com Google"
3. Faça login com sua conta Google
4. Escolha "Sou Produtor" ou "Sou Empresa"
5. ✅ Deve criar usuário e redirecionar para dashboard

### Teste 2: Login com Google (usuário existente)
1. Faça logout
2. Clique em "Entrar com Google" novamente
3. ✅ Deve reconhecer e logar direto

---

## 🐛 Troubleshooting

### Erro: "redirect_uri_mismatch"
**Solução**: Verifique se as URIs no Google Console estão exatamente:
```
http://localhost:8000/accounts/google/login/callback/
```

### Erro: "Site matching query does not exist"
**Solução**: 
```python
from django.contrib.sites.models import Site
Site.objects.create(domain='localhost:8000', name='Amazônia Marketing')
```

### Erro: "No Social Application found"
**Solução**: Certifique-se de adicionar a Social Application no Admin com as credenciais corretas.

---

## 📝 Resumo dos Comandos

```bash
# 1. Instalar allauth
pip install django-allauth

# 2. Executar migrações
python manage.py migrate

# 3. Criar superusuário
python manage.py createsuperuser

# 4. Rodar servidor
python manage.py runserver

# 5. Acessar admin e configurar
http://localhost:8000/admin
```

---

## 🔒 Segurança em Produção

**NUNCA** coloque Client ID e Secret no código!

Use variáveis de ambiente:

```python
# settings.py
import os

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
            'secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
        }
    }
}
```

---

**Implementação completa! 🎉**
Siga os passos na ordem e você terá o Login Social funcionando perfeitamente.
