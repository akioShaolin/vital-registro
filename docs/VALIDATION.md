# Validação — primeiro APK e revisão posterior

## Evidência em aparelho fornecida pelo autor

Marco em **30/09/2026**, APK `vitalregistro-0.1.0-arm64-v8a-debug.apk`, **26.009.326 bytes**. Compilação e download pelo Google Colab com kernel **Python 3.13.15**; instalação e uso em **Android 16 físico**. Modelo não informado. As [quatro capturas](screenshots/README.md) contêm dados fictícios confirmados pelo autor.

| Funcionalidade | Evidência |
| --- | --- |
| Build debug ARM64 no Colab e download | Confirmados pelo autor |
| Instalação e inicialização no Android 16 | Confirmadas pelo autor; Home capturada |
| Criação e persistência de registro | Confirmadas pelo autor |
| Histórico e apresentação compacta | Confirmados pelo autor e captura |
| Abrir gráficos e representar uma medição | Confirmados pelo autor e captura |

O relato do autor comprova esse marco; não equivale a teste independente de todas as funcionalidades. Não foi recebido o APK/log original para inspecionar manifesto, calcular hash ou recuperar o HEAD p4a efetivo. Os commits **configurados** estão em [ANDROID.md](ANDROID.md). O notebook registra a proveniência efetiva nos próximos builds.

## Verificações locais da revisão posterior

Executadas no Windows com Python 3.13.3 e Kivy 2.3.1; a suíte independente também é executável no Python de build. Nenhuma nova compilação Android foi feita nesta revisão.

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

## Pendente no próximo APK

- Confirmar a transparência no launcher e a Home após reconstruir o APK.
- Conferir topo/rodapé, Cancelar totalmente acessível, rolagem e foco com teclado aberto em Android 16; testar gestos e navegação por botões.
- Testar edição de **todos** os campos, reordenação histórica e cancelamento/confirmação de exclusão.
- Conferir sistólica/diastólica, pulso e peso, múltiplas medições e todos os períodos no aparelho.
- Exportar pelo SAF para um destino local; conferir UTF-8, vírgulas, aspas e quebras de linha; cancelar e exportar novamente.
- Suspender/retomar e encerrar o processo, inclusive com formulário e seletor abertos.
- Inspecionar manifesto final e comportamento do backup/transferência do fabricante.

As correções de layout dependem de APIs Android e ainda precisam dessa verificação real. APK debug funcional não é sinônimo de release estável ou cobertura completa de dispositivos.
