"""
Script para verificar usuários empresa sem perfil Empresa
"""
import os
import sys
import django

sys.path.insert(0, r'c:\Github\Plataforma-Certificacao-e-ComercioJusto\amazonia_marketing')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amazonia_marketing.settings')
django.setup()

from plataforma_certificacao.models import UsuarioBase, Empresa

print("\n🔍 Buscando usuários empresa sem perfil Empresa...")

usuarios_empresa = UsuarioBase.objects.filter(tipo='empresa')
print(f"\nTotal de usuários tipo 'empresa': {usuarios_empresa.count()}")

for usuario in usuarios_empresa:
    print(f"\n📋 Usuário: {usuario.nome} ({usuario.email})")
    print(f"   ID: {usuario.id_usuario}")
    print(f"   Tipo: {usuario.tipo}")
    
    try:
        empresa = usuario.empresa_profile
        print(f"   ✅ Possui perfil Empresa: {empresa.razao_social}")
        print(f"      CNPJ: {empresa.cnpj}")
    except Empresa.DoesNotExist:
        print(f"   ❌ SEM PERFIL EMPRESA! <-- PROBLEMA ENCONTRADO")
        print(f"   🔧 Criando perfil automaticamente...")
        
        # Tentar criar perfil vazio
        try:
            empresa = Empresa.objects.create(usuario=usuario)
            print(f"   ✅ Perfil criado com sucesso!")
        except Exception as e:
            print(f"   ❌ Erro ao criar perfil: {e}")

print("\n✅ Verificação concluída!")
