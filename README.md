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
├── main.py                 # ponto de entrada: gera o index.html
├── wca_report/
│   ├── config.py           # caminhos, recortes e parâmetros do mapa
│   ├── db.py               # conexão DuckDB (materializa os TSVs em tabelas)
│   ├── queries.py          # consultas SQL -> DataFrames
│   ├── charts.py           # figuras Plotly (linhas, presença, etc.)
│   ├── coverage.py         # mapa de cobertura (união de círculos + seletores)
│   └── report.py           # página HTML final com abas
├── tsv/
│   └── WCA_export_*.tsv     # dados oficiais da WCA (não versionados)
├── index.html              # relatório gerado (deploy via GitHub Pages)
├── explore.ipynb           # notebook exploratório original (histórico)
├── requirements.txt
└── README.md
```

## Como gerar o relatório

```bash
pip install -r requirements.txt
python main.py
```

O comando lê os TSVs em `tsv/`, executa as análises e escreve o `index.html`
(página única com abas **Competições** e **Competidores**). Basta versionar o
`index.html` gerado — o GitHub Pages publica o relatório automaticamente.

Parâmetros de análise (anos, recortes geográficos, raios do mapa de cobertura)
ficam centralizados em `wca_report/config.py`.

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
