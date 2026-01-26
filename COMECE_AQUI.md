# 🚀 COMEÇAR AGORA - 3 Passos Simples

## ✅ Status: 95% Completo

O código está pronto! Falta apenas configurar as credenciais do Google (5 minutos).

---

## 📋 Passo 1: Criar Credenciais Google (5 min)

### 1.1 Acesse o Google Cloud Console
🔗 https://console.cloud.google.com/

### 1.2 Crie/Selecione Projeto
- Clique em **Criar Projeto**
- Nome: "Amazonia Marketing"
- Clique em **Criar**

### 1.3 Configure Tela de Consentimento OAuth
1. Vá em: **APIs e Serviços** > **Tela de consentimento OAuth**
2. Escolha: **Externo**
3. Preencha:
   - **Nome do app**: Amazônia Marketing
   - **Email de suporte**: seu@email.com
   - **Domínios autorizados**: `localhost`
   - **Email do desenvolvedor**: seu@email.com
4. Clique em **SALVAR E CONTINUAR**
5. Pule as seções "Escopos" e "Usuários de teste"
6. Clique em **VOLTAR AO PAINEL**

### 1.4 Criar Credenciais OAuth 2.0
1. Vá em: **APIs e Serviços** > **Credenciais**
2. Clique em: **+ CRIAR CREDENCIAIS**
3. Escolha: **ID do cliente OAuth**
4. Tipo: **Aplicativo da Web**
5. Preencha exatamente:

**Nome:**
```
Amazonia Marketing
```

**Origens JavaScript autorizadas:**
```
http://localhost:8000
http://127.0.0.1:8000
```

**URIs de redirecionamento autorizados:**
```
http://localhost:8000/accounts/google/login/callback/
http://127.0.0.1:8000/accounts/google/login/callback/
```

6. Clique em **CRIAR**
7. **⚠️ COPIE E SALVE**:
   - Client ID (começa com números e termina em `.apps.googleusercontent.com`)
   - Client Secret (string aleatória)

---

## 📋 Passo 2: Configurar Django Admin (3 min)

### 2.1 Iniciar Servidor
```bash
cd amazonia_marketing
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

### 2.2 Acessar Admin
🔗 http://localhost:8000/admin

**Login:**
- Se já tem superusuário: use suas credenciais
- Se não tem: Abra outro terminal e execute:
  ```bash
  python manage.py createsuperuser
  ```

### 2.3 Configurar Site
1. No admin, vá em: **Sites**
2. Clique no site existente (example.com)
3. Edite:
   - **Domain name**: `localhost:8000`
   - **Display name**: `Amazônia Marketing`
4. Clique em **Save**

### 2.4 Adicionar Social Application
1. No admin, vá em: **Social accounts** > **Social applications**
2. Clique em: **Add Social Application** (botão verde no canto superior direito)
3. Preencha:

| Campo | Valor |
|-------|-------|
| **Provider** | Google |
| **Name** | Google OAuth |
| **Client id** | Cole o Client ID copiado do Google |
| **Secret key** | Cole o Client Secret copiado do Google |
| **Key** | Deixe em branco |

4. Em **Sites**:
   - Selecione "localhost:8000" na caixa **Available sites**
   - Clique na seta → para mover para **Chosen sites**
5. Clique em **SAVE**

---

## 📋 Passo 3: Testar (1 min)

### 3.1 Fazer Logout do Admin
- Clique em **LOG OUT** no canto superior direito

### 3.2 Testar Login Social
1. Acesse: http://localhost:8000/registration/login/
2. Você verá 3 opções:
   - **Formulário de login** tradicional (email/senha)
   - **OU**
   - **Botão "Entrar com Google"** (branco com logo do Google)
3. Clique no botão **"Entrar com Google"**
4. Faça login com sua conta Google
5. Escolha se você é **Produtor** 🌱 ou **Empresa** 🏢
6. ✅ **Sucesso!** Você será redirecionado para o dashboard

---

## 🎉 Pronto!

### O que aconteceu por trás:
1. ✅ Usuário autenticado via Google OAuth 2.0
2. ✅ Email e nome buscados do Google
3. ✅ Registro criado em `usuariobase`
4. ✅ Perfil criado em `produtor` ou `empresa`
5. ✅ Login automático realizado
6. ✅ Redirecionamento inteligente para dashboard

---

## 🐛 Se algo der errado:

### Erro: "redirect_uri_mismatch"
- Verifique se copiou os URIs **EXATAMENTE** como mostrado acima
- Deve incluir `/accounts/google/login/callback/` no final

### Erro: "SocialApp matching query does not exist"
- Verifique se adicionou a Social Application no Admin
- Verifique se moveu o site para "Chosen sites"

### Erro: "Site matching query does not exist"
- Verifique se editou o site para `localhost:8000`

### Erro: Página em branco ou erro 500
- Verifique os logs no terminal onde o servidor está rodando
- Use `python manage.py runserver` (não feche o terminal)

---

## 📚 Arquivos de Referência

- **Guia Completo**: `GUIA_LOGIN_GOOGLE.md`
- **Resumo da Implementação**: `IMPLEMENTACAO_COMPLETA.md`
- **Este arquivo**: `COMECE_AQUI.md`

---

## 💡 Dicas

- Mantenha as credenciais do Google **em segredo**
- Use uma **aba anônima** se tiver problemas de cache
- O primeiro login sempre pede para escolher tipo
- Logins seguintes são automáticos

---

**Qualquer dúvida, consulte os arquivos de referência!** 📖
