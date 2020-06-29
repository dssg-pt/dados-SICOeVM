# 🧱 Estrutura

Em /extra/mortalidade vão estar todas as sources e dados deste miniprojecto

O repositório está organizado da seguinte forma:
+ `testes/`: Dados extraídos do site e scripts para realizar testes
+ `dadosSICO-eVM/` : Dados extraídos automaticamente do site (github actions)  

## Testes

Contém: 

+ `mortalidade_ddmmyyyy.csv`: exemplo de output de dados extraidos do site SICO-eVM para efeitos de testes, agrupadas por dia-mes-ano (DD-MM-YYYY) (consultar dicionário de dados) 
+ `mortalidade_wkyyyy.csv`: exemplo de output de dados extraidos do site SICO-eVM para efeitos de testes, agrupadas por semana-ano (WK-YYYY) (consultar dicionário de dados)  

Nota: outros ficheiros poderão ser criados em função do tipo de agrupamento temporal (...; dia ; semana ; mês; ano; ...) 

## dadosSICO-eVM

Contém os ficheiros com os dados extraidos automaticamente do site [SICO-eVM](https://evm.min-saude.pt/#shiny-tab-dashboard)

+ `dicionariodeados_ddmmyyyy.md` : dicionário de dados com todas as variáveis agrupadas por dia-mes-ano (DD-MM-YYYY)
+ `dicionariodeados_wkyyyy.md` : dicionário de dados com todas as variáveis agrupadas por semana-ano (WK-YYYY)
+ `scraping.py` : script python para fazer scraping dos dados e exportá-los para ficheiro(s) .csv 

+ `mortalidade_ddmmyyyy.csv`: output de dados diários (DD-MM-YYYY), extraidos do site (consultar dicionário de dados) 
+ `mortalidade_wkyyyy.csv`: output de dados semanais (WK-YYYY), extraidos do site (consultar dicionário de dados)
