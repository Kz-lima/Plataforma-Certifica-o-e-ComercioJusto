# 🎯 Guia Prático - Nova Arquitetura de Usuários

## Como Usar a Nova Estrutura

### 1. Criar um Novo Produtor

```python
from django.contrib.auth import get_user_model
from plataforma_certificacao.models import Produtor

User = get_user_model()  # Retorna UsuarioBase

# Criar usuário base
usuario = User.objects.create_user(
    username='joao_silva',
    email='joao@email.com',
    password='senha123',
    tipo='produtor',
    telefone='11999999999',
    endereco='Rua das Flores, 123'
)

# Criar perfil de produtor
produtor = Produtor.objects.create(
    usuario=usuario,
    cpf='123.456.789-00'
)

print(usuario)  # joao_silva (Produtor)
print(produtor.cpf)  # 123.456.789-00
print(usuario.produtor_profile)  # Produtor: joao_silva
```

---

### 2. Criar uma Nova Empresa

```python
from django.contrib.auth import get_user_model
from plataforma_certificacao.models import Empresa

User = get_user_model()

# Criar usuário base
usuario = User.objects.create_user(
    username='amazonia_corp',
    email='contato@amazonia.com.br',
    password='senha456',
    tipo='empresa',
    telefone='1133333333',
    endereco='Avenida Paulista, 1000'
)

# Criar perfil de empresa
empresa = Empresa.objects.create(
    usuario=usuario,
    cnpj='12.345.678/0001-99',
    razao_social='Amazônia Comércio Justo LTDA'
)

print(usuario)  # amazonia_corp (Empresa)
print(empresa.razao_social)  # Amazônia Comércio Justo LTDA
print(usuario.empresa_profile)  # Empresa: amazonia_corp
```

---

### 3. Consultar Usuários por Tipo

```python
from django.contrib.auth import get_user_model

User = get_user_model()

# Todos os produtores
produtores = User.objects.filter(tipo='produtor')

# Todas as empresas
empresas = User.objects.filter(tipo='empresa')

# Administradores
admins = User.objects.filter(tipo='admin', is_staff=True)

# Usuários ativos
usuarios_ativos = User.objects.filter(is_active=True)
```

---

### 4. Acessar Dados Específicos do Produtor

```python
usuario = User.objects.get(username='joao_silva')

# Acessar dados específicos de produtor
if hasattr(usuario, 'produtor_profile'):
    cpf = usuario.produtor_profile.cpf
    data_criacao = usuario.produtor_profile.data_criacao
    print(f"CPF: {cpf}")
    print(f"Membro desde: {data_criacao}")
else:
    print("Este usuário não é um produtor")
```

---

### 5. Acessar Dados Específicos da Empresa

```python
usuario = User.objects.get(username='amazonia_corp')

# Acessar dados específicos de empresa
if hasattr(usuario, 'empresa_profile'):
    cnpj = usuario.empresa_profile.cnpj
    razao_social = usuario.empresa_profile.razao_social
    print(f"CNPJ: {cnpj}")
    print(f"Razão Social: {razao_social}")
else:
    print("Este usuário não é uma empresa")
```

---

### 6. Atualizar Informações de Um Produtor

```python
usuario = User.objects.get(username='joao_silva')

# Atualizar dados da UsuarioBase
usuario.telefone = '11988888888'
usuario.endereco = 'Novo endereço'
usuario.save()

# Atualizar dados específicos do produtor
produtor = usuario.produtor_profile
produtor.cpf = '987.654.321-00'
produtor.save()
```

---

### 7. Usar com Django Views

```python
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def perfil_produtor(request):
    """View que exibe perfil do produtor logado"""
    usuario = request.user
    
    if usuario.tipo != 'produtor':
        return HttpResponse("Apenas produtores podem acessar esta página", status=403)
    
    produtor = usuario.produtor_profile
    
    return render(request, 'perfil_produtor.html', {
        'usuario': usuario,
        'cpf': produtor.cpf,
        'membro_desde': produtor.data_criacao
    })
```

---

### 8. Usar com Django Forms

```python
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class CriarProdutorForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'telefone', 'endereco']
    
    cpf = forms.CharField(max_length=14, required=True, label='CPF')
    
    def save(self, commit=True):
        usuario = super().save(commit=commit)
        usuario.tipo = 'produtor'
        
        if commit:
            usuario.save()
            # Criar perfil de produtor
            from plataforma_certificacao.models import Produtor
            Produtor.objects.create(
                usuario=usuario,
                cpf=self.cleaned_data['cpf']
            )
        
        return usuario
```

---

### 9. Verificações e Validações

```python
from django.contrib.auth import get_user_model

User = get_user_model()

usuario = User.objects.get(username='joao_silva')

# Verificar tipo de usuário
if usuario.tipo == 'produtor':
    print("É um produtor")
    
if usuario.tipo == 'empresa':
    print("É uma empresa")

# Verificar se é staff/admin
if usuario.is_staff:
    print("É administrador")

# Verificar se está ativo
if usuario.is_active:
    print("Usuário ativo")
```

---

### 10. Queries Avançadas

```python
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

# Produtores de uma determinada região
produtores_sp = User.objects.filter(
    tipo='produtor',
    endereco__icontains='São Paulo'
)

# Empresas ativas
empresas_ativas = User.objects.filter(
    tipo='empresa',
    is_active=True
)

# Usuários com email específico que é produtor
queryset = User.objects.filter(
    Q(tipo='produtor') & 
    Q(email__endswith='@gmail.com')
)

# Contar produtores
total_produtores = User.objects.filter(tipo='produtor').count()

# Últimos 10 usuários cadastrados
usuarios_recentes = User.objects.order_by('-date_joined')[:10]
```

---

## 🔐 Segurança

### Não Faça:
```python
# ❌ ERRADO - Nunca armazene senhas em texto puro
usuario.senha = 'minhasenha123'  # NÃO FAÇA ISSO!
```

### Faça:
```python
# ✅ CORRETO - Use set_password()
usuario.set_password('minhasenha123')
usuario.save()
```

---

## 📚 Relacionamento de Dados

```
UsuarioBase
├── Dados de Autenticação (username, email, password)
├── Dados Pessoais (first_name, last_name, telefone, endereco)
├── Tipo (produtor, empresa, admin)
├── Status (is_active, is_staff, is_superuser)
└── Timestamps (date_joined, last_login)

Produtor (OneToOne com UsuarioBase)
└── CPF único
└── Data de criação

Empresa (OneToOne com UsuarioBase)
├── CNPJ único
├── Razão Social
└── Data de criação

Produtos (ForeignKey para UsuarioBase)
└── Pertence a um produtor/empresa

Certificacoes (ForeignKey para Produtos e UsuarioBase)
└── Certificação de um produto
└── Responsável: um usuário admin
```

---

## ✅ Checklist de Migração

- [ ] Executar `python manage.py makemigrations`
- [ ] Executar `python manage.py migrate`
- [ ] Testar Django Admin em `/admin`
- [ ] Criar um usuário teste
- [ ] Atualizar views.py para usar `UsuarioBase`
- [ ] Atualizar forms.py conforme necessário
- [ ] Testar login/logout
- [ ] Validar relacionamentos de dados
- [ ] Verificar permissões e grupos

---

**Boa sorte com a nova arquitetura! 🚀**
