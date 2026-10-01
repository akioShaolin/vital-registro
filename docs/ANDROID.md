# Compilação Android e Google Colab

## Por que o fluxo mudou

O notebook anterior exigia Python 3.10–3.12 e combinava p4a `master`, API 35 e NDK 25b. Ele interrompia no Python 3.13 do Colab antes de instalar as ferramentas. Remover essa restrição não atualizaria as recipes, o compilador nativo nem as dependências Python.

O Google anunciou a [migração do Colab para Python 3.13](https://github.com/googlecolab/colabtools/issues/6081) em agosto de 2026. O primeiro build funcional deste projeto utilizou **Python 3.13.15 no kernel**, conforme informado pelo autor. A primeira célula imprime a versão da sessão real, que pode variar entre imagens.

O fluxo novo separa três interpretadores:

1. **Kernel Colab:** executa o notebook e coordena subprocessos. Permanece com seus pacotes originais.
2. **Python de build:** CPython **3.14.7 com GIL**, em `.venv-build/`, executa Buildozer, p4a e os testes. Se o interpretador inicial não for exatamente esse, uv baixa uma distribuição isolada; não há downgrade do Colab.
3. **Python das recipes p4a:** **3.14.2**, tanto `hostpython3` quanto `python3` embarcado no APK. Esse par deve ter a mesma versão; não é o Python do kernel. Usamos a versão padrão do commit p4a selecionado, sem substituir isoladamente a recipe por outro patch de CPython.

## Combinação selecionada

Esta é a configuração preservada do fluxo que o autor confirmou ter produzido o primeiro APK funcional em 30/09/2026. Nenhuma versão de Python, Buildozer, p4a, Kivy, SDK, NDK ou Java foi trocada na revisão pós-build.

| Componente | Seleção e função |
| --- | --- |
| Host | Linux x86_64, Colab CPU ou Ubuntu/WSL2 |
| Python de build | CPython 3.14.7 com GIL, ambiente isolado |
| uv | 0.12.21, somente para obter o Python quando necessário |
| Buildozer | `1.6.1.dev0`, master fixado em `a153097b3c534bea8a17da2abf1369d67c8cbfcb` |
| python-for-android | develop fixado em `e772ad93f20a61c0bbe1cf8955e073cfb41062e1` |
| Python Android / hostpython | 3.14.2 / 3.14.2, recipes do p4a |
| Kivy / Pyjnius | 2.3.1 / 1.7.0, compilados pelas recipes p4a |
| SDK target / mínimo | API 36 / API 24 (Android 7) |
| NDK / NDK API | r29 / 24 |
| Java | OpenJDK 17, JDK completo |
| Bootstrap / ABI | SDL2 / arm64-v8a |
| Ferramentas Python do build | Cython 3.3.0, setuptools 84.0.0, legacy-cgi 2.6.4 |

### Evidência do primeiro build

- Arquivo: `vitalregistro-0.1.0-arm64-v8a-debug.apk`.
- Tamanho informado: **26.009.326 bytes**.
- Compilado e baixado pelo Google Colab, kernel **Python 3.13.15**.
- Instalado e iniciado em aparelho físico com **Android 16**; modelo não informado.
- Criação e persistência de registro, histórico e representação inicial no gráfico confirmados pelo autor.

Os commits na tabela estão identificados e fixados no repositório: p4a `e772ad93f20a61c0bbe1cf8955e073cfb41062e1` e Buildozer `a153097b3c534bea8a17da2abf1369d67c8cbfcb`. **Não recebemos o log/HEAD efetivo nem o APK local desse build para confirmar independentemente os commits ou calcular seu hash.** A configuração declarada não deve ser confundida com uma inspeção do binário. O notebook passa a guardar `bin/build-info.json` com commit efetivo p4a, commit do projeto, versões e SHA-256 dos APKs nas próximas execuções.

As [capturas reais](screenshots/README.md) são do primeiro APK, antes das correções visuais desta revisão. Gerar novamente o APK e conferir essas correções em Android 16 é uma etapa pendente; não invalida o marco já alcançado.

A [documentação atual do Buildozer](https://buildozer.readthedocs.io/en/latest/installation/) indica o fluxo moderno com Python 3.14, p4a develop, API 36 e NDK 29, mantendo Java 17. Fixamos commits para evitar mudanças silenciosas nas branches.

O [Buildozer fixado](https://github.com/kivy/buildozer/blob/a153097b3c534bea8a17da2abf1369d67c8cbfcb/setup.py) admite Cython `<3.4`; por isso não mantivemos o antigo 0.29.34 no ambiente principal. As dependências específicas das recipes são instaladas **separadamente pelo p4a**, que controla suas restrições de Cython. Não force globalmente essa versão dentro das recipes.

A [recipe Kivy fixada](https://github.com/kivy/python-for-android/blob/e772ad93f20a61c0bbe1cf8955e073cfb41062e1/pythonforandroid/recipes/kivy/__init__.py) inclui patches, inclusive para `ast.Str` no Python 3.14. Não instalamos o Kivy desktop no kernel ou no ambiente de build; o p4a prepara a versão Android. `requirements.txt` continua destinado ao aplicativo desktop em Python 3.12/3.13. Nenhuma funcionalidade do aplicativo foi alterada para compilar.

## Executar no Colab

1. Publique esta revisão do projeto em **https://github.com/akioShaolin/vital-registro.git**. Abrir um notebook local atualizado não atualiza o código que ele clonará.
2. Abra [build_colab.ipynb](build_colab.ipynb) no Colab, com runtime CPU Linux x86_64. GPU não é necessária.
3. Execute a detecção e o clone. Um clone existente do mesmo remoto pode ser reutilizado, mas não recebe `pull` automático; para obter a revisão publicada mais recente, use uma sessão limpa.
4. Execute a instalação. O notebook passa explicitamente `sys.executable` ao script, evitando escolher por acidente outro `python3` no PATH.
5. Execute os testes e a verificação de sintaxe com `.venv-build/bin/python`.
6. Leia as condições do SDK e habilite `ACCEPT_ANDROID_SDK_LICENSES` se concordar. Só o spec do clone temporário será alterado.
7. Execute a compilação. O script mostra Java, dependências Python, saída detalhada do Buildozer e commit p4a efetivo.
8. Baixe os APKs e `build-info.json` de `bin/`. A célula recusa download se a compilação da sessão não terminou com sucesso. Guarde o JSON junto ao APK para identificar a compilação.

O setup usa `apt-get` como root no Colab e `sudo` em uma sessão Linux comum. Ferramentas auxiliares, Python baixado e Rust ficam em `.build-tools/`, excluída de Git e APK; o ambiente de build fica em `.venv-build/`. [uv usa distribuições python-build-standalone](https://docs.astral.sh/uv/guides/install-python/). Não modifica o Python do sistema ou o kernel.

As restrições não foram simplesmente removidas: o bootstrap exige Python >=3.10 e Linux x86_64; antes de compilar há verificação exata de CPython 3.14.7 com GIL. Uma falha de download, instalação ou validação interrompe o fluxo. Não há fallback silencioso para um interpretador incompatível.

## Linux / WSL2 fora do Colab

Em um clone no filesystem Linux, com Python >=3.10 disponível para iniciar o preparo:

```bash
bash scripts/setup_linux.sh
.venv-build/bin/python -m unittest discover -s tests -v
.venv-build/bin/python scripts/build_android.py
```

Não é necessário ativar o ambiente. `build_android.py` prepara PATH, Java 17 e Rust antes de chamar `buildozer -v android debug`. O wrapper usa `subprocess.run(..., check=True)`; não disfarça falhas como sucesso. Em execução root, responde somente ao aviso do Buildozer; o aceite das licenças Android é independente. No terminal comum, o SDK pode solicitar confirmação interativa.

Para guardar a saída sem perder o código de erro:

```bash
set -o pipefail
.venv-build/bin/python scripts/build_android.py 2>&1 | tee build.log
```

No WSL2, clone em `~/vital-registro`, fora de `/mnt/c` e do OneDrive. O script não oferece build nativo Windows/macOS nem host ARM. O APK é ARM64, não um APK x86 de emulador.

## Repetição e caches antigos

Uma `.venv-build` de versão incompatível é rejeitada e preservada. No Colab, prefira uma sessão limpa após atualizar do fluxo antigo. Em Linux, renomeie a pasta antiga antes de executar o setup novamente. Não reutilize `.buildozer/` de p4a master/NDK 25b: guarde-a fora do clone ou use outro clone limpo. Nenhum script apaga recursivamente esses diretórios.

Os commits principais e várias dependências são fixos, mas pacotes apt, Rust stable e dependências transitivas das recipes ainda podem evoluir. Guarde logs, versões efetivas e `build-info.json` das próximas execuções. A compilação depende de disponibilidade de GitHub, PyPI, downloads Astral e servidores Android, de vários GB de disco e da duração da sessão Colab.

## Exportação e privacidade Android

O aplicativo permanece offline. `android.permissions` continua vazio, `android.allow_backup = False` e o seletor CSV usa `ACTION_CREATE_DOCUMENT`. Não adicionamos internet nem permissões amplas de armazenamento. A rede é necessária somente para obter as ferramentas e dependências **durante o build**.

## Validação e limites

Testes de lógica e seleção de ambiente podem ser executados localmente sem SDK. Os testes da preparação usam subprocessos simulados para verificar a escolha do Python e a propagação de falhas; não provam compilação nativa.

**O primeiro build Colab e o uso básico em Android 16 foram confirmados pelo autor.** Nesta revisão, as correções posteriores foram verificadas localmente, sem gerar outro APK. Buildozer master e p4a develop continuam sendo versões de desenvolvimento, mesmo fixadas em commits; futuros builds e novos ambientes exigem nova verificação. Consulte [VALIDATION.md](VALIDATION.md).

No próximo APK, confira o ícone do launcher, margens de status/navegação, formulário e teclado, edição/exclusão, todos os gráficos/períodos, exportação/cancelamento e suspensão/retomada. A exportação SAF está implementada e revisada, mas ainda não foi confirmada em aparelho. Publicação na Play Store continua fora deste fluxo debug.
