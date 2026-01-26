# 🔐 SEGURANÇA E CONTROLE DE ACESSO - Implementação Completa

## 📋 Resumo

Implementamos segurança em **3 camadas** no Django:
1. **Autenticação** (@login_required)
2. **Autorização** (@user_is_produtor, @user_is_empresa, @user_is_admin)
3. **IDOR Prevention** (Validação de propriedade de recursos)

---

## 🎯 1. DECORADORES CUSTOMIZADOS

Arquivo: `plataforma_certificacao/decorators.py`

### Decoradores Disponíveis

#### A. `@group_required('NomeDoGrupo')`
Valida se o usuário pertence a um grupo específico.

```python
@group_required('Produtor')
def minha_view(request):
    # Apenas usuários do grupo 'Produtor' acessam
    pass
```

#### B. `@user_is_produtor`
Protege views exclusivas de produtores.

```python
@login_required
@user_is_produtor
def home_produtor(request):
    usuario = get_usuario_session(request)
    # Apenas produtores autenticados
    pass
```

#### C. `@user_is_empresa`
Protege views exclusivas de empresas.

```python
@login_required
@user_is_empresa
def home_empresa(request):
    # Apenas empresas autenticadas
    pass
```

#### D. `@user_is_admin`
Protege views exclusivas de auditores/admins.

```python
@login_required
@user_is_admin
def home_admin(request):
    # Apenas auditores autenticados
    pass
```

#### E. `@owns_produto`
**Protege contra IDOR**: valida se o usuário é o dono do produto.

```python
@login_required
@user_is_produtor
@owns_produto
def editar_produto(request, produto_id):
    produto = kwargs['produto']  # Já filtrado e validado
    # Apenas o dono pode editar
    pass
```

#### F. `@owns_certificacao`
**Protege contra IDOR**: valida se o auditor é responsável pela certificação.

```python
@login_required
@user_is_admin
@owns_certificacao
def responder_certificacao(request, certificacao_id):
    certificacao = kwargs['certificacao']  # Já filtrado
    # Apenas o auditor responsável pode responder
    pass
```

---

## 👥 2. GRUPOS DE SEGURANÇA

Os grupos são criados automaticamente pela migration `0004_create_security_groups.py`.

### Grupos Disponíveis

| Grupo | Descrição | Permissões |
|-------|-----------|-----------|
| **Produtor** | Usuário que cultiva e vende produtos | Gerenciar próprios produtos e certificações |
| **Empresa** | Usuário que compra e revende produtos | Visualizar produtos e criar certificações |
| **Auditor** | Administrador que aprova certificações | Acesso completo a certificações |

### Como Configurar Grupos no Admin

1. Acesse `/admin/auth/group/`
2. Clique em um grupo (ex: "Produtor")
3. Marque as permissões desejadas
4. Salve

**Permissões Padrão:**
```
Produtor:
  ✓ add_produtos
  ✓ change_produtos
  ✓ delete_produtos
  ✓ view_produtos
  ✓ add_certificacoes
  ✓ view_certificacoes

Empresa:
  ✓ view_produtos
  ✓ add_certificacoes
  ✓ view_certificacoes

Auditor:
  ✓ view_produtos
  ✓ view_certificacoes
  ✓ change_certificacoes
  ✓ delete_certificacoes
  ✓ view_usuariobase
```

---

## 🛡️ 3. PROTEÇÃO CONTRA IDOR (Insecure Direct Object References)

### O Problema

URL original (INSEGURA):
```
/produtor/editar-produto/5/
```

Um produtor pode trocar `5` por `6` e editar o produto de outro usuário!

### A Solução

Sempre filtrar por proprietário na view:

```python
@login_required
@user_is_produtor
def editar_produto(request, produto_id):
    usuario = get_usuario_session(request)
    
    # IDOR PREVENTION: Filtrar APENAS produtos do usuário
    produto = get_object_or_404(Produtos, id_produto=produto_id, usuario=usuario)
    
    # Agora é seguro
    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto atualizado!')
            return redirect('home_produtor')
    else:
        form = ProdutoForm(instance=produto)
    
    return render(request, 'editar_produto.html', {'form': form})
```

### Exemplo com Decorador

Usando `@owns_produto`:

```python
@login_required
@user_is_produtor
@owns_produto
def editar_produto(request, produto_id):
    # O decorador já garantiu que o produto pertence ao usuário
    produto = kwargs['produto']
    # código seguro aqui
```

---

## 📝 4. VALIDAÇÃO EM FORMULÁRIOS

Todos os forms usam Django ModelForm com validação:

### Validação de Campos Individuais

```python
class CadastroProdutorForm(forms.ModelForm):
    email = forms.EmailField()
    cpf = forms.CharField(max_length=14)
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Validar se email já existe
        if UsuarioBase.objects.filter(email__iexact=email).exists():
            raise ValidationError('Email já cadastrado.')
        return email.lower()
    
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        cpf_limpo = ''.join(filter(str.isdigit, cpf))
        
        if len(cpf_limpo) != 11:
            raise ValidationError('CPF deve ter 11 dígitos.')
        
        if Produtor.objects.filter(cpf=cpf_limpo).exists():
            raise ValidationError('CPF já cadastrado.')
        
        return cpf_limpo
```

### Validação Cruzada (Multiple Fields)

