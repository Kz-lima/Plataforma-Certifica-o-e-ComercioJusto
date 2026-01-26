from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.utils.html import format_html
from .models import UsuarioBase, Produtor, Empresa, Certificacoes, Marketplace, Produtos


# ============================================================================
# CONFIGURAÇÃO DE GRUPOS (Segurança e Permissões)
# ============================================================================

class CustomGroupAdmin(BaseGroupAdmin):
    """Customização para admin de grupos com melhor interface."""
    list_display = ('name', 'permissions_count')
    
    def permissions_count(self, obj):
        return obj.permissions.count()
    permissions_count.short_description = 'Quantidade de Permissões'


# Re-registrar Group com customizações
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass

admin.site.register(Group, CustomGroupAdmin)


# ============================================================================
# ADMIN PARA USUÁRIOS
# ============================================================================

# Registros para os modelos de usuário
@admin.register(UsuarioBase)
class UsuarioBaseAdmin(admin.ModelAdmin):
    list_display = ('id_usuario', 'nome', 'email', 'tipo', 'telefone', 'user_vinculado')
    list_filter = ('tipo',)
    search_fields = ('nome', 'email')
    ordering = ('id_usuario',)
    readonly_fields = ('id_usuario',)
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('id_usuario', 'user', 'nome', 'email', 'tipo')
        }),
        ('Informações de Contato', {
            'fields': ('telefone', 'endereco')
        }),
    )
    
    def user_vinculado(self, obj):
        """Indica visualmente se está vinculado a um User do Django."""
        if obj.user:
            return format_html('<span style="color: green;">✓ Vinculado</span>')
        return format_html('<span style="color: red;">✗ Não vinculado</span>')
    user_vinculado.short_description = 'User Django'
    
    def get_readonly_fields(self, request, obj=None):
        """ID e tipo não podem ser editados depois de criado."""
        if obj:
            return ('id_usuario', 'tipo', 'user')
        return ('id_usuario',)


@admin.register(Produtor)
class ProdutorAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'cpf_masked', 'data_criacao')
    search_fields = ('usuario__nome', 'cpf')
    list_filter = ('data_criacao',)
    readonly_fields = ('data_criacao',)
    fieldsets = (
        ('Usuário', {
            'fields': ('usuario',)
        }),
        ('Dados Pessoais', {
            'fields': ('cpf',)
        }),
        ('Auditoria', {
            'fields': ('data_criacao',)
        }),
    )
    
    def cpf_masked(self, obj):
        """Exibe CPF mascarado por segurança nos listados."""
        if obj.cpf:
            return f"***-{obj.cpf[-2:]}"
        return "Não informado"
    cpf_masked.short_description = 'CPF'


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'cnpj_masked', 'razao_social', 'data_criacao')
    search_fields = ('usuario__nome', 'cnpj', 'razao_social')
    list_filter = ('data_criacao',)
    readonly_fields = ('data_criacao',)
    fieldsets = (
        ('Usuário', {
            'fields': ('usuario',)
        }),
        ('Dados da Empresa', {
            'fields': ('cnpj', 'razao_social')
        }),
        ('Auditoria', {
            'fields': ('data_criacao',)
        }),
    )
    
    def cnpj_masked(self, obj):
        """Exibe CNPJ mascarado por segurança nos listados."""
        if obj.cnpj:
            return f"****-{obj.cnpj[-2:]}"
        return "Não informado"
    cnpj_masked.short_description = 'CNPJ'


# ============================================================================
# ADMIN PARA NEGÓCIO
# ============================================================================

# Registros para os modelos de negócio
@admin.register(Certificacoes)
class CertificacoesAdmin(admin.ModelAdmin):
    list_display = ('id_certificacao', 'produto', 'status_certificacao', 'data_envio', 'admin_responsavel')
    list_filter = ('status_certificacao', 'data_envio')
    search_fields = ('produto__nome', 'admin_responsavel__nome')
    readonly_fields = ('id_certificacao', 'data_envio', 'data_resposta')
    fieldsets = (
        ('Produto', {
            'fields': ('produto',)
        }),
        ('Documentação', {
            'fields': ('documento', 'texto_autodeclaracao')
        }),
        ('Status e Datas', {
            'fields': ('status_certificacao', 'data_envio', 'data_resposta')
        }),
        ('Responsável', {
            'fields': ('admin_responsavel',)
        }),
    )


@admin.register(Marketplace)
class MarketplaceAdmin(admin.ModelAdmin):
    list_display = ('id_anuncio', 'produto', 'plataforma', 'data_geracao')
    list_filter = ('plataforma', 'data_geracao')
    search_fields = ('produto__nome', 'plataforma')
    readonly_fields = ('data_geracao',)


@admin.register(Produtos)
class ProdutosAdmin(admin.ModelAdmin):
    list_display = ('id_produto', 'nome', 'categoria', 'status_estoque', 'preco', 'usuario')
    list_filter = ('status_estoque', 'categoria')
    search_fields = ('nome', 'categoria', 'usuario__nome')
    readonly_fields = ('id_produto',)
    fieldsets = (
        ('Identificação', {
            'fields': ('nome', 'categoria')
        }),
        ('Descrição e Imagem', {
            'fields': ('descricao', 'imagem')
        }),
        ('Informações Comerciais', {
            'fields': ('preco', 'status_estoque')
        }),
        ('Propriedade', {
            'fields': ('usuario',)
        }),
    )
