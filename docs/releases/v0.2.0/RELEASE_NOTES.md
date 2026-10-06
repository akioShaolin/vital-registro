# VitalRegistro v0.2.0

Versão de desenvolvimento **DEBUG + ARM64-V8A**, preparada para publicação como **Release normal** no GitHub. Data de publicação definida pelo autor: **06/10/2026**. A publicação no GitHub não foi executada nesta preparação. Não é um pacote de produção para Google Play.

## Novidades

- Medições independentes de pressão arterial/pulso, peso e glicemia em mg/dL, com data, horário e observações próprios.
- Formulários por tipo e histórico geral filtrável, com edição e exclusão por registro.
- Contextos de glicemia: Jejum, Antes da refeição, Após a refeição e Outro.
- Seletores rolantes de data e horário, incluindo ajuste de dias por mês e ano bissexto.
- Gráfico de glicemia e seleção de pontos em todas as métricas, com valor, série, data/hora e escolha em sobreposições exatas.
- CSV formato 2: UUID persistente, timestamp local e importação com prévia e confirmação. Duplicatas idênticas são ignoradas; erros ou conflitos bloqueiam o lote inteiro, sem sobrescrever registros.

O aplicativo continua offline, com SQLite local, sem conta, telemetria ou novas permissões Android. Não interpreta clinicamente as medições.

## Atenção ao atualizar da v0.1.0

**Banco e CSV mudaram de formato.** A v0.2.0 usa `vitalregistro-v2.sqlite3` (schema 2) e inicia um histórico separado. O banco anterior permanece intacto, com aviso ao detectá-lo, mas não existe migração nem importação de CSV v0.1.0. Não desinstale nem limpe os dados para fazer essa transição. Exporte e guarde os dados antigos antes de atualizar; o CSV antigo serve como cópia externa, não como entrada para o importador v2.

Importar acrescenta registros; não sincroniza edições ou exclusões. Um registro excluído pode reaparecer ao importar uma cópia antiga. Limites: 10 MiB e 20.000 linhas de dados por arquivo. Consulte o [formato CSV](https://github.com/akioShaolin/vital-registro/blob/v0.2.0/docs/CSV.md).

## Artefato e rastreabilidade

Anexos previstos: `vitalregistro-0.2.0-arm64-v8a-debug.apk` e `build-info.json` correspondente.

| Campo | Registro fornecido pelo autor |
| --- | --- |
| APK | `vitalregistro-0.2.0-arm64-v8a-debug.apk` |
| Tamanho | 26.326.438 bytes |
| SHA-256 | `ce8a592d5485ae328335a7e03aa9a566356fd6cf65fdbbee8410377e1158a202` |
| Commit que produziu o APK | `0835bab79306bbf44bf21954dff897d4f936a562` |
| Kernel Colab / Python de build | 3.13.16 / CPython 3.14.7 |
| Buildozer | commit `a153097b3c534bea8a17da2abf1369d67c8cbfcb` |
| python-for-android | develop, commit `e772ad93f20a61c0bbe1cf8955e073cfb41062e1` |
| Android API / NDK | 36 / 29 |

A configuração mantém Java 17, Kivy 2.3.1, Pyjnius 1.7.0, Python embarcado/hostpython 3.14.2 e mínimo API 24 (Android 7). Esses componentes vêm da configuração, não de inspeção independente do APK. O JSON não é um inventário completo do sistema nem garante reprodução binária idêntica.

O fechamento documental é posterior ao commit do build. A tag deverá identificar o commit final revisado; isso não muda a origem do APK acima. O binário não foi inspecionado nem seu hash recalculado nesta revisão. Antes de anexá-lo, confira tamanho e SHA-256 contra o JSON.

## Evidências e limites

- Verificação local registrada em 05/10/2026: 66 testes aprovados no Windows/Python 3.13.3, sintaxe, auditoria do repositório e smoke desktop com Kivy 2.3.1.
- Metadados do build fornecidos pelo autor e preservados com esta versão.
- Capturas Android com dados fictícios autorizados mostram formulários, histórico, seletores, gráficos, tooltip e prévias de importação. Não identificam por si só o hash do APK nem comprovam confirmação da importação, persistência após reinício ou rollback.
- Permanecem pendentes a validação completa em aparelho, upgrade com preservação do banco antigo, round-trip real pelo SAF, todos os gestos/períodos, teclado/insets, ciclo de vida e inspeção do manifesto final. A validação histórica da v0.1.0 no Samsung Galaxy M55/Android 16 não valida automaticamente a v0.2.0.

Veja a [galeria](https://github.com/akioShaolin/vital-registro/blob/v0.2.0/docs/screenshots/v0.2.0/README.md), o [registro de validação](https://github.com/akioShaolin/vital-registro/blob/v0.2.0/docs/VALIDATION.md) e a [política de versionamento](https://github.com/akioShaolin/vital-registro/blob/v0.2.0/docs/VERSIONING.md). Os links com a tag passam a funcionar após sua publicação.
