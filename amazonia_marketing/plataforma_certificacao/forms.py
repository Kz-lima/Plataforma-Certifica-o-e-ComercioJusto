from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import Produtos, UsuarioBase, Produtor, Empresa
from django.contrib.auth.models import User
from .models import CustomUser, PerfilProduto, PerfilEmpresa, Produtos, Certificacoes
from django.contrib.auth.forms import UserCreationForm

# --- Princípio DRY - Don't Repeat Yourself ---
def validar_arquivo_seguro(arquivo):
    """
    Função isolada para validar arquivos. 
    Pode ser reutilizada em qualquer formulário do sistema.
    """
    if not arquivo:
        return arquivo

    # 1. Validação de Tamanho (Regra de Negócio: Máx 5MB)
    limite_mb = 5
    if arquivo.size > limite_mb * 1024 * 1024: # Convertendo MB para Bytes
        raise ValidationError(f'O arquivo não pode exceder {limite_mb} MB.')
    
    # 2. Validação de Extensão (Segurança básica)
    extensoes_permitidas = ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png']
    # Pega o nome "documento.pdf", separa no ponto e pega a última parte "pdf"
    extensao = arquivo.name.split('.')[-1].lower()
    # Verifica a lista de extensões permitidas e retorna erro se não estiver lá
    if extensao not in extensoes_permitidas:
        raise ValidationError(f'Extensão não permitida. Use: {", ".join(extensoes_permitidas)}')

    # 3. Validação de Tipo MIME (Segurança avançada)
    # Verifica se a constante existe no settings para evitar erro se esquecermos de configurar
    if hasattr(settings, 'ALLOWED_UPLOAD_MIME_TYPES'):
        # arquivo.content_type é o tipo real do arquivo (ex: 'application/pdf')
        if arquivo.content_type not in settings.ALLOWED_UPLOAD_MIME_TYPES:
            raise ValidationError('Tipo de arquivo inválido (MIME type rejeitado).')
    
    return arquivo

# --- FORMULÁRIO 1: CADASTRO DE PRODUTO ---
class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produtos
        fields = ['nome', 'categoria', 'descricao', 'preco', 'imagem']
        # Design System: Mantemos a classe 'form-input' para consistência visual (garantindo a identidade do cliente)
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Mel de Jataí'}),
            'categoria': forms.TextInput(attrs={'class': 'form-input'}),
            'descricao': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'preco': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
        }
    
    # Aplicamos a validação de segurança também na foto do produto!
    def clean_imagem(self):
        imagem = self.cleaned_data.get('imagem')
        return validar_arquivo_seguro(imagem)

class EditarPerfilProdutorForm(forms.ModelForm):
    # Campos que queremos editar
    first_name = forms.CharField(label='Nome da Pessoa Física', widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-input'}))
    
    # Campos do perfil
    class Meta:
        model = PerfilProduto
        fields = ['nome', 'telefon', 'endereco', 'bio']
        
        labels = {
            'nome': 'Nome da Fazenda / Negócio',
            'endereco': 'Endereço da Propriedade',
            'telefon': 'Telefone'
        }
        
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-input'}),
            'telefon': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '(XX) XXXXX-XXXX'}),
            'endereco': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'bio': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Fale sobre o que torna seus produtos diferentes.'}),
        }
        
