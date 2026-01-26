# 🎨 GUIA VISUAL - Cores e Componentes

## Paleta de Cores Oficial

### Verde Amazônia (Principal)
- **Cor:** `#1C3E1D`
- **Uso:** Headers, botões principais, textos primários
- **RGB:** rgb(28, 62, 29)

### Verde Escuro (Contraste)
- **Cor:** `#0a4d01`
- **Uso:** Hover, borders, sombras escuras
- **RGB:** rgb(10, 77, 1)

### Amarelo Sol (Destaque)
- **Cor:** `#DABB2C`
- **Uso:** Badges, badges, divisores, highlights
- **RGB:** rgb(218, 187, 44)

### Azul Rio (Informação)
- **Cor:** `#225082`
- **Uso:** Links, informações técnicas
- **RGB:** rgb(34, 80, 130)

### Cores de Status
- **Sucesso:** `#27AE60` (Verde)
- **Erro:** `#E74C3C` (Vermelho)
- **Aviso:** `#F39C12` (Laranja)
- **Info:** `#3498DB` (Azul claro)

---

## Tipografia

### Font Family
```
'Segoe UI', 'Calibri', 'Arial', sans-serif
```

### Tamanhos
- **Extra Small (xs):** 12px - Legenda, metadados
- **Small (sm):** 14px - Descrições, helper text
- **Base:** 16px - Texto padrão
- **Large (lg):** 18px - Subtítulos
- **Extra Large (xl):** 24px - Títulos de seção
- **2XL:** 32px - Títulos principais

### Pesos
- **Regular:** 400
- **Medium:** 500
- **Semi-bold:** 600
- **Bold:** 700
- **Extra Bold:** 800

---

## Espaçamento

### Escala de Espaçamentos
- **xs:** 4px - Micro espaçamentos
- **sm:** 8px - Pequenos espaços
- **md:** 16px - Espaçamento padrão
- **lg:** 24px - Espaçamento grande
- **xl:** 32px - Espaçamento extra grande
- **2xl:** 48px - Espaçamento máximo

---

## Sombras

### Tipos de Sombras
```css
--shadow-sm: 0 2px 5px rgba(0, 0, 0, 0.1)
--shadow-md: 0 4px 12px rgba(0, 0, 0, 0.1)
--shadow-lg: 0 10px 25px rgba(0, 0, 0, 0.15)
```

---

## Border Radius

- **sm:** 4px - Pequenas bordas
- **md:** 8px - Bordas padrão
- **lg:** 12px - Bordas grandes
- **full:** 50% - Elemento circular

---

## Transições

```css
--transition: all 0.3s ease
--transition-fast: all 0.15s ease
```

---

## Componentes de Botões

### Botão Primário (Verde)
```html
<button class="btn btn-primary">Ação Principal</button>
```
- Background: Gradiente verde
- Hover: Levanta (+2px)
- Cor: Branco

### Botão Secundário (Branco com borda)
```html
<button class="btn btn-secondary">Ação Secundária</button>
```
- Background: Branco
- Border: Verde
- Hover: Inverte cores

### Botão Sucesso (Verde claro)
```html
<button class="btn btn-success">Confirmar</button>
```
- Background: Gradiente verde claro
- Cor: Branco

### Botão Perigo (Vermelho)
```html
<button class="btn btn-danger">Deletar</button>
```
- Background: Gradiente vermelho
- Cor: Branco

### Botão Aviso (Laranja)
```html
<button class="btn btn-warning">Cuidado</button>
```
- Background: Gradiente laranja
- Cor: Branco

---

## Alertas

### Alert Sucesso
```html
<div class="alert alert-success">
    <span>✓</span> Operação realizada com sucesso!
</div>
```

### Alert Erro
```html
<div class="alert alert-error">
    <span>✕</span> Erro ao processar a solicitação
</div>
```

### Alert Aviso
```html
<div class="alert alert-warning">
    <span>⚠</span> Atenção: Verifique os dados
</div>
```

### Alert Informação
```html
<div class="alert alert-info">
    <span>ℹ</span> Dica: Preencha todos os campos obrigatórios
</div>
```

---

## Cards

