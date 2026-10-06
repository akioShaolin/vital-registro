# Compilação Android e Google Colab

A revisão atual prepara **v0.2.0**. Somente a versão do aplicativo mudou no spec; a cadeia abaixo permanece fixa. As evidências do APK v0.1.0 são históricas e não validam v0.2.0. Novo banco e CSV incompatíveis com v0.1.0: veja [CSV.md](CSV.md).

## Por que o fluxo mudou

O notebook anterior exigia Python 3.10–3.12 e combinava p4a `master`, API 35 e NDK 25b. Ele interrompia no Python 3.13 do Colab antes de instalar as ferramentas. Remover essa restrição não atualizaria as recipes, o compilador nativo nem as dependências Python.

O Google anunciou a [migração do Colab para Python 3.13](https://github.com/googlecolab/colabtools/issues/6081) em agosto de 2026. Os metadados fornecidos pelo autor registram **Python 3.13.16 no kernel da v0.2.0** e **3.13.15 na v0.1.0**. A primeira célula imprime a versão da sessão real, que pode variar entre imagens.

O fluxo novo separa três interpretadores:

1. **Kernel Colab:** executa o notebook e coordena subprocessos. Permanece com seus pacotes originais.
2. **Python de build:** CPython **3.14.7 com GIL**, em `.venv-build/`, executa Buildozer, p4a e os testes. Se o interpretador inicial não for exatamente esse, uv baixa uma distribuição isolada; não há downgrade do Colab.
3. **Python das recipes p4a:** **3.14.2**, tanto `hostpython3` quanto `python3` embarcado no APK. Esse par deve ter a mesma versão; não é o Python do kernel. Usamos a versão padrão do commit p4a selecionado, sem substituir isoladamente a recipe por outro patch de CPython.

## Combinação selecionada

Esta é a configuração preservada do build bem-sucedido documentado para a v0.1.0. Nenhuma versão de Python, Buildozer, p4a, Kivy, SDK, NDK ou Java foi trocada na implementação v0.2.0.

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

### Evidência do build da v0.2.0

O [JSON fornecido pelo autor](releases/v0.2.0/build-info.json) registra kernel Colab **3.13.16**, Python de build **3.14.7**, API **36**, NDK **29** e os mesmos commits Buildozer/p4a da tabela. O projeto foi compilado no commit `0835bab79306bbf44bf21954dff897d4f936a562`. O artefato `vitalregistro-0.2.0-arm64-v8a-debug.apk` tem **26.326.438 bytes**, segundo o JSON. SHA-256 informado e limites estão nas [notas da release](releases/v0.2.0/RELEASE_NOTES.md).

Java, Kivy, Python embarcado e API mínima acima são dados da configuração; o JSON não atesta diretamente todos esses componentes. Não foi executado build nem recalculado o hash nesta revisão. A documentação de fechamento é posterior ao commit que produziu o APK.

### Evidência do build da v0.1.0

O [build-info.json fornecido pelo autor](releases/v0.1.0/build-info.json) foi preservado sem alterações como registro do ambiente efetivamente utilizado. Ele identifica:

| Campo | Valor registrado |
| --- | --- |
| Kernel Colab | Python 3.13.15 |
| Python de build | Python 3.14.7 |
| Commit do projeto | `895c3dc2a1cff899107797aa92c391f79b14af91` |
| Commit p4a | `e772ad93f20a61c0bbe1cf8955e073cfb41062e1` |
| Commit Buildozer | `a153097b3c534bea8a17da2abf1369d67c8cbfcb` |
| Android API / NDK | 36 / 29 |
| APK | `vitalregistro-0.1.0-arm64-v8a-debug.apk` |
| Tamanho | **26.306.986 bytes** |
| SHA-256 informado | `259866134942d6990cf9f157603e3f024538b1101006a633fda633d5d386765a` |

O JSON também guarda a lista efetiva de pacotes Python do ambiente de build. Java 17, Kivy 2.3.1, Python embarcado 3.14.2 e API mínima 24 são escolhas da configuração preservada; o JSON não registra diretamente todos esses componentes. Não é um inventário completo do sistema nem garantia de reprodução binária idêntica.

O autor confirmou instalação e inicialização no **Samsung Galaxy M55 com Android 16**, criação e persistência local, histórico, abertura de gráficos e representação correta de uma única medição. O APK permanece **DEBUG + ARM64-V8A**. O binário não foi inspecionado nem seu hash recalculado nesta revisão documental; tamanho e SHA-256 acima foram transcritos do JSON, não obtidos de uma compilação executada aqui.

As [capturas históricas](screenshots/README.md) antecedem as correções visuais incluídas no commit identificado. Não devem ser usadas para afirmar que transparência, áreas seguras, teclado ou exportação foram testados no artefato de 26.306.986 bytes. Consulte [VALIDATION.md](VALIDATION.md) para o escopo confirmado.

A v0.1.0 já foi publicada, conforme informado pelo autor. Preserve o JSON junto ao artefato correspondente. A v0.2.0 tem [seu próprio JSON](releases/v0.2.0/build-info.json); não reutilize hashes ou evidências da v0.1.0. Em novas compilações, preserve os metadados correspondentes ao novo artefato. Nenhuma publicação é feita nesta implementação.

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

O aplicativo permanece offline. `android.permissions` continua vazio, `android.allow_backup = False` e o seletor CSV usa `ACTION_CREATE_DOCUMENT` para exportar e `ACTION_OPEN_DOCUMENT` para importar. Não adicionamos internet nem permissões amplas de armazenamento. A rede é necessária somente para obter as ferramentas e dependências **durante o build**.

## Validação e limites

Testes de lógica e seleção de ambiente podem ser executados localmente sem SDK. Os testes da preparação usam subprocessos simulados para verificar a escolha do Python e a propagação de falhas; não provam compilação nativa.

**O build Colab e o uso básico no Samsung Galaxy M55 com Android 16 foram confirmados pelo autor.** Essa evidência refere-se à v0.1.0. Para a v0.2.0, o autor forneceu metadados do build e capturas Android; nesta revisão não houve nova compilação, inspeção do APK ou teste em hardware. Buildozer master e p4a develop continuam sendo versões de desenvolvimento, mesmo fixadas em commits; futuros builds e novos ambientes exigem nova verificação. Consulte [VALIDATION.md](VALIDATION.md).

Na próxima rodada de testes em aparelho, confira o ícone do launcher, margens de status/navegação, formulário e teclado, edição/exclusão, todos os gráficos/períodos, exportação/cancelamento e suspensão/retomada. A exportação SAF está implementada e revisada, mas ainda não foi confirmada em aparelho. Publicação na Play Store continua fora deste fluxo debug.

## Checklist Android v0.2.0

- Conferir instalação/upgrade e aviso do banco antigo preservado, com histórico v2 separado.
- Criar, editar e excluir os três tipos, incluindo vírgula decimal e contextos de glicemia.
- Rolar dia/mês/ano, ano bissexto e hora/minuto; confirmar/cancelar sem abrir teclado.
- Tocar pontos próximos e sobrepostos de ambas as séries de pressão, pulso, peso e glicemia; conferir data/hora, tolerância e fechamento do rótulo.
- Exportar e importar pelo SAF, cancelar e repetir; verificar UTF-8/multilinha, round-trip, duplicatas e conflitos sem sobrescrita.
- Conferir insets, teclado, navegação por gestos/botões, suspensão/retomada e encerramento durante o seletor.

O seletor SAF pode perder uma operação pendente se o Android encerrar o processo. Se isso ocorrer, selecione o arquivo novamente; a prévia não grava e os UUIDs protegem contra reimportação idêntica.