# --- FORMULÁRIO 2: CERTIFICAÇÃO (Entrega da Sprint 4) ---
class ProdutoComAutodeclaracaoForm(forms.Form): # Formulário híbrido, por isso não herda ModelForm
    # Campo 1: Select (Menu) para escolher qual produto certificar
    produto = forms.ModelChoiceField(
        queryset=Produtos.objects.none(), # Segurança: Começa vazio, a View vai preencher
        label='Selecione o Produto',
        empty_label='-- Escolha um produto --',
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    
    # Campo 2: Texto livre
    texto_autodeclaracao = forms.CharField(
        required=False, # Opcional (pode mandar só arquivo)
        label='Texto da Autodeclaração',
        widget=forms.Textarea(attrs={
            'class': 'form-input', 
            'rows': 5,
            'placeholder': 'Escreva aqui sua declaração se não tiver o arquivo PDF...'
        })
    )
    
    # Campo 3: Upload do arquivo
    arquivo_autodeclaracao = forms.FileField(
        required=False, # Opcional (pode mandar só texto)
        label='Arquivo (PDF/Foto)',
        help_text='Máximo 5MB.',
        widget=forms.FileInput(attrs={'class': 'form-input'})
    )

    # Validação Específica: Chama nossa função validar_arquivo_seguro (garante o DRY)
    def clean_arquivo_autodeclaracao(self):
        arquivo = self.cleaned_data.get('arquivo_autodeclaracao')
        return validar_arquivo_seguro(arquivo)

    # Validação Geral: (Cross-field validation - Validação cruzada)
    def clean(self):
from .models import Certificacoes, Produtos
from django.core.exceptions import ValidationError
from django.conf import settings


class CertificacaoForm(forms.ModelForm):
    """Formulário para cadastro de certificação com upload de autodeclaração"""
    
    class Meta:
        model = Certificacoes
        fields = ['texto_autodeclaracao', 'arquivo_autodeclaracao']
        widgets = {
            'texto_autodeclaracao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Digite aqui o texto da sua autodeclaração (opcional)',
                'style': 'font-size: 14px;'
            }),
            'arquivo_autodeclaracao': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png',
                'id': 'arquivo_input'
            }),
        }
        labels = {
            'texto_autodeclaracao': 'Texto da Autodeclaração',
            'arquivo_autodeclaracao': 'Arquivo de Autodeclaração (PDF, DOC, DOCX, JPG, PNG)',
        }
        help_texts = {
            'arquivo_autodeclaracao': 'Máximo de 5MB. Formatos aceitos: PDF, DOC, DOCX, JPG, PNG',
        }

    def clean_arquivo_autodeclaracao(self):
        """Validação customizada do arquivo"""
        arquivo = self.cleaned_data.get('arquivo_autodeclaracao')
        
        if arquivo:
            # Validar tamanho
            if arquivo.size > 5242880:  # 5MB
                raise ValidationError('O arquivo não pode exceder 5MB.')
            
            # Validar extensão
            extensoes_permitidas = ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png']
            extensao_arquivo = arquivo.name.split('.')[-1].lower()
            
            if extensao_arquivo not in extensoes_permitidas:
                raise ValidationError(
                    f'Tipo de arquivo não permitido. Aceitos: {", ".join(extensoes_permitidas)}'
                )
            
            # Validar tipo MIME
            tipos_mime_permitidos = settings.ALLOWED_UPLOAD_MIME_TYPES
            if arquivo.content_type not in tipos_mime_permitidos:
                raise ValidationError('Tipo MIME do arquivo não é permitido.')
        
        return arquivo

    def clean(self):
        """Validação geral do formulário"""
        cleaned_data = super().clean()
        texto = cleaned_data.get('texto_autodeclaracao')
        arquivo = cleaned_data.get('arquivo_autodeclaracao')
        
        # Regra de Negócio: Não pode enviar tudo vazio
        if not texto and not arquivo:
            raise ValidationError('Por favor, preencha o texto OU envie um arquivo.')

        return cleaned_data


