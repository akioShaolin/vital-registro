# Contribuindo

1. Faça um fork e clone `https://github.com/SEU_USUARIO/vital-registro.git`.
2. Prepare Python 3.12/3.13 e o ambiente virtual conforme o [README](README.md#executando-localmente).
3. Instale `requirements.txt` e crie uma branch: `git switch -c minha-alteracao`.
4. Mantenha SQL em `database.py`, validações em `models.py` e interface em `app.py`/`ui/`.
5. Execute `python -m unittest discover -s tests -v`. Para mudanças visuais, execute também `python scripts/smoke_ui.py` e confira a interface manualmente.
6. Use apenas dados fictícios. Não inclua bancos, exportações pessoais, tokens, APKs ou caminhos da sua máquina.
7. Revise `git diff` e `git status`, faça commit e push da branch e abra um Pull Request explicando a alteração e os testes executados.

Mudanças Android devem descrever o aparelho/API testados ou deixar explícito que não foram validadas. Não adicione dependências nativas sem considerar recipes do python-for-android. Atualize documentação quando o comportamento mudar.