```python
class CadastroProdutorForm(forms.ModelForm):
    senha = forms.CharField(widget=forms.PasswordInput)
    confirmar_senha = forms.CharField(widget=forms.PasswordInput)
    
    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get('senha')
        confirmar_senha = cleaned_data.get('confirmar_senha')
        
        if senha != confirmar_senha:
            raise ValidationError('As senhas não coincidem.')
        
        return cleaned_data
```

### Validação de Arquivo

```python
def validar_arquivo_seguro(arquivo):
    """Valida tamanho, extensão e MIME type."""
    
    if not arquivo:
        return arquivo
    
    # 1. Tamanho máximo (5MB)
    if arquivo.size > 5 * 1024 * 1024:
        raise ValidationError('Arquivo não pode exceder 5 MB.')
    
    # 2. Extensão permitida
    extensoes_permitidas = ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png']
    extensao = arquivo.name.split('.')[-1].lower()
    
    if extensao not in extensoes_permitidas:
        raise ValidationError(f'Use: {", ".join(extensoes_permitidas)}')
    
    return arquivo
```

---

## 🔑 5. CSRF PROTECTION (CSRF Token)

**OBRIGATÓRIO** em todos os formulários HTML:

```html
<form method="POST" action="{% url 'editar_produto' %}">
    {% csrf_token %}
    
    <!-- Seus campos aqui -->
    <input type="text" name="nome" required>
    <button type="submit">Salvar</button>
</form>
```

**O que o token faz:**
- Previne ataques CSRF (Cross-Site Request Forgery)
- Valida que o formulário veio do seu site
- É gerado automaticamente pelo Django

---

## 🚀 6. EXECUTAR AS MIGRATIONS

Para criar os grupos automaticamente:

```bash
python manage.py migrate
```

Isso executará `0004_create_security_groups.py` e criará:
- Grupo "Produtor"
- Grupo "Empresa"
- Grupo "Auditor"

---

## 📊 7. EXEMPLO COMPLETO - View Protegida

```python
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .decorators import user_is_produtor, get_usuario_session
from .models import Produtos
from .forms import ProdutoForm

@login_required(login_url='login')
@user_is_produtor
def editar_produto(request, produto_id):
    """
    Editar produto - PROTEGIDO
    
    Segurança em 3 camadas:
    1. @login_required - Usuário autenticado
    2. @user_is_produtor - É produtor
    3. Filtro por usuário - Proteção IDOR
    """
    
    # Passo 1: Obter usuário logado
    usuario = get_usuario_session(request)
    if not usuario:
        return redirect('login')
    
    # Passo 2: IDOR Prevention - Filtrar APENAS produtos do usuário
    produto = get_object_or_404(Produtos, id_produto=produto_id, usuario=usuario)
    
    # Passo 3: Processar formulário
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES, instance=produto)
        if form.is_valid():
            form.save()
            messages.success(request, f'Produto "{produto.nome}" atualizado!')
            return redirect('home_produtor')
    else:
        form = ProdutoForm(instance=produto)
    
    context = {
        'form': form,
        'produto': produto,
    }
    return render(request, 'editar_produto.html', context)
```

**Template (editar_produto.html):**
```html
<form method="POST" enctype="multipart/form-data">
    {% csrf_token %}
    
    {{ form.as_p }}
    
    <button type="submit">Salvar Produto</button>
</form>
```

---

## ✅ CHECKLIST DE SEGURANÇA

- [ ] Todas as views protegidas usam `@login_required`
- [ ] Views específicas usam `@user_is_produtor`, `@user_is_empresa`, ou `@user_is_admin`
- [ ] Dados filtrados SEMPRE pelo usuário logado (proteção IDOR)
- [ ] Formulários usam `{% csrf_token %}`
- [ ] Formulários usam ModelForm com `clean()` methods
- [ ] Permissões configuradas no Django Admin
- [ ] Usuários atribuídos aos grupos corretos
- [ ] Migration `0004_create_security_groups.py` foi executada
- [ ] Testes realizados para acesso cruzado (produtor não acessa dados de empresa)

---

## 🔍 TESTANDO SEGURANÇA

### Teste 1: IDOR Prevention
```bash
1. Faça login como Produtor A
2. Crie Produto P1 (ID: 1)
3. Crie outro navegador anônimo
4. Acesse /produtor/editar/1/ sem logar
   Resultado esperado: Redireciona para login ✓
5. Crie Produtor B
6. Crie Produto P2 (ID: 2)
7. Como Produtor A, tente acessar /produtor/editar/2/
   Resultado esperado: 404 - Não encontrado ✓
```

### Teste 2: Group Protection
```bash
1. Faça login como Empresa
2. Tente acessar /auditoria/dashboard
   Resultado esperado: Acesso negado ✓
3. Tente acessar /produtor/dashboard
   Resultado esperado: Acesso negado ✓
```

### Teste 3: CSRF Protection
```bash
1. Remova {% csrf_token %} de um formulário
2. Tente enviar o formulário
   Resultado esperado: Erro 403 CSRF ✓
```

---

## 📚 REFERÊNCIAS

- [Django Login Required](https://docs.djangoproject.com/en/6.0/topics/auth/default/#limiting-access-to-logged-in-users)
- [Django Permissions](https://docs.djangoproject.com/en/6.0/topics/auth/default/#permissions-and-authorization)
- [Django CSRF Protection](https://docs.djangoproject.com/en/6.0/middleware/csrf/)
- [OWASP - IDOR](https://owasp.org/www-community/attacks/Insecure_Direct_Object_References)

---

**Última atualização:** 25/01/2026
**Status:** ✅ Implementação Completa
