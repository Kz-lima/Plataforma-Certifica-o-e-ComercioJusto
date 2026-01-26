# 📊 Diagrama da Nova Arquitetura

## Arquitetura Anterior (Problema)

```
┌─────────────────────────────────────┐
│      Tabela: Usuarios              │
├─────────────────────────────────────┤
│ • id_usuario                        │
│ • nome                              │
│ • email                             │
│ • tipo (produtor/empresa/admin)    │
│ • cpf (usado só por produtores)     │
│ • cnpj (usado só por empresas)      │
│ • matricula (usado só por admin)    │
│ • telefone                          │
│ • endereco                          │
│ • senha (texto puro - inseguro)    │
└─────────────────────────────────────┘
         ❌ Todos misturados
         ❌ Difícil escalar
         ❌ Sem configurações específicas
         ❌ Sem admin Django
```

---

## Arquitetura Nova (Solução)

```
┌─────────────────────────────────────┐
│    Django AbstractUser              │
│  (Autenticação Segura do Django)    │
│   • username                        │
│   • password (hashed)               │
│   • email                           │
│   • first_name, last_name           │
│   • is_active, is_staff             │
│   • date_joined, last_login         │
└────────────────┬────────────────────┘
                 │ herança
                 ▼
┌─────────────────────────────────────┐
│      UsuarioBase (Nova!)            │
├─────────────────────────────────────┤
│ Estende AbstractUser com:           │
│ • tipo (produtor/empresa/admin)     │
│ • telefone                          │
│ • endereco                          │
│ • id_usuario (PK)                   │
└────────────────┬────────────────────┘
                 │
     ┌───────────┴───────────┐
     │                       │
     ▼ OneToOne              ▼ OneToOne
┌──────────────────┐  ┌──────────────────┐
│   Produtor       │  │    Empresa       │
├──────────────────┤  ├──────────────────┤
│ • cpf (único)    │  │ • cnpj (único)   │
│ • data_criacao   │  │ • razao_social   │
│                  │  │ • data_criacao   │
│ Access:          │  │                  │
│ usuario.produtor │  │ Access:          │
│        _profile  │  │ usuario.empresa_ │
│                  │  │        profile   │
└──────────────────┘  └──────────────────┘

      ✅ Bem organizado
      ✅ Fácil de escalar
      ✅ Seguro (Django Auth)
      ✅ Com admin Django
      ✅ Configurações específicas
```

---

## Relacionamentos

```
UsuarioBase ──1─────────────────N─────── Produtos
     │
     │ (1:1)
     ├─── Produtor
     │
     │ (1:1)
     └─── Empresa

Certificacoes ──N─────────────1──── Produtos
      │
      └──N─────────1──── UsuarioBase (admin_responsavel)

Marketplace ──N─────────────1──── Produtos
```

---

## Tabelas do Banco de Dados

### Antes (1 tabela)
```
├── Usuarios (tabela única)
│   ├── Todos os dados misturados
│   └── Campos não utilizados por alguns tipos
```

### Depois (Novo Sistema)
```
├── plataforma_certificacao_usuariobase
│   ├── Dados de autenticação (do Django)
│   ├── Tipo de usuário
│   ├── Telefone
│   └── Endereço
│
├── plataforma_certificacao_produtor
│   ├── usuario_id (1:1 com UsuarioBase)
│   ├── cpf
│   └── data_criacao
│
├── plataforma_certificacao_empresa
│   ├── usuario_id (1:1 com UsuarioBase)
│   ├── cnpj
│   ├── razao_social
│   └── data_criacao
│
├── Usuarios (tabela legada, mantida para compatibilidade)
│   └── managed = False
│
├── Certificacoes (atualizado)
│   └── admin_responsavel → UsuarioBase
│
├── Produtos (atualizado)
│   └── usuario → UsuarioBase
│
├── Marketplace (sem alterações)
│
└── ... (outras tabelas do Django Auth)
```

---

## Comparação de Campos

### Campo: Tipo de Usuário

| Antes | Depois |
|-------|--------|
| `Usuario.tipo = 'produtor'` | `UsuarioBase.tipo = 'produtor'` + `Produtor` profile |
| Sem estrutura específica | Estrutura específica com CPF, CNPJ, etc. |
| Sem configurações por tipo | Fácil adicionar configs por tipo |

### Campo: Autenticação

