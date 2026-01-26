# Script de Instalação e Configuração - Login com Google
# Execute este script para instalar e configurar tudo necessário

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Instalação django-allauth + Google" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Ativar ambiente virtual
Write-Host "[1/5] Ativando ambiente virtual..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# 2. Instalar django-allauth
Write-Host "[2/5] Instalando django-allauth..." -ForegroundColor Yellow
pip install django-allauth

# 3. Executar migrações
Write-Host "[3/5] Executando migrações do banco de dados..." -ForegroundColor Yellow
python manage.py migrate

# 4. Verificar se há erros
Write-Host "[4/5] Verificando configurações..." -ForegroundColor Yellow
python manage.py check

# 5. Criar superusuário (opcional)
Write-Host "[5/5] Deseja criar um superusuário agora? (S/N)" -ForegroundColor Green
$resposta = Read-Host
if ($resposta -eq "S" -or $resposta -eq "s") {
    python manage.py createsuperuser
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   ✅ Instalação Concluída!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 PRÓXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1️⃣  Criar credenciais no Google Cloud Console:" -ForegroundColor Yellow
Write-Host "   https://console.cloud.google.com/" -ForegroundColor Gray
Write-Host ""
Write-Host "2️⃣  Iniciar o servidor:" -ForegroundColor Yellow
Write-Host "   python manage.py runserver" -ForegroundColor Gray
Write-Host ""
Write-Host "3️⃣  Acessar o admin:" -ForegroundColor Yellow
Write-Host "   http://localhost:8000/admin" -ForegroundColor Gray
Write-Host ""
Write-Host "4️⃣  Configurar Social Application no Django Admin:" -ForegroundColor Yellow
Write-Host "   - Sites > Editar site > localhost:8000" -ForegroundColor Gray
Write-Host "   - Social applications > Add > Google OAuth" -ForegroundColor Gray
Write-Host "   - Adicionar Client ID e Secret do Google" -ForegroundColor Gray
Write-Host ""
Write-Host "5️⃣  Testar login:" -ForegroundColor Yellow
Write-Host "   http://localhost:8000/registration/login/" -ForegroundColor Gray
Write-Host ""
Write-Host "📖 Consulte o GUIA_LOGIN_GOOGLE.md para detalhes completos" -ForegroundColor Magenta
Write-Host ""
