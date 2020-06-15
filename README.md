# 😷️🇵🇹 Dados da SICO-eVM (plataforma de vigilância da mortalidade)

## 🤔 Contexto: 
Os dados de mortalidade têm uma extrema importância para entender o impacto da pandemia do COVID-19 em Portugal. No [Sistema de Informação dos Certificados de Óbito - e-Vigilância de Mortalidade](SICO-eVM - https://evm.min-saude.pt/) são disponibilizados dados sobre a mortalidade em Portugal, mas sem uma estrutura e dicionário de dados associados.

Mais informações disponíveis no issue #48.

## 🥅 Objetivo:
Criar uma pipeline de extração diária de dados do portal SICO-eVM com um dicionário de dados associados.

## 👥 Equipa:
* [Nuno Pires](https://github.com/piresn)
* [Paulo Silva](https://github.com/paulo-jsilva)
* [Filipe Barroso](https://github.com/OldMetalmind)

## 🎯 Resultado final esperado: 
Criação de um conjunto de ficheiros `.csv` e dicionários de dados com fontes que os voluntários considerem relevantes para estudos do impacto do COVID-19 na mortalidade em Portugal.

## 🧱 Principais etapas:
- Criar um script para extração de dados para um ficheiro `.csv com dados que considerem relevantes do portal SICO-eVM 
    - Mortalidade Geral, Portugal
    - Mortalidade por região de saúde
    - Óbitos por 100 000 habitantes
    - (...)
-  Criar um dicionário de dados (tabela em Markdown ou ficheiro `.csv`) com o significado de cada variável .
- Criar um script para atualizar diariamente estes dados, com uma lógica semelhante ao que temos feito no repositório (usando o Github Actions).
- Criar um script de teste para testar a validade dos dados e o funcionamento do script, com os testes que considerarem relevantes.
- Incluir os scripts no workflow atual.

## 🌍 Sobre a Data Science for Social Good Portugal

A [Data Science for Social Good Portugal](https://www.dssg.pt) é uma comunidade aberta de cientistas de dados, amantes de dados e entusiastas de dados que querem atacar problemas que importam verdadeiramente. Acreditamos no poder dos dados para transformar a nossa sociedade para o melhor e para todos.

[@dssgPT](https://twitter.com/dssgpt) | [fb.com/DSSGPortugal](https://www.facebook.com/DSSGPortugal/) | [Instagram @dssg_pt](www.instagram.com/dssg_pt/) | [LinkedIn](https://www.linkedin.com/company/dssg-portugal)
