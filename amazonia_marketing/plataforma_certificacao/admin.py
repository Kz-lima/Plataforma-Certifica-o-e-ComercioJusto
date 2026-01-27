from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.utils.html import format_html
from .models import CustomUser, PerfilProduto, PerfilEmpresa, Certificacoes, Produtos


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

# Essa configuração permite que os campos de usuário sejam mostrados
# na tabela usuários ao criar um cadastro.
class ProdutorInline(admin.StackedInline):
    model = PerfilProduto
    can_delete = False
    verbose_name_plural = 'Perfil de Produtor'
    
class EmpresaInline(admin.StackedInline):
    model = PerfilEmpresa
    can_delete = False
    verbose_name_plural = 'Perfil de Empresa'

# Personalizando o painel administrativo do usuário 'CustomUser'
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'tipo_usuario', 'is_staff')
    # Filtros laterais adicionados
    list_filter = ('tipo_usuario', 'is_staff', 'is_superuser')
    # Adicionando os inlines criados em cima
    inlines = (ProdutorInline, EmpresaInline)
    # Configurando campos que aparecem ao editar
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Extras', {'fields': ('tipo_usuario',)}),
    )
    
    # Configurações dos campos que aparecem ao criar
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Extras', {'fields': ('tipo_usuario',)}),
    )

# Registra o usuário com a configuração avançada acima
admin.site.register(CustomUser, CustomUserAdmin)



# ============================================================================
# ADMIN PARA NEGÓCIO
# ============================================================================

# Registros para os modelos de negócio
@admin.register(Certificacoes)
class CertificacoesAdmin(admin.ModelAdmin):
    list_display = ('id_certificacao', 'produto', 'status_certificacao', 'data_envio', 'admin_responsavel')
    list_filter = ('status_certificacao', 'data_envio')
    search_fields = ('produto__nome', 'admin_responsavel__username')
    readonly_fields = ('id_certificacao', 'data_envio', 'data_resposta')
    fieldsets = (
        ('Produto', {
            'fields': ('produto',)
        }),
        ('Documentação', {
            'fields': ('texto_autodeclaracao', 'arquivo_autodeclaracao')
        }),
        ('Status e Datas', {
            'fields': ('status_certificacao', 'data_envio', 'data_resposta')
        }),
        ('Responsável', {
            'fields': ('admin_responsavel',)
        }),
    )


@admin.register(Produtos)
class ProdutosAdmin(admin.ModelAdmin):
    list_display = ('id_produto', 'nome', 'categoria', 'status_estoque', 'preco', 'usuario')
    list_filter = ('status_estoque', 'categoria')
    search_fields = ('nome', 'categoria', 'usuario__username')
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

    
