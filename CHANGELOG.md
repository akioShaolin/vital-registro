# Changelog

Mudanças relevantes, em estrutura inspirada no Keep a Changelog. A versão 0.1.0 é de desenvolvimento, não estável ou produção.

## [Unreleased]

Preparação da **v0.2.0**, sem commit/tag/release criados por esta implementação. A seção histórica v0.1.0 abaixo foi preservada.

### Added

- Medições independentes de pressão arterial/pulso, peso e glicemia em mg/dL, com timestamps próprios e contextos de glicemia.
- Escolha de tipo, formulários específicos e histórico geral filtrável, com edição e exclusão por registro.
- Gráfico de glicemia e seleção por toque/clique dos pontos de todas as métricas, com tolerância e identificação da série; escolha explícita em sobreposições exatas.
- Seletores rolantes reutilizáveis de dia/mês/ano e hora/minuto, sem teclado, com encaixe e correção de dias por mês/ano bissexto.
- CSV formato 2 com UUID persistente, timestamp ISO local e importação via prévia/confirmar; SAF no Android e seletor desktop.
- Detecção de duplicatas idênticas e conflitos de UUID, validação integral antes de gravar e transação com rollback.
- Testes de round-trip, novos tipos, UUID/conflitos, falhas de importação, pickers, seleção de pontos e SAF simulado; smoke desktop ampliado.

### Changed

- Novo schema 2 em `vitalregistro-v2.sqlite3`; banco antigo preservado com aviso, sem migração nem importação de CSV v0.1.0.
- Versão do aplicativo e do pacote Android preparada como 0.2.0. Dependências, SDK/NDK/Java/p4a, permissões e insets preservados.
- Documentação do [CSV e schema](docs/CSV.md), recursos novos e limites de validação.

### Validation

Testes locais e smoke são registrados em [VALIDATION.md](docs/VALIDATION.md). Nenhum build APK v0.2.0 ou teste em hardware Android foi executado nesta implementação.

## [0.1.0] - 2026-09-30

### Fixed

- Fundo externo preto do ícone convertido em transparência, preservando dimensões e canais RGB originais; Home e launcher continuam referenciando o mesmo asset.
- Área de conteúdo ajustada ao espaço ocupado por barras, recortes de tela e teclado Android; margem adicional no fim da rolagem e foco visível no formulário.
- Seletores dos gráficos seguem a paleta existente e não repetem o valor atual no menu.
- Largura do eixo vertical calculada pelas labels; mantido apenas um ponto por série quando há uma medição.
- Falha ao registrar o callback de exportação não deixa a operação permanentemente bloqueada.

### Changed

- README com capturas reais e documentação do armazenamento exclusivamente local.
- Registro separado de evidência Android fornecida pelo autor e verificações locais.
- Notebook salva metadados e hashes dos próximos APKs em `bin/build-info.json`.
- Testes de área segura e adaptação SAF, além de smoke para métricas/períodos e exportações repetidas.

Os ajustes acima constam do commit `895c3dc2a1cff899107797aa92c391f79b14af91`, identificado no build-info fornecido para a v0.1.0. Sua presença no código não comprova validação visual ou de todos os fluxos em aparelho. Versões da cadeia de build e permissões Android preservadas.

### Fechamento documental

- Documentação da v0.1.0 consolidada com Samsung Galaxy M55, ambiente efetivo e cópia do `build-info.json`; sem alterações funcionais ou de dependências.
- Guia de contribuição distingue execução local, CI, kernel Colab, ambiente de build e Python embarcado no APK.

O fechamento documental pertence à v0.1.0, mas é posterior ao commit que produziu o APK acima. O commit de documentação não substitui o commit do build registrado no JSON, nem representa uma nova compilação ou validação em hardware.

### Added

- Registro de pressão sistólica/diastólica, pulso, peso decimal e observações.
- Data e horário editáveis, inclusive para medições históricas.
- Persistência local SQLite, histórico, detalhes, edição e exclusão com confirmação.
- Gráficos de pressão, pulso e peso, com períodos de 7 dias, 30 dias e todo o histórico.
- Exportação CSV UTF-8; integração Android por Storage Access Framework implementada.
- Build Android por Google Colab, kernel 3.13.15 e ambiente de compilação isolado.
- Testes de lógica, smoke desktop, CI e documentação do projeto.

### Validated

Confirmado pelo autor no **Samsung Galaxy M55 com Android 16**:

- APK debug ARM64 compilado no Colab e baixado: `vitalregistro-0.1.0-arm64-v8a-debug.apk`, 26.306.986 bytes, conforme o [build-info.json](docs/releases/v0.1.0/build-info.json).
- Instalação e inicialização do aplicativo.
- Criação e persistência de registro.
- Visualização do registro no histórico.
- Abertura da tela de gráficos e representação correta de um gráfico contendo apenas uma medição.

Edição/exclusão, exportação CSV no seletor Android, todos os períodos/métricas, teclado e ciclo de vida ainda não foram confirmados em aparelho. O artefato é **DEBUG + ARM64-V8A**, primeiro marco funcional, sem indicação de estabilidade ou prontidão para Google Play. Nenhuma tag ou GitHub Release foi criada neste fechamento documental. Veja [VALIDATION.md](docs/VALIDATION.md).
