# Publicar em vital-registro

O repositório do projeto é `https://github.com/akioShaolin/vital-registro.git`. A versão 0.1.0 já teve APK debug ARM64 compilado no Colab e uso básico confirmado em Android 16 pelo autor. Esta revisão não faz push nem cria release automaticamente. O autor da licença é Pedro Sakuma (2026).

## Revisar antes do commit

Se ainda não houver `.git`, execute `git init -b main`. Em um repositório existente, preserve a branch e o histórico.

```bash
python -m unittest discover -s tests -v
python -m compileall -q main.py vitalregistro scripts tests
python scripts/check_repository.py
git status --short --untracked-files=all
git status --ignored --short
git add .gitignore .gitattributes .github README.md LICENSE CONTRIBUTING.md CHANGELOG.md requirements.txt requirements-build.txt buildozer.spec main.py vitalregistro assets tests scripts docs
git diff --cached --check
git diff --cached --stat
git diff --cached
```

No Windows, use `py -3.13` ou o Python do ambiente virtual. Confira a lista antes de continuar: não deve conter banco de dados, CSV pessoal, `.env`, tokens, arquivos de assinatura, `.venv`, `.buildozer`, APK ou logs. Imagens devem mostrar somente a identidade visual ou dados fictícios. O `.gitignore` não remove arquivos já rastreados; inspecione `git ls-files` caso esteja reaproveitando um histórico.

```bash
git commit -m "Polish 0.1.0 after first Android build"
```

A mensagem descreve as correções após o primeiro build funcional. Os ajustes novos ainda precisam de teste no aparelho. Não trate o APK debug como release estável. Caso decida distribuir o APK, use GitHub Releases com indicação explícita de desenvolvimento, fora do histórico normal do código.

## Enviar ao remoto existente ou preparar outro clone

Para o projeto existente, confira `git remote -v` e `git status` antes de `git push`. As instruções de criação abaixo são somente para quem ainda não tem remoto; não recrie `vital-registro` se ele já existe.

Opção com GitHub CLI instalada e autenticada:

```bash
gh auth status
gh repo create vital-registro --public --source=. --remote=origin
git push -u origin HEAD
```

Caso `origin` já exista, confira `git remote -v` e use-o somente se for o destino correto. Não substitua URLs nem histórico automaticamente.

Alternativa: no GitHub, crie um repositório público vazio chamado **vital-registro**, sem gerar README ou LICENSE. Depois substitua `SEU_USUARIO`:

```bash
git remote add origin https://github.com/SEU_USUARIO/vital-registro.git
git remote -v
git push -u origin HEAD
```

Se o remoto já tiver commits, busque e examine o histórico antes de integrar. Não use force push. Após publicar, atualize o URL de clone no README e no notebook e confirme a execução de `.github/workflows/tests.yml` na aba Actions.
