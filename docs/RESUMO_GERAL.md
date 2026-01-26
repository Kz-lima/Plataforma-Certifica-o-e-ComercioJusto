# Resumo Geral do Projeto

## Estrutura essencial (topo do repositório)
- README.md
- COMECE_AQUI.md
- GUIA_PRATICO_NOVO_USUARIO.md
- SUMARIO_EXECUTIVO.md
- docs/RESUMO_GERAL.md (este arquivo)
- docs/archive/… (documentação completa arquivada para reduzir poluição visual)

## Ambiente e comandos principais
- Ativar venv (única a manter):
  - PowerShell: `.\\venv\\Scripts\\Activate.ps1`
- Instalar deps: `pip install -r amazonia_marketing/requirements.txt`
- Rodar servidor: `cd amazonia_marketing` e `python manage.py runserver`

## Credenciais de teste
- Produtor: teste@produtor.com / senha123
- Empresa: teste@empresa.com / senha123
- Admin: teste@admin.com / senha123

## Principais mudanças recentes
- Login corrigido: `UsuarioBase` agora tem senha hash (métodos `set_password` e `check_password`).
- Forms de cadastro (produtor/empresa) agora salvam senha hash antes de criar o usuário.
- View `login_usuarios` valida senha com hash e mantém fallback para `UsuariosLegado`.
- Migração 0007 aplicada para adicionar campo `senha` e timestamps a `UsuarioBase`.
- Instalação de Pillow como wheel binário para suportar `ImageField` sem erros.
- Removido venv duplicado em `amazonia_marketing/venv` para evitar conflito (usar apenas venv da raiz).

## Onde está o restante da documentação
- Pasta `docs/archive/`: todos os guias detalhados e históricos.
- Pasta `docs/archive/amazonia_marketing/`: sumários e guias específicos do app.

## Próximos passos sugeridos
- Testar login via UI com as credenciais acima (produtor, empresa, admin) e confirmar redirecionamentos.
- Se precisar de instruções completas, consultar os arquivos em `docs/archive/`.
