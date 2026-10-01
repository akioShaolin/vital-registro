# Validação local

Executada em 30/09/2026, no Windows, com Python 3.13.3 e Kivy 2.3.1.

| Verificação | Resultado |
| --- | --- |
| `python -m unittest discover -s tests -v` | 16 testes aprovados |
| `python scripts/smoke_ui.py` | Aprovado em sessão gráfica Windows |
| `python -m compileall -q main.py vitalregistro scripts tests` | Sem erros de sintaxe |
| `python scripts/check_repository.py` | Aprovado: 33 arquivos candidatos, notebook, ícone e permissões |
| `.gitignore` | Banco, runtime CSV, ambientes e `.env` ignorados; CSV em `tests/fixtures/` permitido |

Os testes cobrem CRUD, persistência ao reabrir o banco, edição de todos os campos, ordem cronológica, datas históricas, ano bissexto, períodos inclusivos, decimais, validação, rollback, proteção de banco inválido/versão futura e CSV UTF-8 com caracteres especiais e proteção contra sobrescrita.

O smoke exercita as ações da interface com SQLite temporário e medições fictícias: criar, editar, abrir detalhes, atualizar gráficos, abrir seletores, exportar e excluir. Não substitui testes manuais de toque, teclado, acessibilidade ou ciclo de vida Android. Capturas de revisão ficam em `runtime/`, ignorado pelo Git.

## Ainda não executado

- Buildozer em Linux e notebook completo no Google Colab.
- Instalação de APK, ícone no launcher e inspeção do manifesto final.
- Exportação via Storage Access Framework em aparelho real.
- Suspensão/retomada, encerramento pelo sistema, teclado e resoluções Android.
- Workflow no GitHub: depende da publicação do repositório.

Não há APK validado ou release publicada. A documentação de build descreve o procedimento e suas condições, não um resultado já obtido.
