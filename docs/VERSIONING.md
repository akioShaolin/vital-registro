# Versionamento

O VitalRegistro usa `MAJOR.MINOR.PATCH` para a versão do aplicativo. Enquanto estiver em `0.x`, o projeto está em desenvolvimento e pode introduzir incompatibilidades em versões MINOR, sempre destacadas no changelog e nas notas da release. O número da versão não comprova estabilidade nem validação em aparelho.

- **PATCH** (`0.2.1`, por exemplo): correções compatíveis com os dados e fluxos da versão MINOR vigente.
- **MINOR** (`0.2.0`): novos recursos; durante a fase `0.x`, também pode mudar contratos de dados, com incompatibilidades documentadas.
- **MAJOR**: a primeira `1.0.0` deverá declarar os contratos considerados estáveis; depois disso, mudanças incompatíveis nesses contratos exigirão incremento MAJOR. Não há prazo definido para esse marco.

## Por que v0.2.0

A v0.2.0 acrescenta medições independentes, glicemia, seletores rolantes, seleção de pontos nos gráficos e importação CSV com UUID. Também introduz **banco schema 2 e CSV formato 2**, incompatíveis com a v0.1.0. Como o projeto ainda está na fase `0.x`, essa evolução recebe uma nova MINOR. O banco anterior é preservado, mas não há migração nem importação do CSV antigo; o histórico v2 começa separado.

## Identificadores diferentes

| Identificador | v0.2.0 e significado |
| --- | --- |
| Versão do aplicativo | `0.2.0` em `vitalregistro/__init__.py` e `buildozer.spec`; devem concordar. |
| Tag Git | `v0.2.0`: referência ao commit escolhido para fechar a versão. O prefixo `v` não entra no spec. |
| Título da GitHub Release | `VitalRegistro v0.2.0`, associada à tag e acompanhada das notas e dos anexos. |
| Variante do artefato | `debug`, ABI `arm64-v8a`; publicar uma GitHub Release não converte o APK em build Android release assinado para produção. |
| Schema SQLite / formato CSV | `2` / `2`: contratos de armazenamento, independentes da versão do aplicativo. Não aumentam automaticamente a cada release. |
| Python e ferramentas | Versões próprias: local 3.12/3.13; CI de lógica 3.12/3.13/3.14; kernel Colab registrado 3.13.16; build isolado 3.14.7; Python embarcado configurado 3.14.2. |

`v0.2.0` é a tag planejada, sem sufixo `-rc`. Por decisão do autor, será publicada como **Release normal** no GitHub, com a opção **Set as a pre-release** desmarcada. Essa classificação não altera a versão embutida, a variante debug do APK ou o escopo das validações registradas; não cria garantia de estabilidade.

## Commit do build e commit da tag

O [build-info da v0.2.0](releases/v0.2.0/build-info.json) identifica `0835bab79306bbf44bf21954dff897d4f936a562` como commit que produziu o APK. O fechamento documental acontece depois. A tag poderá apontar para o commit final revisado, desde que a diferença em relação ao build seja conferida e não altere o aplicativo ou sua compilação. As notas devem continuar identificando o commit original do APK; não o substitua pelo commit da tag.

Se houver mudança funcional ou de build após esse commit, compile novamente e registre o novo APK e seus metadados antes de publicar. Nunca associe um JSON antigo a outro binário apenas porque têm o mesmo nome. Tags já publicadas não devem ser movidas para corrigir código: prepare uma nova versão. Preserve os metadados históricos e registre correções documentais sem inventar nova validação.

Use [PUBLISHING.md](PUBLISHING.md) para a revisão final. A data do changelog deve ser a data efetiva da publicação, preenchida quando confirmada; a preparação destas notas não publica a versão.