# --- FORMULÁRIO 3: CADASTRO DE PRODUTOR ---
class CadastroProdutorForm(forms.ModelForm):
    """Formulário para cadastro de novos produtores"""
    
    # Campos adicionais não presentes no modelo
    senha = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Senha'}),
        min_length=6,
        help_text='Mínimo 6 caracteres'
    )
    confirmar_senha = forms.CharField(
        label='Confirmar Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirme a senha'})
    )
    cpf = forms.CharField(
        label='CPF',
        max_length=14,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '000.000.000-00'})
    )
    
    class Meta:
        model = UsuarioBase
        fields = ['nome', 'email', 'telefone', 'endereco']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nome completo'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'seu@email.com'}),
            'telefone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '(00) 00000-0000'}),
            'endereco': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Endereço completo'}),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if UsuarioBase.objects.filter(email__iexact=email).exists():
            raise ValidationError('Este email já está cadastrado.')
        return email.lower()  # Tratamento case insensitive
    
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        # Remove formatação
        cpf_numeros = ''.join(filter(str.isdigit, cpf))
        if len(cpf_numeros) != 11:
            raise ValidationError('CPF deve ter 11 dígitos.')
        if Produtor.objects.filter(cpf=cpf_numeros).exists():
            raise ValidationError('Este CPF já está cadastrado.')
        return cpf_numeros
    
    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get('senha')
        confirmar_senha = cleaned_data.get('confirmar_senha')
        
        if senha and confirmar_senha and senha != confirmar_senha:
            raise ValidationError('As senhas não coincidem.')
        
        return cleaned_data
    
    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.tipo = 'produtor'  # Define tipo automaticamente
        
        # Hasheia a senha antes de salvar
        usuario.set_password(self.cleaned_data['senha'])
        
        if commit:
            usuario.save()
            # Cria/associa usuário Django para funcionar com login_required
            UserModel = get_user_model()
            auth_user, _ = UserModel.objects.get_or_create(
                username=usuario.email,
                defaults={'email': usuario.email}
            )
            auth_user.set_password(self.cleaned_data['senha'])
            auth_user.save()
            if usuario.user_id != auth_user.id:
                usuario.user = auth_user
                usuario.save(update_fields=['user'])

            # Criar perfil de produtor (ou atualizar se já existir)
            produtor, created = Produtor.objects.get_or_create(
                usuario=usuario,
                defaults={'cpf': self.cleaned_data['cpf']}
            )
            # Se já existia, atualiza o CPF
            if not created:
                produtor.cpf = self.cleaned_data['cpf']
                produtor.save()
        
        return usuario


# --- FORMULÁRIO 4: CADASTRO DE EMPRESA ---
class CadastroEmpresaForm(forms.ModelForm):
    """Formulário para cadastro de novas empresas"""
    
    # Campos adicionais não presentes no modelo
    senha = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Senha'}),
        min_length=6,
        help_text='Mínimo 6 caracteres'
    )
    confirmar_senha = forms.CharField(
        label='Confirmar Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirme a senha'})
    )
    cnpj = forms.CharField(
        label='CNPJ',
        max_length=18,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '00.000.000/0000-00'})
    )
    razao_social = forms.CharField(
        label='Razão Social',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nome da empresa'})
    )
    
    class Meta:
        model = UsuarioBase
        fields = ['nome', 'email', 'telefone', 'endereco']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nome do responsável'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'contato@empresa.com'}),
            'telefone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '(00) 0000-0000'}),
            'endereco': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Endereço da empresa'}),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if UsuarioBase.objects.filter(email__iexact=email).exists():
            raise ValidationError('Este email já está cadastrado.')
        return email.lower()  # Tratamento case insensitive
    
    def clean_cnpj(self):
        cnpj = self.cleaned_data.get('cnpj')
        # Remove formatação
        cnpj_numeros = ''.join(filter(str.isdigit, cnpj))
        if len(cnpj_numeros) != 14:
            raise ValidationError('CNPJ deve ter 14 dígitos.')
        if Empresa.objects.filter(cnpj=cnpj_numeros).exists():
            raise ValidationError('Este CNPJ já está cadastrado.')
        return cnpj_numeros
    
    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get('senha')
        confirmar_senha = cleaned_data.get('confirmar_senha')
        
        if senha and confirmar_senha and senha != confirmar_senha:
            raise ValidationError('As senhas não coincidem.')
        
        return cleaned_data
    
    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.tipo = 'empresa'  # Define tipo automaticamente
        
        # Hasheia a senha antes de salvar
        usuario.set_password(self.cleaned_data['senha'])
        
        if commit:
            usuario.save()
            # Cria/associa usuário Django para funcionar com login_required
            UserModel = get_user_model()
            auth_user, _ = UserModel.objects.get_or_create(
                username=usuario.email,
                defaults={'email': usuario.email}
            )
            auth_user.set_password(self.cleaned_data['senha'])
            auth_user.save()
            if usuario.user_id != auth_user.id:
                usuario.user = auth_user
                usuario.save(update_fields=['user'])

            # Criar perfil de empresa (ou atualizar se já existir)
            empresa, created = Empresa.objects.get_or_create(
                usuario=usuario,
                defaults={
                    'cnpj': self.cleaned_data['cnpj'],
                    'razao_social': self.cleaned_data['razao_social']
                }
            )
            # Se já existia, atualiza os dados
            if not created:
                empresa.cnpj = self.cleaned_data['cnpj']
                empresa.razao_social = self.cleaned_data['razao_social']
                empresa.save()
        
        return usuario


