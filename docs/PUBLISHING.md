# Publicação da v0.2.0

Roteiro para o responsável publicar em `https://github.com/akioShaolin/vital-registro`. Esta preparação documental não executa commit, tag, push ou GitHub Release. A v0.1.0 já foi publicada conforme informado pelo autor; sua evidência permanece em [releases/v0.1.0/build-info.json](releases/v0.1.0/build-info.json) e [VALIDATION.md](VALIDATION.md).

## Identidade da versão

- Versão no aplicativo e spec: `0.2.0`.
- Tag a publicar: `v0.2.0`.
- Data de publicação definida pelo autor: **06/10/2026**.
- Título: **VitalRegistro v0.2.0**.
- Classificação definida pelo autor: **Release normal**, com APK de desenvolvimento **DEBUG + ARM64-V8A**.
- Texto preparado: [RELEASE_NOTES.md](releases/v0.2.0/RELEASE_NOTES.md).
- Anexos: `vitalregistro-0.2.0-arm64-v8a-debug.apk` e o [build-info.json correspondente](releases/v0.2.0/build-info.json).

A [política de versionamento](VERSIONING.md) explica a evolução 0.1.0 → 0.2.0, a incompatibilidade de dados e a diferença entre versão, tag, release e schema.

## Revisão antes do fechamento

Execute com o Python local 3.12/3.13 preparado conforme o README (no Windows, use `.\.venv\Scripts\python.exe`):

```bash
python -m unittest discover -s tests -v
python -m compileall -q main.py vitalregistro scripts tests
python scripts/check_repository.py
git diff --check
git diff --cached --check
git status --short --untracked-files=all
git diff
git diff --cached
```

Confira os arquivos já preparados no índice antes de adicionar qualquer alteração. APKs ficam fora do histórico Git; `prints/` contém material local ignorado e as capturas selecionadas ficam em `docs/screenshots/v0.2.0/`. Não inclua bancos ou CSVs pessoais, credenciais e chaves de assinatura. Registre resultados novos sem substituir o histórico de validação.

O APK documentado veio de `0835bab79306bbf44bf21954dff897d4f936a562`. Compare esse commit com a árvore final, incluindo alterações ainda não commitadas:

```bash
git diff --stat 0835bab79306bbf44bf21954dff897d4f936a562
git diff 0835bab79306bbf44bf21954dff897d4f936a562 -- main.py vitalregistro assets buildozer.spec requirements.txt requirements-build.txt scripts
```

Revise também o diff completo para não deixar de fora outros arquivos de build. Se houver mudança funcional ou na compilação, gere novo APK e metadados e atualize as notas. Se as diferenças forem somente documentais, a tag poderá apontar para o commit final de documentação, mantendo o commit original do APK explicitamente registrado. Não invente o SHA do fechamento antes de ele existir.

## Conferência do binário antes de anexar

Coloque o APK recebido em `bin/`. Em PowerShell, compare com o JSON arquivado e interrompa se não coincidir:

```powershell
$releaseInfo = Get-Content -Raw docs/releases/v0.2.0/build-info.json | ConvertFrom-Json
$releaseArtifact = $releaseInfo.artifacts[0]
$releaseApk = Get-Item -LiteralPath (Join-Path bin $releaseArtifact.name)
if ($releaseApk.Length -ne $releaseArtifact.bytes) { throw 'Tamanho do APK divergente' }
$releaseHash = (Get-FileHash -LiteralPath $releaseApk.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
if ($releaseHash -ne $releaseArtifact.sha256) { throw 'SHA-256 do APK divergente' }
```

Essa conferência não foi realizada nesta revisão documental. Mesmo um hash coincidente não valida o funcionamento em aparelho. Consulte as pendências em [VALIDATION.md](VALIDATION.md) e mantenha-as nas notas se ainda não tiverem sido testadas.

## Publicação manual após a revisão

1. A data definida é **06/10/2026**, já registrada no changelog e nas notas. Se a publicação for adiada, ajuste-a. Atualize o status de preparação nas notas e no README quando a publicação for efetiva.
2. Revise e faça o commit final somente quando decidir fechar a versão. Confira a branch e o remoto antes de enviar. Aguarde o resultado do CI; não declare aprovação antes de observá-la.
3. Confira se `v0.2.0` já existe localmente ou no remoto. Se existir, examine-a; não sobrescreva uma tag publicada.
4. Crie uma tag anotada `v0.2.0` no commit final revisado e envie essa tag ao remoto correto. Confira a diferença entre esse commit e o commit do build conforme descrito acima.
5. No GitHub Releases, prepare um rascunho com a tag `v0.2.0`, título **VitalRegistro v0.2.0** e o conteúdo das notas. Deixe a opção **Set as a pre-release** desmarcada e anexe somente o APK conferido e seu JSON.
6. Confira os links das notas para a tag, os dois anexos e as advertências de incompatibilidade. Publique apenas após essa revisão; então registre o URL efetivo onde pertinente.

Não reutilize o JSON da v0.1.0 e não confunda GitHub Release com APK Android de produção. Novas compilações precisam de seus próprios metadados. Não mova uma tag publicada para acomodar correções de código: prepare a próxima versão.
