# Validação — v0.1.0

## Evidência em aparelho fornecida pelo autor

Primeiro marco funcional em **30/09/2026**. Para o fechamento, o autor forneceu o [build-info.json](releases/v0.1.0/build-info.json) do APK `vitalregistro-0.1.0-arm64-v8a-debug.apk`, **26.306.986 bytes**, **DEBUG + ARM64-V8A**. Ambiente Colab Python **3.13.15**, Python de build **3.14.7**, API **36** e NDK **29**; commits e SHA-256 informado estão em [ANDROID.md](ANDROID.md#evidência-do-build-da-v010). Instalação e uso confirmados no **Samsung Galaxy M55 com Android 16**. As [quatro capturas históricas](screenshots/README.md) contêm dados fictícios e antecedem os ajustes visuais; não documentam uma nova verificação desses ajustes.

| Funcionalidade | Evidência |
| --- | --- |
| Build debug ARM64 no Colab e download | Confirmados pelo autor |
| Instalação e inicialização no Android 16 | Confirmadas pelo autor; Home capturada |
| Criação e persistência de registro | Confirmadas pelo autor |
| Histórico e apresentação compacta | Confirmados pelo autor e captura |
| Abrir gráficos e representar corretamente uma única medição | Confirmados pelo autor e captura |

O relato do autor registra esse marco; não equivale a teste independente de todas as funcionalidades. O JSON fornece os commits efetivos do projeto, p4a e Buildozer e o hash informado do artefato. O APK não foi inspecionado nem seu hash recalculado nesta revisão documental. Não foi executado novo build nesta tarefa.

## Verificações locais anteriores ao fechamento documental

Resultados registrados na revisão de código anterior, no Windows com Python 3.13.3 e Kivy 2.3.1; não são testes repetidos neste fechamento documental nem testes de hardware. A suíte independente também é executável no Python de build.

| Verificação | Resultado |
| --- | --- |
| `python -m unittest discover -s tests -v` | 35 testes aprovados |
| `python scripts/smoke_ui.py --screenshot` | Fluxos desktop e renderização da Home aprovados |
| Sintaxe Python, Bash e células do notebook | Verificada localmente |
| `python scripts/check_repository.py` | Auditoria local de candidatos, notebook, ícone e permissões |
| Ícone | RGB original preservado byte a byte; canal alfa corrigido; Home conferida no desktop |
| `.gitignore` | SQLite, CSVs de runtime, APK, ferramentas e caches excluídos; capturas fictícias permitidas |

Os testes de dados cobrem CRUD, persistência, edição de todos os campos, reordenação por data/hora histórica, datas inválidas e bissextas, peso decimal, rollback e CSV UTF-8 com vírgulas, aspas e quebras de linha. Não foi necessário duplicar esses testes.

Os testes novos verificam o cálculo da sobreposição de barras/teclado sem margem duplicada e os estados do adaptador SAF: criação do documento, UTF-8, cancelamento, repetição, operação concorrente, falhas de escrita, abertura e registro de callback. **Java, Activity e seletor são simulados**; isso não valida o SAF real no aparelho.

O smoke usa apenas dados fictícios temporários e exercita detalhes/edição, gráficos vazios, uma e múltiplas medições, pressão/pulso/peso, períodos 7/30/todos, seletores, exportações repetidas e exclusão. Os testes de seleção do Python usam subprocessos simulados, separados da evidência do build fornecida pelo autor.

## Pendente de validação em aparelho

- Confirmar a transparência no launcher e a aparência da Home no APK com os ajustes.
- Conferir topo/rodapé, Cancelar totalmente acessível, rolagem e foco com teclado aberto em Android 16; testar gestos e navegação por botões.
- Testar edição de **todos** os campos, reordenação histórica e cancelamento/confirmação de exclusão.
- Conferir sistólica/diastólica, pulso e peso, múltiplas medições e todos os períodos no aparelho.
- Exportar pelo SAF para um destino local; conferir UTF-8, vírgulas, aspas e quebras de linha; cancelar e exportar novamente.
- Suspender/retomar e encerrar o processo, inclusive com formulário e seletor abertos.
- Inspecionar manifesto final e comportamento do backup/transferência do fabricante.

As correções de layout dependem de APIs Android e ainda precisam dessa verificação real. APK debug funcional não é sinônimo de release estável ou cobertura completa de dispositivos.
