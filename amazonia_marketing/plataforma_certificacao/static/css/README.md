# 📋 Documentação da Estrutura CSS - Amazônia Marketing

## 🎨 Visão Geral

A estrutura CSS foi modularizada em arquivos temáticos para melhor manutenibilidade, reutilização e organização. Cada arquivo CSS é responsável por uma seção específica do site.

---

## 📁 Arquivos CSS

### 1. **variables.css** 🎯
**Função:** Definir todas as variáveis globais e padrões do projeto

**Contém:**
- Paleta de cores (verde, amarelo, azul, cinza, etc.)
- Tamanhos de fonte (xs, sm, base, lg, xl, 2xl)
- Espaçamentos (xs até 2xl)
- Sombras (sm, md, lg)
- Border radius (sm, md, lg, full)
- Transições

**Uso:**
```css
/* Usar as variáveis em qualquer arquivo */
color: var(--verde-amazonia);
padding: var(--spacing-lg);
box-shadow: var(--shadow-md);
```

---

### 2. **layout.css** 🏗️
**Função:** Estilos globais de layout (header, footer, navegação)

**Contém:**
- Header/Navegação principal
- Footer com links sociais
- Menu hamburguer (responsivo)
- Container padrão
- Seções base
- Classes utilitárias

**Uso:**
- Importar em `base.html` para que apareça em TODAS as páginas

---

### 3. **auth.css** 🔐
**Função:** Estilos da página de login e formulários de autenticação

**Contém:**
- Animações de entrada
- Estilos de formulários
- Campos de entrada com foco
- Checkboxes
- Botões de submit
- Divisor OU
- Mensagens de erro/sucesso

**Uso:**
- Usar em `login.html`

---

### 4. **auth-choice.css** ✅
**Função:** Estilos da tela de escolha Produtor/Empresa

**Contém:**
- Card de escolha
- Perfil do usuário (avatar, nome, email)
- Botões de opção (produtor/empresa)
- Animações de hover
- Layout responsivo

**Uso:**
- Usar em `escolher_tipo_google.html`

---

### 5. **home.css** 🏠
**Função:** Estilos da página inicial e listagem de produtos

**Contém:**
- Hero section com gradiente
- Grid de produtos
- Cards de produtos
- Badges de certificação
- Filtros de busca
- Preço e ações de produto

**Uso:**
- Usar em `index.html`

---

### 6. **dashboard.css** 📊
**Função:** Estilos dos painéis (Produtor, Empresa, Admin)

**Contém:**
- Layout sidebar + content
- Menu lateral
- Cards de estatísticas
- Tabelas com dados
- Status badges
- Formulários no dashboard

**Uso:**
- Usar em `home_produtor.html`, `home_empresa.html`, `home_admin.html`

---

### 7. **components.css** 🧩
**Função:** Componentes reutilizáveis em toda a plataforma

**Contém:**
- Botões (primary, secondary, success, danger, warning)
- Alertas (success, error, warning, info)
- Cards genéricos
- Modais
- Badges
- Breadcrumb
- Pagination
- Spinner de carregamento

**Uso:**
- Importar em `base.html` para usar em qualquer página

---

## 🎯 Como Usar em Templates Django

### No `base.html`:

```html
<!DOCTYPE html>
<html lang="pt-br">
<head>
    {% load static %}
    
    <!-- CSS GLOBAIS - Aparecem em todas as páginas -->
    <link rel="stylesheet" href="{% static 'css/variables.css' %}">
    <link rel="stylesheet" href="{% static 'css/layout.css' %}">
    <link rel="stylesheet" href="{% static 'css/components.css' %}">
    
    <!-- CSS ESPECÍFICO POR PÁGINA (opcional) -->
    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- Header, Footer, etc. vem aqui -->
    {% block content %}{% endblock %}
</body>
</html>
```

### Em templates específicos:

```html
{% extends 'base.html' %}

{% load static %}

{% block extra_css %}
    <link rel="stylesheet" href="{% static 'css/home.css' %}">
{% endblock %}

{% block content %}
    <div class="hero">
        <h1>Bem-vindo</h1>
    </div>
    
    <div class="products-grid">
        <!-- Produtos aqui -->
    </div>
{% endblock %}
```

---

## 🎨 Variáveis de Cor Disponíveis