# --- FORMULÁRIO 5: CONFIGURAÇÃO DE PERFIL PRODUTOR ---
class ProdutorConfigForm(forms.ModelForm):
    """Formulário para edição de perfil do produtor"""
    
    class Meta:
        model = Produtor
        fields = ['bio', 'foto_perfil', 'cidade', 'estado', 'cep', 'whatsapp', 'instagram', 'facebook']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-input', 
                'rows': 5,
                'placeholder': 'Conte sua história, sua missão e valores...'
            }),
            'foto_perfil': forms.FileInput(attrs={'class': 'form-input', 'accept': 'image/*'}),
            'cidade': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Cidade'}),
            'estado': forms.Select(attrs={'class': 'form-input'}, choices=[
                ('', 'Selecione o estado'),
                ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'),
                ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'),
                ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'),
                ('MG', 'Minas Gerais'), ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'),
                ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
                ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'),
                ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins')
            ]),
            'cep': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '00000-000'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '(00) 00000-0000'}),
            'instagram': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '@seuusuario'}),
            'facebook': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'facebook.com/seuperfil'}),
        }
    
    def clean_foto_perfil(self):
        foto = self.cleaned_data.get('foto_perfil')
        if foto:
            return validar_arquivo_seguro(foto)
        return foto


class UsuarioBaseConfigForm(forms.ModelForm):
    """Formulário para dados básicos do usuário"""
    
    class Meta:
        model = UsuarioBase
        fields = ['nome', 'email', 'telefone', 'endereco']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nome completo'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'seu@email.com'}),
            'telefone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '(00) 00000-0000'}),
            'endereco': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Endereço completo'}),
        }


# --- FORMULÁRIO 6: CONFIGURAÇÃO DE PERFIL EMPRESA ---
class EmpresaConfigForm(forms.ModelForm):
    """Formulário para edição de perfil da empresa com validação de CNPJ"""
    
    class Meta:
        model = Empresa
        fields = [
            'razao_social', 'nome_fantasia', 'cnpj', 'inscricao_estadual',
            'documento_contrato_social', 'documento_cnpj', 'documento_alvara',
            'endereco_comercial', 'cidade', 'estado', 'cep',
            'telefone_comercial', 'site', 'descricao_empresa', 'logo'
        ]
        widgets = {
            'razao_social': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Razão Social'}),
            'nome_fantasia': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nome Fantasia'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '00.000.000/0000-00'}),
            'inscricao_estadual': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Inscrição Estadual'}),
            'documento_contrato_social': forms.FileInput(attrs={'class': 'form-input', 'accept': '.pdf'}),
            'documento_cnpj': forms.FileInput(attrs={'class': 'form-input', 'accept': '.pdf'}),
            'documento_alvara': forms.FileInput(attrs={'class': 'form-input', 'accept': '.pdf'}),
            'endereco_comercial': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Endereço comercial'}),
            'cidade': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Cidade'}),
            'estado': forms.Select(attrs={'class': 'form-input'}, choices=[
                ('', 'Selecione o estado'),
                ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'),
                ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'),
                ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'),
                ('MG', 'Minas Gerais'), ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'),
                ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
                ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'),
                ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins')
            ]),
            'cep': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '00000-000'}),
            'telefone_comercial': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '(00) 0000-0000'}),
            'site': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://seusite.com'}),
            'descricao_empresa': forms.Textarea(attrs={
                'class': 'form-input', 
                'rows': 5,
                'placeholder': 'Descreva sua empresa, atividades e diferenciais...'
            }),
            'logo': forms.FileInput(attrs={'class': 'form-input', 'accept': 'image/*'}),
        }
    
    def clean_cnpj(self):
        cnpj = self.cleaned_data.get('cnpj')
        if cnpj:
            # Remove formatação
            cnpj_numeros = ''.join(filter(str.isdigit, cnpj))
            if len(cnpj_numeros) != 14:
                raise ValidationError('CNPJ deve ter 14 dígitos.')
            
            # Verifica se CNPJ já existe (exceto para o próprio registro)
            qs = Empresa.objects.filter(cnpj=cnpj_numeros)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError('Este CNPJ já está cadastrado.')
            
            return cnpj_numeros
        return cnpj
    
    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if logo:
            return validar_arquivo_seguro(logo)
        return logo
    
    def clean_documento_contrato_social(self):
        doc = self.cleaned_data.get('documento_contrato_social')
        if doc:
            return validar_arquivo_seguro(doc)
        return doc
    
    def clean_documento_cnpj(self):
        doc = self.cleaned_data.get('documento_cnpj')
        if doc:
            return validar_arquivo_seguro(doc)
        return doc
    
    def clean_documento_alvara(self):
        doc = self.cleaned_data.get('documento_alvara')
        if doc:
            return validar_arquivo_seguro(doc)
        return doc


