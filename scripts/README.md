# 🧱 Estrutura

Neste repositório vão estar todas as sources e dados deste projeto.

O repositório está organizado da seguinte forma:

## subpastas

+ `tests/test_validate_mortality.py`: script com testes básicos para validar fiabilidade dos dados:
i) ordem das datas -> verificação se data da linha anterior é o dia anterior, em relação ao da linha actual
ii) colunas -> total de colunas dos ficheiro criados, é igual ao total de colunas identificadas para serem descarregadas
+ `facts/`: factos sobre dados para tentar uma uniformização da leitura dos dados (ex: designação dos concelhos)    

## dados do site SICO-eVM

Contém os ficheiros, com os dados extraidos automaticamente do site [SICO-eVM](https://evm.min-saude.pt/#shiny-tab-dashboard) 

+ `mortalidade.csv`: dados gerais de mortalidade, sob diversas perspectivas, agrupados por dia-mes-ano (DD-MM-YYYY). São descarregados todas as madrugadas, os dados até ao dia anterior.
Dicionário de dados em dicionariodados_mortalidade.md
+ `mortalidade_concelhos.csv`: dados de mortalidade por concelho, agrupados por semana-ano (WK-YYYY). São descarregados todas as madrugadas, os dados até ao dia anterior.
Dicionário de dados em dicionariodados_mortalidade_concelhos.md

## outros

+ `scripts/scraping.py` : script python para fazer scraping dos dados e exportá-los para ficheiro(s) mortalidade.csv e mortalidade_concelho.csv
+ `scripts/requirements.txt` : dependencias dos pacotes python a instalar