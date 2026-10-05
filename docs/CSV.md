# CSV e persistência — v0.2.0

## Schema 2

Uma tabela `measurements` guarda `id` (UUID textual canônico, chave primária), `measured_at` (ISO local), `kind`, `note` e campos específicos opcionais. `PRAGMA user_version = 2`; índice por timestamp. Uma tabela é suficiente para três tipos pequenos e facilita histórico geral e transações. Modelos e CHECKs SQLite exigem os campos do tipo e rejeitam campos de outros tipos.

- `pressao`: `systolic`, `diastolic`, `pulse` inteiros, em mmHg/mmHg/bpm.
- `peso`: `weight` Decimal, armazenado como texto para preservar precisão.
- `glicemia`: `glucose` inteiro em mg/dL e `context` obrigatório.

UUID é criado uma vez, preservado na edição/exportação/importação. Tipo não pode mudar na edição. Cada medição tem timestamp independente; não há periodicidade obrigatória. Empates temporais são ordenados por UUID para resultados determinísticos, não por ordem de inserção.

O aplicativo usa `vitalregistro-v2.sqlite3`. O arquivo antigo `vitalregistro.sqlite3` permanece intacto e provoca um aviso na inicialização. Não existe migração, conversão ou importação de dados v0.1.0. Um banco de schema incompatível ou inválido no caminho v2 produz erro sem apagar/recriar o arquivo. Desinstalar/limpar dados não é um procedimento de migração e pode remover ambos os históricos.

## Contrato CSV formato 2

UTF-8 (BOM opcional na leitura), vírgula como separador, quoting padrão de `csv`, cabeçalho exato e ordenado:

```text
formato,id,tipo,timestamp,sistolica,diastolica,pulso,peso,glicemia,contexto,observacao
```

Exemplos fictícios:

```csv
formato,id,tipo,timestamp,sistolica,diastolica,pulso,peso,glicemia,contexto,observacao
2,00000000-0000-4000-8000-000000000001,pressao,2026-10-05T08:12,151,86,74,,,,"Medição fictícia, pela manhã"
2,00000000-0000-4000-8000-000000000002,peso,2026-10-03T07:45,,,,104.2,,,
2,00000000-0000-4000-8000-000000000003,glicemia,2026-10-05T07:30,,,,,96,jejum,
```

`formato` vale `2` em cada linha. `id` é UUID canônico minúsculo com hífens. `timestamp` segue exatamente `AAAA-MM-DDTHH:MM`, sem segundos ou fuso. É o horário local informado, não um instante convertido para UTC. Viagens/fusos não alteram os valores. Exportação usa ordem cronológica crescente.

Campos irrelevantes ao tipo ficam vazios, não zero. Pressão/pulso/glicemia são inteiros positivos. Peso usa ponto decimal, até três casas, sem notação exponencial no CSV. Os limites técnicos de digitação são: sistólica 1–400, diastólica 1–300, pulso 1–350, peso >0 até 700 kg, glicemia 1–2000 mg/dL. Esses limites não classificam resultados nem têm significado de diagnóstico.

Contextos usam códigos estáveis separados dos rótulos:

| Código | Rótulo |
| --- | --- |
| `jejum` | Jejum |
| `antes_refeicao` | Antes da refeição |
| `apos_refeicao` | Após a refeição |
| `outro` | Outro |

A estrutura central `CONTEXTS` permite adicionar códigos em futuras versões, acompanhados de atualização da restrição SQLite e documentação. Códigos desconhecidos são rejeitados por esta versão. Não há cálculo automático de tempo após refeição. Observações são opcionais, até 5000 caracteres, sem NUL. Vírgulas, aspas e quebras de linha são preservadas pelo módulo `csv`; não divida o arquivo manualmente por vírgula ou linha.

## Prévia, duplicatas e transação

1. Selecionar o arquivo não altera o banco. Leitura limitada a **10 MiB** e **20.000 linhas de dados**. Arquivos maiores são recusados; um histórico exportado acima desses limites precisa ser dividido preservando o cabeçalho e os UUIDs antes da importação.
2. UTF-8, cabeçalho, versão, quantidade de colunas, UUID, tipo, timestamp, contexto e campos são validados. Um registro CSV com observação multilinha conta como uma linha de dados; erros indicam a linha física final lida. Erro estrutural de quoting interrompe a leitura e bloqueia o lote.
3. A prévia mostra registros novos válidos, duplicatas idênticas, conflitos e erros. Qualquer erro/conflito bloqueia o lote inteiro; não há importação parcial. Corrija o arquivo e selecione-o novamente. Cancelar não grava.
4. Mesmo UUID e todos os valores iguais: duplicata ignorada, inclusive dentro do arquivo. Decimal numericamente igual é equivalente (por exemplo, `70.5` e `70.500`).
5. Mesmo UUID com conteúdo diferente: conflito. Nenhum registro é sobrescrito automaticamente. Uma cópia exportada antes de uma edição pode conflitar com o registro editado; conserve a versão desejada antes de importar. Não troque UUID para contornar conflitos sem querer criar outra medição.
6. UUIDs diferentes são medições diferentes, mesmo com timestamp/valores iguais. Não se usa comparação frágil de texto para deduplicação. CSV não é sincronização: reimportar uma cópia antiga pode restaurar registros já excluídos.
7. Confirmar inicia `BEGIN IMMEDIATE`, revalida UUIDs dos registros a inserir sob bloqueio de escrita e grava tudo em uma transação. Falha de SQL ou conflito implica rollback; não há commit parcial.

O round-trip preserva UUID, timestamp, tipo, valores, contexto e observação. Importar em um banco vazio restaura as medições do CSV. Reimportar o mesmo CSV no mesmo banco não duplica o histórico. O arquivo é uma cópia portátil escolhida pelo usuário, sem backup automático, conta ou nuvem obrigatória.

## Interface e Android

`ACTION_CREATE_DOCUMENT` exporta e `ACTION_OPEN_DOCUMENT` seleciona a importação, sem permissões amplas. A leitura SAF ocorre em thread auxiliar, com limite de bytes e fechamento do stream; prévia e confirmação retornam à thread Kivy. O filtro de seleção Android aceita qualquer MIME porque provedores identificam CSV de formas diferentes; o conteúdo continua estritamente validado. Desktop usa seletor Kivy.

O código de importação usa cópia de arrays mutáveis documentada no [Pyjnius](https://pyjnius.readthedocs.io/en/latest/api.html#passing-variables-by-reference-or-by-value). O SAF real permanece pendente de teste Android.

Seletores de data/hora usam [RecycleView do Kivy](https://kivy.org/doc/stable/api-kivy.uix.recycleview.html), com linhas de 48 dp, coluna de anos 1–9999 virtualizada e encaixe no valor central. Datas inválidas são ajustadas ao último dia válido do mês. Gráficos usam timestamp completo com precisão de minuto; tolerância de seleção de 24 dp e distância euclidiana, sem alterar os dados. Empates exatos abrem uma lista para escolher série/medição. As cores identificam séries, nunca condições clínicas.