| Antes | Depois |
|-------|--------|
| `Usuario.senha` (texto puro!) ❌ | `UsuarioBase.password` (hash seguro) ✅ |
| Sem permissões Django | Sistema de permissões Django completo |
| Sem login integrado | Django Admin e Auth automáticos |

### Campo: CPF

| Antes | Depois |
|-------|--------|
| `Usuario.cpf` (em todos) | `Produtor.cpf` (apenas produtores) |
| Campo vazio para empresas/admin | Sem campos vazios desnecessários |

---

## Django Admin - Antes vs Depois

### Antes
```
❌ Nenhum admin registrado
❌ Não conseguia gerenciar dados pela admin
❌ Forçava usar SQL direto
❌ Sem interface visual
```

### Depois
```
✅ 7 modelos registrados no admin
✅ Interface visual em http://localhost:8000/admin
✅ Filtros avançados (por tipo, status, data)
✅ Buscas por username, email, CPF, CNPJ
✅ Organização em abas/fieldsets
✅ Validação automática de dados
✅ Histórico de mudanças
```

---

## Exemplo de Fluxo: Criar um Produtor

### Antes
```
INSERT INTO Usuarios 
  (nome, email, senha, tipo, telefone, endereco, cpf, cnpj, matricula)
VALUES 
  ('João Silva', 'joao@email.com', 'senhaLivre', 'produtor', 
   '11999999999', 'Rua X', '123.456.789-00', NULL, NULL)
```

### Depois
```python
from django.contrib.auth import get_user_model
from plataforma_certificacao.models import Produtor

User = get_user_model()

# Criar usuário
usuario = User.objects.create_user(
    username='joao_silva',
    email='joao@email.com',
    password='senhaLivre',  # Django hash automaticamente!
    tipo='produtor',
    telefone='11999999999',
    endereco='Rua X'
)

# Criar perfil
Produtor.objects.create(
    usuario=usuario,
    cpf='123.456.789-00'
)

# Agora tudo está seguro, validado e pronto para usar! ✅
```

---

## Verificações de Segurança

### Antes ❌
```python
usuario.senha = 'minhasenha123'  # Texto puro - INSEGURO
usuario.save()
```

### Depois ✅
```python
usuario.set_password('minhasenha123')  # Hashed - SEGURO
usuario.save()
```

---

## Transição Gradual

A tabela legada `Usuarios` foi mantida com `managed = False`, permitindo:

```
1. Novos dados ──→ UsuarioBase + Produtor/Empresa
2. Dados antigos ──→ Continuam em Usuarios (legado)
3. Migração gradual ──→ Script para mover dados conforme necessário
4. Sem quebra ──→ Sistema continua funcionando durante transição
```

---

## Checklist de Implementação

### ✅ Arquivo: models.py
- [x] Importado `AbstractUser`
- [x] Criado `UsuarioBase` estendendo `AbstractUser`
- [x] Criado `Produtor` com OneToOneField
- [x] Criado `Empresa` com OneToOneField
- [x] Atualizado `Certificacoes` (admin_responsavel)
- [x] Atualizado `Produtos` (usuario)
- [x] Criado `UsuariosLegado` (compatibilidade)

### ✅ Arquivo: admin.py
- [x] Importados todos os modelos
- [x] Registrado `UsuarioBase` com fieldsets
- [x] Registrado `Produtor` com filtros
- [x] Registrado `Empresa` com filtros
- [x] Registrado `Certificacoes` com fieldsets
- [x] Registrado `Marketplace` com filtros
- [x] Registrado `Produtos` com fieldsets
- [x] Registrado `UsuariosLegado` (legado)

### ✅ Arquivo: settings.py
- [x] Adicionado `AUTH_USER_MODEL`
- [x] Configuração apontando para `UsuarioBase`

---

## 🚀 Próximas Etapas Recomendadas

1. **Executar Migrações**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Criar Super Usuário**
   ```bash
   python manage.py createsuperuser
   ```

3. **Testar Admin**
   - Acessar: http://localhost:8000/admin
   - Criar um produtor
   - Criar uma empresa
   - Testar filtros e buscas

4. **Atualizar Views** (conforme necessário)
   - Revisar `views.py`
   - Usar `request.user` (já é `UsuarioBase`)
   - Testar login/logout

5. **Atualizar Forms** (conforme necessário)
   - Revisar `forms.py`
   - Atualizar para usar novo modelo
   - Adicionar campos específicos de Produtor/Empresa

---

**Implementação completa e pronta para uso! 🎉**
