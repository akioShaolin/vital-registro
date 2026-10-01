# Contribuindo

1. Faça um fork e clone `https://github.com/SEU_USUARIO/vital-registro.git`.
2. Para desenvolver e executar a interface localmente, prepare Python **3.12 ou 3.13** e o ambiente virtual conforme o [README](README.md#executando-localmente). Para compilar Android, siga o ambiente separado descrito abaixo.
3. Instale `requirements.txt` e crie uma branch: `git switch -c minha-alteracao`.
4. Mantenha SQL em `database.py`, validações em `models.py` e interface em `app.py`/`ui/`.
5. Execute `python -m unittest discover -s tests -v`. Para mudanças visuais, execute também `python scripts/smoke_ui.py` e confira a interface manualmente.
6. Use apenas dados fictícios. Não inclua bancos, exportações pessoais, tokens, APKs ou caminhos da sua máquina.
7. Revise `git diff` e `git status`, faça commit e push da branch e abra um Pull Request explicando a alteração e os testes executados.

Mudanças Android devem descrever o aparelho/API testados ou deixar explícito que não foram validadas. Não adicione dependências nativas sem considerar recipes do python-for-android. Atualize documentação quando o comportamento mudar.

## Qual Python usar

| Contexto | Versão e finalidade |
| --- | --- |
| Desenvolvimento/execução local | Python **3.12 ou 3.13**, com Kivy 2.3.1 de `requirements.txt`, conforme o suporte desktop documentado no README. |
| CI | Python **3.12, 3.13 e 3.14** na [matriz do GitHub Actions](.github/workflows/tests.yml), para testes de lógica independente e verificação de sintaxe. O workflow não instala Kivy nem executa a interface ou compila Android. |
| Kernel Google Colab | Python **3.13.15** no build documentado. O notebook detecta a versão da sessão, que pode mudar, e preserva o kernel. |
| Ferramentas de build Android | **CPython 3.14.7 com GIL**, isolado em `.venv-build/`, para Buildozer, p4a e testes. O setup prepara esse interpretador e instala `requirements-build.txt`. |
| Python embarcado no APK | **3.14.2**, com `hostpython3` também **3.14.2**, conforme `buildozer.spec` e as recipes do commit p4a fixado. É preparado pelo p4a; não precisa ser instalado como Python desktop. |

A cobertura da lógica no CI com Python 3.14 não equivale à validação da interface desktop nessa versão. Para contribuir na interface, mantenha o ambiente local 3.12/3.13; não use `requirements-build.txt` como dependências de execução do aplicativo.

Para compilar, siga [docs/ANDROID.md](docs/ANDROID.md) e o notebook Colab. Em Linux x86_64/WSL2, `scripts/setup_linux.sh` aceita Python >=3.10 apenas para iniciar o preparo e obtém o CPython 3.14.7 isolado quando necessário. Esse requisito inicial não amplia o suporte desktop nem muda o Python embarcado. Não substitua o kernel do Colab ou as versões fixadas para igualar os diferentes ambientes.
