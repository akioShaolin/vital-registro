# Compilação Android

## Escopo e estado

A configuração inicial gera APK **debug ARM64** para testes, com mínimo API 24. Compilação e instalação em aparelho ainda não foram executadas neste projeto. Ela não é uma configuração de publicação na Play Store.

O ambiente recomendado para esta configuração é Ubuntu 24.04 com Python 3.12 e Java 17. O `buildozer.spec` usa Buildozer 1.6.0, p4a `master`, Kivy 2.3.1, API 35 e NDK 25b. A branch p4a não é imutável: depois do primeiro build validado, registre o commit exato usando `git -C .buildozer/android/platform/python-for-android rev-parse HEAD` e fixe `p4a.commit` para maior reprodutibilidade.

## Preparar e compilar

No Linux, dentro do clone do projeto:

```bash
bash scripts/setup_linux.sh
source .venv-build/bin/activate
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH="$JAVA_HOME/bin:$PATH"
buildozer -v android debug
```

O script instala pacotes de sistema via `sudo` e cria um ambiente separado de build. Leia e aceite as licenças do Android SDK quando o Buildozer solicitar. `android.accept_sdk_license` permanece desativado por padrão.

O download inicial do SDK/NDK exige rede, vários GB de disco e pode demorar. O aplicativo resultante funciona offline. A saída fica em `bin/`. Para guardar os logs sem ocultar falhas:

```bash
set -o pipefail
buildozer -v android debug 2>&1 | tee build.log
```

No WSL2, copie/clone o projeto no filesystem Linux (por exemplo `~/vital-registro`), fora de `/mnt/c` e do OneDrive, antes de compilar. No Windows, utilize ADB para instalar o APK ou transfira-o ao aparelho e autorize a instalação pela origem escolhida.

## Colab

Abra [build_colab.ipynb](build_colab.ipynb) e execute as células em ordem. Informe uma URL HTTPS pública; se o repositório ainda não existe, publique-o primeiro usando [PUBLISHING.md](PUBLISHING.md). O notebook não utiliza tokens.

O fluxo verifica Python 3.10–3.12 para a configuração p4a master e interrompe em outras versões. Se o Colab mudar seu runtime, use Ubuntu 24.04/Python 3.12 em vez de ignorar a verificação. A documentação atual do Buildozer descreve também um fluxo com Python 3.14/p4a develop/NDK recente, que exige atualização e nova validação conjunta da configuração.

O notebook exige confirmação explícita de leitura das licenças para habilitar o aceite automático apenas no clone do Colab. Comandos usam `subprocess.run(check=True)` e propagam erros. A sessão pode expirar e o disco é temporário: baixe o APK antes de encerrá-la. Não há promessa de build reproduzido até execução real e fixação do commit p4a.

## Exportação e privacidade Android

`android_export.py` usa `ACTION_CREATE_DOCUMENT` e grava UTF-8 no URI escolhido pelo usuário através de `ContentResolver`. O seletor é iniciado na thread Android e o retorno atualiza a interface pela thread Kivy. Não requer `WRITE_EXTERNAL_STORAGE`, `READ_EXTERNAL_STORAGE` ou `MANAGE_EXTERNAL_STORAGE`.

Cancelar encerra a exportação sem modificar os registros. Se a gravação falhar, o banco permanece intacto, mas o destino pode conter um CSV parcial; o aplicativo informa a falha e permite exportar novamente. Se o Android encerrar o processo durante o seletor, será necessário reiniciar a exportação.

`android.allow_backup = False` desativa o backup automático configurado pelo manifesto. Confirme o manifesto do APK gerado e o comportamento de backup/transferência da versão Android e fabricante; não foi verificado em aparelho.

## Checklist do primeiro APK

- Conferir pacote `org.vitalregistro.vitalregistro`, ícone, versão e ausência de permissões de internet/armazenamento.
- Criar medição fictícia histórica; fechar e reabrir o app; conferir persistência.
- Editar todos os campos e conferir reordenação; cancelar e confirmar exclusão.
- Testar teclado, rolagem, seletores e botão voltar em tela pequena.
- Testar gráficos vazios, uma medição, várias medições e todos os períodos.
- Exportar para Downloads; testar cancelamento, exportações repetidas, UTF-8 e falha de escrita.
- Suspender/retomar o aplicativo, inclusive durante a exportação.

## Fontes oficiais

- [Instalação do Buildozer](https://buildozer.readthedocs.io/en/stable/installation/)
- [Especificações do Buildozer](https://buildozer.readthedocs.io/en/latest/specifications/)
- [APIs Android do python-for-android](https://python-for-android.readthedocs.io/en/latest/apis.html)
- [Storage Access Framework](https://developer.android.com/training/data-storage/shared/documents-files)

Consulte essas fontes ao atualizar SDK, NDK ou p4a. Não resolva falhas adicionando permissões indiscriminadamente ou ignorando códigos de saída.
