# 😷️ Dados da SICO-eVM (plataforma de vigilância da mortalidade)

## 🤔 Contexto
Os dados de mortalidade têm uma extrema importância para entender o impacto da pandemia do COVID-19 em Portugal. No [Sistema de Informação dos Certificados de Óbito - e-Vigilância de Mortalidade](https://evm.min-saude.pt/) são disponibilizados dados sobre a mortalidade em Portugal, mas sem uma estrutura e dicionário de dados associados.

Mais informações disponíveis no issue #48.

## 🥅 Objetivo
Criar uma pipeline de extração diária de dados do portal SICO-eVM com um dicionário de dados associados.

## 👥 Equipa
* [Nuno Pires](https://github.com/piresn)
* [Paulo Silva](https://github.com/paulo-jsilva)
* [Filipe Barroso](https://github.com/OldMetalmind)

## 🎯 Resultado final
Criação de um conjunto de ficheiros `.csv` e dicionários de dados com fontes que os voluntários considerem relevantes para estudos do impacto do COVID-19 na mortalidade em Portugal.

## 🧱 Principais objectivos
- Criar um script para extração de dados do portal SICO-eVM para dois ficheiros `.csv`, um com variáveis agrupadas por dd-mm-aaaa e outro por sem-aaaa  
- Criar um dicionário de dados (tabela em Markdown) com a descrição de cada variável.
- Criar um script para atualizar diariamente estes dados, com uma lógica semelhante ao que temos feito no repositório (usando o Github Actions).
- Criar um script de teste para testar a validade dos dados e o funcionamento do script, com os testes que considerarem relevantes.
- Incluir os scripts no workflow atual.

# 🧱 Estrutura

O repositório está organizado da seguinte forma:

## subpastas

+ `tests/test_validate_mortality.py`: script com testes básicos para validar fiabilidade dos dados:
i) ordem das datas -> verificação se data da linha anterior é o dia anterior, em relação ao da linha actual
ii) colunas -> total de colunas dos ficheiro criados, é igual ao total de colunas identificadas para serem descarregadas

+ `scripts/facts/`: factos sobre dados para tentar uma uniformização da leitura dos dados (ex: designação dos concelhos)
+ `scripts/logs/`: logs da execução do script de descarregamento dos dados do site SICO-eVM
+ `scripts/reports/`: ficheiros `.json`, organizados por dia com breve resumo do estado da execução da operação descarregamento
+ `scripts/scraping.py`: script python para fazer scraping dos dados e exportá-los para ficheiro(s) mortalidade.csv e mortalidade_concelho.csv
+ `scripts/requirements.txt`: dependencias dos pacotes python a instalar

+ `.github/workflows/mortality_data_extraction.yml`: script github actions 

## dados do site SICO-eVM

Contém os ficheiros, com os dados extraidos automaticamente do site [SICO-eVM](https://evm.min-saude.pt/#shiny-tab-dashboard) 

+ `mortalidade.csv`: dados gerais de mortalidade, sob diversas perspectivas, agrupados por dia-mes-ano (DD-MM-YYYY). São descarregados todas as madrugadas, os dados até ao dia anterior. Respectivo dicionário de dados em `dicionariodados_mortalidade.md`
+ `mortalidade_concelhos.csv`: dados de mortalidade por concelho, agrupados por semana-ano (WK-YYYY). São descarregados todas as madrugadas, os dados até ao dia anterior. Respectivo dicionário de dados em `dicionariodados_mortalidade_concelhos.md`

### pressupostos associados aos dados descarregados
+ script de extracção dos dados é executado, por uma vez, na madrugada de todos os dias
+ ficheiros `.csv` são recriados todos os dias com os dados existentes no site SICO-eVM. Segundo este site `Os dados apresentados são atualizados automaticamente a cada 10 minutos com base na informação recolhida pelo Sistema de Informação dos Certificados de Óbito (SICO). São dados provisórios e as atualizações efetuadas podem afetar qualquer dia dos dois últimos anos apresentados.`
+ ficheiros `.csv` gerados, correspondem aos dados existentes no site SICO-eVM, até ao dia anterior em que script está a ser executado  
+ selecção do grupo de variáveis a descarregar, corresponde ao tipo de dados, que podem estar relacionados com o ambito deste projecto   

## 🌍 Sobre a Data Science for Social Good Portugal

A [Data Science for Social Good Portugal](https://www.dssg.pt) é uma comunidade aberta de cientistas de dados, amantes de dados e entusiastas de dados que querem atacar problemas que importam verdadeiramente. Acreditamos no poder dos dados para transformar a nossa sociedade para o melhor e para todos.

[@dssgPT](https://twitter.com/dssgpt) | [fb.com/DSSGPortugal](https://www.facebook.com/DSSGPortugal/) | [Instagram @dssg_pt](www.instagram.com/dssg_pt/) | [LinkedIn](https://www.linkedin.com/company/dssg-portugal)
