# Compilação Android e Google Colab

## Por que o fluxo mudou

O notebook anterior exigia Python 3.10–3.12 e combinava p4a `master`, API 35 e NDK 25b. Ele interrompia no Python 3.13 do Colab antes de instalar as ferramentas. Remover essa restrição não atualizaria as recipes, o compilador nativo nem as dependências Python.

O Google anunciou a [migração do Colab para Python 3.13](https://github.com/googlecolab/colabtools/issues/6081) em agosto de 2026. A versão de manutenção pode variar entre imagens; a primeira célula imprime `sys.version`, `sys.executable` e o sistema da sessão real. Não presumimos que todas as sessões tenham exatamente a mesma versão.

O fluxo novo separa três interpretadores:

1. **Kernel Colab:** executa o notebook e coordena subprocessos. Permanece com seus pacotes originais.
2. **Python de build:** CPython **3.14.7 com GIL**, em `.venv-build/`, executa Buildozer, p4a e os testes. Se o interpretador inicial não for exatamente esse, uv baixa uma distribuição isolada; não há downgrade do Colab.
3. **Python das recipes p4a:** **3.14.2**, tanto `hostpython3` quanto `python3` embarcado no APK. Esse par deve ter a mesma versão; não é o Python do kernel. Usamos a versão padrão do commit p4a selecionado, sem substituir isoladamente a recipe por outro patch de CPython.

## Combinação selecionada

Revisada nas fontes oficiais em 30/09/2026. Isto é uma configuração fundamentada no upstream, **não um APK já compilado e validado**.

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
8. Baixe os APKs de `bin/`. A célula recusa download se a compilação da sessão não terminou com sucesso.

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

Os commits principais e várias dependências são fixos, mas pacotes apt, Rust stable e dependências transitivas das recipes ainda podem evoluir. O primeiro build validado deve guardar o log e versões efetivas. A compilação depende de disponibilidade de GitHub, PyPI, downloads Astral e servidores Android, de vários GB de disco e da duração da sessão Colab.

## Exportação e privacidade Android

O aplicativo permanece offline. `android.permissions` continua vazio, `android.allow_backup = False` e o seletor CSV usa `ACTION_CREATE_DOCUMENT`. Não adicionamos internet nem permissões amplas de armazenamento. A rede é necessária somente para obter as ferramentas e dependências **durante o build**.

## Validação e limites

Testes de lógica e seleção de ambiente podem ser executados localmente sem SDK. Os testes da preparação usam subprocessos simulados para verificar a escolha do Python e a propagação de falhas; não provam compilação nativa.

**Não foi executado um build completo no Colab/Linux nem validado APK em aparelho nesta revisão.** Buildozer master e p4a develop são versões de desenvolvimento, mesmo fixadas em commits. Recipes nativas, Cython, downloads e o ambiente Colab ainda podem revelar problemas no primeiro build real. Consulte [VALIDATION.md](VALIDATION.md).

Após gerar o APK, confira manifesto, ícone, instalação, persistência ao reiniciar, edição/exclusão, teclado, gráficos, exportação/cancelamento e suspensão/retomada. Um build bem-sucedido não substitui esses testes. Publicação na Play Store continua fora deste fluxo debug.