### Card Básico
```html
<div class="card">
    <div class="card-header">
        <h3>Título do Card</h3>
    </div>
    <div class="card-body">
        Conteúdo aqui
    </div>
    <div class="card-footer">
        <button class="btn btn-primary">Ação</button>
    </div>
</div>
```

### Card de Produto
```html
<div class="product-card">
    <div class="product-image">
        <img src="produto.jpg" alt="Produto">
        <div class="product-badge">
            🏆 Certificado
        </div>
    </div>
    <div class="product-info">
        <div class="product-category">Categoria</div>
        <div class="product-name">Nome do Produto</div>
        <div class="product-description">Descrição breve</div>
        <div class="product-footer">
            <div class="product-price">R$ 99,90</div>
            <button class="product-action">🛒</button>
        </div>
    </div>
</div>
```

---

## Badges

### Badge Primário (Verde)
```html
<span class="badge badge-primary">Principal</span>
```

### Badge Sucesso (Verde claro)
```html
<span class="badge badge-success">Aprovado</span>
```

### Badge Aviso (Laranja)
```html
<span class="badge badge-warning">Pendente</span>
```

### Badge Perigo (Vermelho)
```html
<span class="badge badge-danger">Rejeitado</span>
```

### Badge Informação (Azul)
```html
<span class="badge badge-info">Novo</span>
```

---

## Formulários

### Grupo de Formulário
```html
<div class="form-group">
    <label for="email">📧 Email</label>
    <input type="email" id="email" name="email" placeholder="seu@email.com">
</div>
```

### Checkbox
```html
<div class="form-checkbox">
    <input type="checkbox" id="terms">
    <label for="terms">Aceito os termos e condições</label>
</div>
```

### Select
```html
<div class="form-group">
    <label for="categoria">Categoria</label>
    <select id="categoria" name="categoria">
        <option>Selecione uma categoria</option>
        <option>Frutas</option>
        <option>Vegetais</option>
    </select>
</div>
```

---

## Tabelas

### Status Badges para Tabelas
```html
<span class="status-badge pending">Pendente</span>
<span class="status-badge approved">Aprovado</span>
<span class="status-badge rejected">Rejeitado</span>
```

---

## Modais

### Abrir Modal
```html
<div id="meuModal" class="modal active">
    <div class="modal-content">
        <div class="modal-header">
            <h2>Título do Modal</h2>
            <button class="modal-close">✕</button>
        </div>
        <div class="modal-body">
            Conteúdo aqui
        </div>
        <div class="modal-footer">
            <button class="btn btn-secondary">Cancelar</button>
            <button class="btn btn-primary">Confirmar</button>
        </div>
    </div>
</div>
```

---

## Paginação

```html
<div class="pagination">
    <a href="#">← Anterior</a>
    <a href="#" class="active">1</a>
    <a href="#">2</a>
    <a href="#">3</a>
    <a href="#">Próximo →</a>
</div>
```

---

## Breadcrumb

```html
<div class="breadcrumb">
    <a href="/">Home</a>
    <span class="breadcrumb-separator">›</span>
    <a href="/produtos">Produtos</a>
    <span class="breadcrumb-separator">›</span>
    <span class="breadcrumb-current">Detalhes do Produto</span>
</div>
```

---

## Loading Spinner

```html
<div class="spinner"></div>
```

---

## Animações Disponíveis

### Fade In
```css
animation: fadeIn 0.8s ease-out;
```

### Slide Up
```css
animation: slideUp 0.6s ease-out;
```

### Scale In
```css
animation: scaleIn 0.6s ease-out;
```

### Rotate
```css
animation: rotate 20s linear infinite;
```

### Spin
```css
animation: spin 1s linear infinite;
```

---

## Grid Responsivo

### 4 Colunas (Desktop)
```css
grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
```

### 2 Colunas (Tablet)
```css
@media (max-width: 768px) {
    grid-template-columns: repeat(2, 1fr);
}
```

### 1 Coluna (Mobile)
```css
@media (max-width: 480px) {
    grid-template-columns: 1fr;
}
```

---

## Compatibilidade

✅ Chrome 90+
✅ Firefox 88+
✅ Safari 14+
✅ Edge 90+
✅ Mobile Chrome
✅ Mobile Safari

---

**Versão:** 1.0
**Data:** Janeiro 2026
**Status:** ✅ Ativo