# --- FORMULÁRIO 7: CERTIFICAÇÃO COM UPLOAD MÚLTIPLO ---
class CertificacaoMultiplaForm(forms.Form):
    """Formulário para solicitação de certificação com até 3 arquivos"""
    
    produto = forms.ModelChoiceField(
        queryset=Produtos.objects.none(),
        label='Selecione o Produto',
        empty_label='-- Escolha um produto --',
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    
    texto_autodeclaracao = forms.CharField(
        required=False,
        label='Texto da Autodeclaração',
        widget=forms.Textarea(attrs={
            'class': 'form-input', 
            'rows': 5,
            'placeholder': 'Descreva as práticas sustentáveis, origem dos produtos, etc...'
        })
    )
    
    documento_1 = forms.FileField(
        required=False,
        label='Documento 1 (Obrigatório)',
        help_text='PDF, DOC, DOCX, JPG, PNG - Máximo 5MB',
        widget=forms.FileInput(attrs={'class': 'form-input', 'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'})
    )
    
    documento_2 = forms.FileField(
        required=False,
        label='Documento 2 (Opcional)',
        help_text='PDF, DOC, DOCX, JPG, PNG - Máximo 5MB',
        widget=forms.FileInput(attrs={'class': 'form-input', 'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'})
    )
    
    documento_3 = forms.FileField(
        required=False,
        label='Documento 3 (Opcional)',
        help_text='PDF, DOC, DOCX, JPG, PNG - Máximo 5MB',
        widget=forms.FileInput(attrs={'class': 'form-input', 'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'})
    )
    
    def clean_documento_1(self):
        arquivo = self.cleaned_data.get('documento_1')
        return validar_arquivo_seguro(arquivo)
    
    def clean_documento_2(self):
        arquivo = self.cleaned_data.get('documento_2')
        if arquivo:
            return validar_arquivo_seguro(arquivo)
        return arquivo
    
    def clean_documento_3(self):
        arquivo = self.cleaned_data.get('documento_3')
        if arquivo:
            return validar_arquivo_seguro(arquivo)
        return arquivo
    
    def clean(self):
        cleaned_data = super().clean()
        texto = cleaned_data.get('texto_autodeclaracao')
        doc1 = cleaned_data.get('documento_1')
        
        # Regra de negócio: Deve ter texto OU pelo menos o primeiro documento
        if not texto and not doc1:
            raise ValidationError('Por favor, preencha o texto OU envie pelo menos o primeiro documento.')
        
        return cleaned_data
    
# FORMULÁRIO DE CADASTRO DO USUÁRIO
class CadastroUsuarioForm(UserCreationForm):
    # Campos extras que não existem no formulário padrão
    nome_completo = forms.CharField(max_length=50, help_text='Nome da Fazenda ou Razão Social')
    email = forms.EmailField(required=True)
    
    # O seletor de topo 
    TIPO_CHOICES = (
        ('produtor', 'Sou Produtor'),
        ('empresa', 'Sou Empresa')
    )
    tipo_usuario = forms.ChoiceField(choices=TIPO_CHOICES, widget=forms.RadioSelect)
    
    # Campos específicos (inicialmente opcionais na validação visual, mas tratados no backend)
    cpf = forms.CharField(max_length=11, label="CPF", required=False)
    cnpj = forms.CharField(max_length=14, label="CNPJ", required=False)
    endereco = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False)
    
    class Meta:
        model = CustomUser
        # Definimos quais campos do Model aparecem no HTML e na ordem certa
        fields = ('username', 'email', 'nome_completo', 'tipo_usuario', 'cpf', 'cnpj', 'endereco')
        
    # Validação Inteligente para saber qual foi escolhido
    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo_usuario')
        cpf = cleaned_data.get('cpf')
        cnpj = cleaned_data.get('cnpj')
        
        # Regra 1: Se for Produtor, TEM que ter CPF
        if tipo == 'produtor':
            if not cpf:
                self.add_error('cpf', 'O CPF é obrigatório para produtores.')
            # Limpa o CNPJ para não salvar lixo
            cleaned_data['cnpj'] = None
            
        # Regra 2: Se for Empresa, TEM que ter CNPJ
        elif tipo == 'empresa':
            if not cnpj:
                self.add_error('cnpj', 'O CNPJ é obrigatório para empresas.')
            # Limpa o CPF para não salvar lixo
            cleaned_data['cpf'] = None

        return cleaned_data
    
    def save(self, commit=True):
        # 1. Salva o Usuário Pai (CustomUser) primeiro
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['nome_completo'] # Usamos first_name para guardar o nome exibido
        user.tipo_usuario = self.cleaned_data['tipo_usuario']
        
        if commit:
            user.save()
            # Salva no perfil correto baseado na escolha
            cpf_limpo = self.cleaned_data['cpf']
            if user.tipo_usuario == 'produtor':
                PerfilProduto.objects.create(
                    user=user,
                    nome=self.cleaned_data['nome_completo'],
                    cpf=cpf_limpo,
                    endereco=self.cleaned_data['endereco']
                )
            elif user.tipo_usuario == 'empresa':
                cnpj_limpo = self.cleaned_data['cnpj']

                PerfilEmpresa.objects.create(
                    user=user,
                    razao_social=self.cleaned_data['nome_completo'],
                    cnpj=cnpj_limpo
                )
        return user
    
  
        # Exigir pelo menos um: texto OU arquivo
        if not texto and not arquivo:
            raise ValidationError(
                'É necessário preenchero texto da autodeclaração ou enviar um arquivo.'
            )
        
        return cleaned_data


