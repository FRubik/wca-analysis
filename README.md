# WCA Brazil Events Analysis

Análise exploratória dos eventos da World Cube Association (WCA) realizados no Brasil utilizando DuckDB, Python e Plotly.

## Objetivo

O objetivo deste projeto é analisar a evolução das modalidades oficiais da WCA no Brasil ao longo dos anos e responder perguntas como:

* Quais modalidades são mais comuns em competições brasileiras?
* Como a disponibilidade dos eventos evoluiu ao longo do tempo?
* Qual a probabilidade de encontrar uma determinada modalidade em uma competição?
* Como o crescimento das modalidades se relaciona com o crescimento do número de competições realizadas no país?

## Fonte dos Dados

Os dados utilizados foram obtidos a partir do export oficial da WCA:

https://www.worldcubeassociation.org/export/results

O projeto utiliza os arquivos TSV disponibilizados pela WCA e realiza consultas locais utilizando DuckDB.

## Tecnologias Utilizadas

* Python
* DuckDB
* Pandas
* Plotly

## Estrutura do Projeto

```text
.
├── data/
│   └── WCA_export_*.tsv
├── notebooks/
│   └── analysis.ipynb
├── outputs/
│   └── index.html
├── README.md
└── requirements.txt
```

## Principais Análises

### Número de Competições por Ano

Avaliação da evolução do número de competições realizadas no Brasil desde o início das atividades da WCA no país.

### Popularidade das Modalidades

Contagem do número de competições que incluíram cada modalidade oficial ao longo dos anos.

### Disponibilidade dos Eventos

Cálculo da proporção de competições brasileiras que oferecem cada modalidade, permitindo estimar a chance de um competidor encontrar determinado evento em uma competição aleatória.

## Metodologia

As consultas são realizadas diretamente sobre os arquivos TSV utilizando DuckDB.

Exemplo simplificado:

```sql
SELECT
    e.name,
    COUNT(DISTINCT c.id) AS num_competitions
FROM competitions c
JOIN results r
    ON r.competition_id = c.id
JOIN events e
    ON e.id = r.event_id
GROUP BY e.name;
```
## Resultados

Os gráficos interativos são gerados com Plotly e podem ser exportados para HTML para publicação via GitHub Pages.

## Licença

Os dados pertencem à World Cube Association (WCA).

Este repositório tem finalidade exclusivamente educacional e analítica.
