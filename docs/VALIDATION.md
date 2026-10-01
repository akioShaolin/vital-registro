# Validação local

Revisada em 30/09/2026, no Windows. A suíte de lógica e build foi executada com Python 3.13.3 e CPython 3.14.7. O smoke da interface foi executado anteriormente com Python 3.13.3 e Kivy 2.3.1; não foi repetido nesta alteração restrita ao build.

| Verificação | Resultado |
| --- | --- |
| `python -m unittest discover -s tests -v` | 25 testes aprovados em 3.13.3 e 3.14.7 |
| `python scripts/smoke_ui.py` | Aprovado anteriormente em sessão gráfica Windows / Python 3.13.3 |
| `python -m compileall -q main.py vitalregistro scripts tests` | Sem erros de sintaxe |
| `python scripts/check_repository.py` | Aprovado: 36 arquivos candidatos, notebook, ícone e permissões |
| `bash -n scripts/setup_linux.sh` | Sintaxe aprovada usando Git Bash; não executa apt ou compilação |
| uv 0.12.21 / Python 3.14.7 | Download isolado da distribuição Windows realizado; não é teste do preparo Linux |
| `.gitignore` | Banco, runtime CSV, ambientes e `.env` ignorados; CSV em `tests/fixtures/` permitido |

Os testes cobrem CRUD, persistência ao reabrir o banco, edição de todos os campos, ordem cronológica, datas históricas, ano bissexto, períodos inclusivos, decimais, validação, rollback, proteção de banco inválido/versão futura e CSV UTF-8 com caracteres especiais e proteção contra sobrescrita.

O smoke exercita as ações da interface com SQLite temporário e medições fictícias: criar, editar, abrir detalhes, atualizar gráficos, abrir seletores, exportar e excluir. Não substitui testes manuais de toque, teclado, acessibilidade ou ciclo de vida Android. Capturas de revisão ficam em `runtime/`, ignorado pelo Git.

Os nove testes novos verificam seleção de CPython 3.14.7 com GIL a partir de um kernel 3.13, uso direto de um interpretador já compatível, preservação de ambiente antigo, interrupção ao falhar o bootstrap, isolamento das variáveis do kernel, configuração offline e bloqueio do download após erro. Instalação Linux e subprocessos de build são **simulados** nesses testes. As células do notebook foram verificadas sintaticamente, sem execução no Colab.

## Ainda não executado

- Buildozer em Linux e notebook completo no Google Colab.
- Instalação de APK, ícone no launcher e inspeção do manifesto final.
- Exportação via Storage Access Framework em aparelho real.
- Suspensão/retomada, encerramento pelo sistema, teclado e resoluções Android.
- Workflow no GitHub: depende da publicação do repositório.

Não há APK validado ou release publicada. A documentação de build descreve o procedimento e suas condições, não um resultado já obtido.
