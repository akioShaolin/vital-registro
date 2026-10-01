# Changelog

As mudanças relevantes serão registradas aqui, em estrutura inspirada no Keep a Changelog.

## [Unreleased]

### Changed

- Fluxo Colab detecta o kernel e prepara CPython 3.14.7 isolado para build, sem exigir downgrade para 3.12.
- Buildozer e p4a develop fixados em commits; API 36, NDK 29 e Java 17; Python Android/hostpython 3.14.2.
- Notebook aponta para o repositório real, executa testes no Python de build e bloqueia download após falha.
- Testes de seleção de ambiente e falhas adicionados; CI inclui Python 3.14. Build Android completo continua pendente.

### Added

- Implementação inicial em Kivy de cadastro, histórico, detalhes, edição e exclusão com confirmação.
- SQLite local, validações, datas históricas e peso decimal.
- Gráficos por período e exportação CSV; integração Android por seletor de documentos implementada, ainda sem validação em aparelho.
- Testes de lógica, smoke desktop, CI e documentação de contribuição/publicação.
- Configuração Buildozer e notebook Colab, com compilação Android ainda pendente.

Nenhuma release publicada. `0.1.0` é a versão interna inicial do pacote.
