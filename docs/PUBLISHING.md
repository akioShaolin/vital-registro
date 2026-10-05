# Publicar em vital-registro

A v0.1.0 já foi publicada, conforme informado pelo autor. A implementação atual prepara v0.2.0 para revisão e não executa commit, tag, push ou release. Os dados de v0.1.0 abaixo são históricos; uma distribuição v0.2.0 exige novo APK, novo build-info e validação Android.

O repositório do projeto é `https://github.com/akioShaolin/vital-registro.git`. A versão 0.1.0 já teve APK debug ARM64 compilado no Colab e uso básico confirmado no Samsung Galaxy M55 com Android 16 pelo autor. Esta revisão não faz push nem cria release automaticamente. O autor da licença é Pedro Sakuma (2026).

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
git commit -m "Prepare v0.2.0 independent measurements and CSV import"
```

A mensagem é uma sugestão para a revisão v0.2.0 após aprovação do autor. As validações de hardware restantes estão em [VALIDATION.md](VALIDATION.md). Não trate o APK debug como release estável. Caso decida distribuir o APK, use GitHub Releases com indicação explícita de desenvolvimento, fora do histórico normal do código.

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

Se o remoto já tiver commits, busque e examine o histórico antes de integrar. Não use force push. Se publicar em outro remoto, ajuste o URL de clone no README e no notebook. No repositório do projeto, o URL já está configurado. Confirme a execução de `.github/workflows/tests.yml` na aba Actions.

## Planejamento histórico da GitHub Release v0.1.0

O roteiro abaixo foi registrado antes da publicação da v0.1.0 e permanece como referência do artefato histórico, não como instrução para republicá-lo.

- Tag planejada: `v0.1.0`.
- Título planejado: **VitalRegistro v0.1.0**.
- Status: primeira versão funcional de desenvolvimento, **DEBUG + ARM64-V8A**, sem indicação de estabilidade ou prontidão para Google Play.
- Anexos previstos: `vitalregistro-0.1.0-arm64-v8a-debug.apk` e `build-info.json`.

O [JSON preservado](releases/v0.1.0/build-info.json) identifica o ambiente e o commit que produziram o APK documentado. Antes de distribuir, confira tamanho e SHA-256 do binário contra esse JSON; não associe o registro a outro APK com o mesmo nome. Se recompilar, preserve os metadados correspondentes à nova compilação. O commit de preparação documental pode ser posterior ao commit do build, e essa distinção deve permanecer explícita.

Na descrição da futura release, limite a validação ao relato do autor no Samsung Galaxy M55: inicialização, criação, persistência local, histórico, abertura dos gráficos e representação correta de uma medição. Mantenha as pendências de [VALIDATION.md](VALIDATION.md). Distribua o APK como anexo da release, nunca dentro do histórico normal do Git.