| Variável | Cor | Uso |
|----------|-----|-----|
| `--verde-amazonia` | #1C3E1D | Cor primária, texts, backgrounds |
| `--verde-escuro` | #0a4d01 | Hover, detalhes |
| `--amarelo-sol` | #DABB2C | Destaque, botões, divisores |
| `--azul-rio` | #225082 | Links, informações |
| `--branco` | #FFFFFF | Backgrounds, textos inversos |
| `--cinza-claro` | #F5F5F5 | Backgrounds leves |
| `--cinza-medio` | #E0E0E0 | Borders |
| `--preto` | #333333 | Textos principais |

---

## 🔄 Responsividade

Todos os arquivos CSS incluem breakpoints para:

- **Tablet**: `@media (max-width: 768px)`
- **Mobile**: `@media (max-width: 480px)`

Exemplo:
```css
@media (max-width: 768px) {
    .products-grid {
        grid-template-columns: 1fr;
    }
}
```

---

## 🚀 Boas Práticas

1. **Sempre use variáveis** em vez de valores hardcoded
   ```css
   ✅ color: var(--verde-amazonia);
   ❌ color: #1C3E1D;
   ```

2. **Mantenha o nível de especificidade baixo** (use classes, não IDs)
   ```css
   ✅ .button { ... }
   ❌ #submit-button { ... }
   ```

3. **Use nomes de classe descritivos**
   ```css
   ✅ .product-card { ... }
   ❌ .card1 { ... }
   ```

4. **Agrupe estilos relacionados com comentários**
   ```css
   /* ============== HERO SECTION ============== */
   .hero { ... }
   ```

5. **Sempre adicione transições suaves**
   ```css
   transition: var(--transition); /* 0.3s ease */
   ```

---

## 🔗 Ordem de Importação Recomendada

```html
<!-- 1. Variáveis (SEMPRE PRIMEIRO) -->
<link rel="stylesheet" href="{% static 'css/variables.css' %}">

<!-- 2. Layout Global -->
<link rel="stylesheet" href="{% static 'css/layout.css' %}">

<!-- 3. Componentes Reutilizáveis -->
<link rel="stylesheet" href="{% static 'css/components.css' %}">

<!-- 4. Estilos Específicos da Página (por último) -->
<link rel="stylesheet" href="{% static 'css/auth.css' %}">
<link rel="stylesheet" href="{% static 'css/home.css' %}">
<link rel="stylesheet" href="{% static 'css/dashboard.css' %}">
```

---

## 📦 Novos Arquivos CSS Necessários

Para adicionar novos estilos, crie arquivos CSS específicos:

- `css/catalog.css` - Catálogo de produtos avançado
- `css/checkout.css` - Processo de compra
- `css/profile.css` - Perfil do usuário
- `css/admin.css` - Painel administrativo especial

---

## 🐛 Debugging

Se os estilos não aparecerem:

1. Verifique se o arquivo CSS existe em `static/css/`
2. Verifique se rode `python manage.py collectstatic` após adicionar arquivos
3. Limpe o cache do navegador (Ctrl+Shift+Delete)
4. Use DevTools (F12) para verificar se o arquivo está sendo carregado

---

## 📝 Exemplos de Uso Comum

### Botão Primário
```html
<button class="btn btn-primary">Clique aqui</button>
```

### Alert de Sucesso
```html
<div class="alert alert-success">
    <span class="alert-icon">✓</span>
    <div class="alert-content">
        <h4>Sucesso!</h4>
        <p>Operação realizada com sucesso.</p>
    </div>
</div>
```

### Card
```html
<div class="card">
    <div class="card-header">
        <h3>Título</h3>
    </div>
    <div class="card-body">
        Conteúdo aqui
    </div>
    <div class="card-footer">
        <button class="btn btn-primary">Ação</button>
    </div>
</div>
```

### Badge
```html
<span class="badge badge-success">Aprovado</span>
<span class="badge badge-warning">Pendente</span>
```

---

## 🎓 Dúvidas Frequentes

**P: Como adicionar uma cor personalizada?**
A: Adicione em `variables.css` e use em qualquer lugar:
```css
--minha-cor: #ABC123;
```

**P: Como fazer um componente responsivo?**
A: Use `@media` queries:
```css
@media (max-width: 768px) {
    .meu-elemento { /* estilos mobile */ }
}
```

**P: Como animar um elemento?**
A: Use `animation` com `@keyframes`:
```css
animation: slideUp 0.6s ease-out;

@keyframes slideUp {
    from { transform: translateY(30px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}
```

---

**Versão:** 1.0  
**Última Atualização:** Janeiro 2026  
**Desenvolvedor:** GitHub Copilot  
**Status:** ✅ Completo
