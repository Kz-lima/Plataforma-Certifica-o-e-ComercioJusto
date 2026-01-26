"""
Script de teste para verificar o fluxo de cadastro de empresa
"""
import os
import sys
import django

# Configura o ambiente Django
sys.path.insert(0, r'c:\Github\Plataforma-Certificacao-e-ComercioJusto\amazonia_marketing')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amazonia_marketing.settings')
django.setup()

from plataforma_certificacao.models import UsuarioBase, Empresa
from django.contrib.auth import get_user_model

# Limpar dados de teste antigos
print("🧹 Limpando dados de teste antigos...")
UsuarioBase.objects.filter(email='teste_empresa@email.com').delete()

# Teste 1: Criar um usuário empresa manualmente
print("\n📝 Teste 1: Criando usuário empresa...")
try:
    usuario = UsuarioBase.objects.create(
        email='teste_empresa@email.com',
        nome='Empresa de Teste',
        telefone='(11) 99999-9999',
        endereco='Rua Teste, 123',
        tipo='empresa'
    )
    usuario.set_password('senha123')
    usuario.save()
    print(f"✅ UsuarioBase criado: {usuario.nome} (ID: {usuario.id_usuario})")
    
    # Criar Django User
    UserModel = get_user_model()
    django_user, created = UserModel.objects.get_or_create(
        username=usuario.email,
        defaults={'email': usuario.email}
    )
    django_user.set_password('senha123')
    django_user.save()
    usuario.user = django_user
    usuario.save()
    print(f"✅ Django User criado/atualizado: {django_user.username}")
    
    # Criar perfil Empresa
    empresa, created = Empresa.objects.get_or_create(
        usuario=usuario,
        defaults={
            'cnpj': '12345678000199',
            'razao_social': 'Empresa de Teste LTDA'
        }
    )
    print(f"✅ Empresa criada: {empresa.razao_social} (CNPJ: {empresa.cnpj})")
    
except Exception as e:
    print(f"❌ Erro ao criar usuário: {e}")
    import traceback
    traceback.print_exc()

# Teste 2: Verificar se o perfil pode ser acessado
print("\n🔍 Teste 2: Verificando acesso ao perfil...")
try:
    usuario = UsuarioBase.objects.get(email='teste_empresa@email.com')
    print(f"✅ UsuarioBase encontrado: {usuario.nome}")
    
    # Tentar acessar o perfil empresa
    empresa_profile = usuario.empresa_profile
    print(f"✅ Perfil empresa acessado: {empresa_profile.razao_social}")
    print(f"   - CNPJ: {empresa_profile.cnpj}")
    print(f"   - Status: {empresa_profile.status_verificacao}")
    
except Empresa.DoesNotExist:
    print("❌ ERRO: Perfil de empresa não encontrado!")
except Exception as e:
    print(f"❌ Erro ao acessar perfil: {e}")
    import traceback
    traceback.print_exc()

# Teste 3: Verificar relacionamento reverso
print("\n🔄 Teste 3: Verificando relacionamento reverso...")
try:
    empresa = Empresa.objects.get(cnpj='12345678000199')
    print(f"✅ Empresa encontrada: {empresa.razao_social}")
    print(f"   - Usuário vinculado: {empresa.usuario.nome}")
    print(f"   - Email: {empresa.usuario.email}")
    print(f"   - Tipo: {empresa.usuario.tipo}")
    
except Exception as e:
    print(f"❌ Erro: {e}")

print("\n✅ Testes concluídos!")
print("\n📋 Resumo:")
print(f"   - Total de usuários empresa: {UsuarioBase.objects.filter(tipo='empresa').count()}")
print(f"   - Total de perfis Empresa: {Empresa.objects.count()}")
