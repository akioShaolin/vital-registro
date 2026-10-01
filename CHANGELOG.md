# Changelog

Mudanças relevantes, em estrutura inspirada no Keep a Changelog. A versão 0.1.0 é de desenvolvimento, não estável ou produção.

## [Unreleased]

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

Esses ajustes posteriores ao primeiro APK ainda precisam de nova compilação e teste em aparelho. Versões da cadeia de build e permissões Android preservadas.

## [0.1.0] - 2026-09-30

### Added

- Registro de pressão sistólica/diastólica, pulso, peso decimal e observações.
- Data e horário editáveis, inclusive para medições históricas.
- Persistência local SQLite, histórico, detalhes, edição e exclusão com confirmação.
- Gráficos de pressão, pulso e peso, com períodos de 7 dias, 30 dias e todo o histórico.
- Exportação CSV UTF-8; integração Android por Storage Access Framework implementada.
- Build Android por Google Colab, kernel 3.13.15 e ambiente de compilação isolado.
- Testes de lógica, smoke desktop, CI e documentação do projeto.

### Validated

Confirmado pelo autor em aparelho físico Android 16:

- APK debug ARM64 compilado no Colab e baixado: `vitalregistro-0.1.0-arm64-v8a-debug.apk`, 26.009.326 bytes.
- Instalação e inicialização do aplicativo.
- Criação e persistência de registro.
- Visualização do registro no histórico.
- Abertura da tela de gráficos e representação inicial de uma medição.

Edição/exclusão, exportação CSV no seletor Android, todos os períodos/métricas, teclado e ciclo de vida ainda não foram confirmados em aparelho. Não foi criada release estável automaticamente. Veja [VALIDATION.md](docs/VALIDATION.md).