class ProdutoComAutodeclaracaoForm(forms.Form):
    """Formulário para selecionar um produto e enviar autodeclaração"""
    
    produto = forms.ModelChoiceField(
        queryset=Produtos.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'produto_select'
        }),
        label='Selecione o Produto',
        empty_label='-- Escolha um produto --'
    )
    
    texto_autodeclaracao = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Digite aqui o texto da sua autodeclaração (opcional)',
            'style': 'font-size: 14px;'
        }),
        label='Texto da Autodeclaração'
    )
    
    arquivo_autodeclaracao = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png',
            'id': 'arquivo_input'
        }),
        label='Arquivo de Autodeclaração',
        help_text='PDF, DOC, DOCX, JPG, PNG. Máximo 5MB.'
    )
    
    def clean_arquivo_autodeclaracao(self):
        """Validação customizada do arquivo"""
        arquivo = self.cleaned_data.get('arquivo_autodeclaracao')
        
        if arquivo:
            # Validar tamanho
            if arquivo.size > 5242880:  # 5MB
                raise ValidationError('O arquivo não pode exceder 5MB.')
            
            # Validar extensão
            extensoes_permitidas = ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png']
            extensao_arquivo = arquivo.name.split('.')[-1].lower()
            
            if extensao_arquivo not in extensoes_permitidas:
                raise ValidationError(
                    f'Tipo de arquivo não permitido. Aceitos: {", ".join(extensoes_permitidas)}'
                )
            
            # Validar tipo MIME
            tipos_mime_permitidos = settings.ALLOWED_UPLOAD_MIME_TYPES
            if arquivo.content_type not in tipos_mime_permitidos:
                raise ValidationError('Tipo MIME do arquivo não é permitido.')
        
        return arquivo

    def clean(self):
        """Validação geral do formulário"""
        cleaned_data = super().clean()
        texto = cleaned_data.get('texto_autodeclaracao')
        arquivo = cleaned_data.get('arquivo_autodeclaracao')
        
        # Exigir pelo menos um: texto OU arquivo
        if not texto and not arquivo:
            raise ValidationError(
                'É necessário preencher o texto da autodeclaração ou enviar um arquivo.'
            )
        
        return cleaned_data
