# tcc-puc-bia
TCC PUC Minas - Business Intelligence and Analytics

Para maiores detalhes sobre o projeto leia o Relatório Técnico no diretório `docs`.

O dashboard está disponível na área [pública do Tableau](https://public.tableau.com/app/profile/alessandro.lemser).

# CSV dataset

O dataset em formato CSV está disponível no diretório `data`.

Trata-se do resultado uma execução dos scripts Python disponíveis neste repositório.

Para saber como gerar o dataset leia as instruções abaixo.

# Gerando o dataset

## Pré-requisitos

### Docker

É preciso ter o Docker instalado para executar os scripts, pois a base de dados é fornecida numa imagem.

### Python 3

Para a execução dos scripts de ETL é preciso ter o Python3 instalado (juntamente com o pip3).

## Preparando o ambiente para execução

Para executar os scripts de ETL é necessário colocar o banco de dados no ar (docker), obter as bibliotecas requeridas
pelos scripts (requirements.txt) e executar os scripts.

### Banco de dados

O banco de dados é provido via Docker e usa a [imagem oficial](https://hub.docker.com/_/postgres).

A configuração abaixo foi baseada no nas orientações [deste site](https://hackernoon.com/dont-install-postgres-docker-pull-postgres-bee20e200198) e pode ser usada como referência para casos de dúvidas adicionais.

Para iniciar o banco de dados execute:

#### Linux/Mac

```
mkdir -p $HOME/docker/volumes/postgres
docker pull postgres
docker run --rm --name pg-docker -e POSTGRES_PASSWORD=docker -e POSTGRES_USER=postgres -d -p 6432:5432 -v $HOME/docker/volumes/postgres:/var/lib/postgresql/data postgres
```

#### Windows

```
mkdir %HOMEDRIVE%%HOMEPATH%/docker/volumes/postgres
docker pull postgres
docker run --rm --name pg-docker -e POSTGRES_PASSWORD=docker -d -p 5432:5432 -v %HOMEDRIVE%%HOMEPATH%/docker/volumes/postgres:/var/lib/postgresql/data postgres
```

> Nota: Os comandos para Windows não foram testados, porém, exceto pelo comando `mkdir`, os demais comandos são padrões do Docker. Caso tenha dificuldades, por favor, revise as variáveis `%HOMEDRIVE%` e `%HOMEPATH%`.

### Bibliotecas Python requeridas

Para instalar as bibliotecas requeridas execute:

`pip3 install -r requirements.txt`

### Scripts Python

1. Crie as tabelas do modelo relacional e dimensional

`python3 main.py preload`

2. Execute o script de coleta de dados no Flickr e processamento do EXIF

`python3 main.py`

# Detalhes dos scripts

O script principal `main.py` está preparado para ser executado mais de uma vez sem prejuízo relacionado a dados duplicados ou perda de processamento.

Numa primeira etapa as URLs das imagens são armazenadas na tabela `f_fotografias` pelo script `image_url_extractor.py`.

Em paralelo, uma thread (`exif_worker.py`) busca as URLs na tabela `f_fotografias` e lê a imagem para extrair o EXIF. Ao ler o EXIF com sucesso o registro relativo à URL é atualizado na tabela `f_fotografias` e mercado como processado (`fl_lido=True`).

Mesmo que o processamento seja abortado no meio e reiniciado posteriormente, não haverá prejuízo para o trabalho já feito.

Ao final do carregamento dos dados de EXIF o script `load_dw.py` povoa a base dimensional.

Uma última etapa gera arquivos CSV para serem usados em outras ferramentas sem a necessidade de ter o banco de dados no ar.

O processo pode ser executado quantas vezes for necessário. A base dimensional irá evoluir sem prejuízo.

> Para executar somente a parte de extração de EXIF e load da base dimensional, execute `python3 main.py X` isso pula a etapa
de extração da URL que é a menos custosa e que normalmente finaliza rapidamente.

> Para executar somente a geração do CSV execute `python3 main.py csv`.


## Opções de comando

### Database to CSV

Para gerar arquivos CSV a partir do banco de dados execute:

`python3 main.py preload`

### Load Data Warehouse

Carrega o DW com base na tabela t_fotografias

`python3 main.py loaddw`

### Load Exif

Carrega o Exif das fotografias com base nos registros disponíveis na tabela t_fotografias.

`python3 main.py exif`

# Entendendo a estrutura do projeto

## Diretórios

### Raiz

Contém o arquivo de entrada principal da ETL (`main.py`) e o arquivo que descreve as bibliotecas
necessárias para os scripts Python rodarem (`requirements.txt`).

### etl

Contém os scripts de extração, transformação e carga.

* `image_url_extractor.py` varre a base de imagens do flickr e armazena dados básicos como a URL da imagem, titulo e tags.
* `exif_worker.py` é uma thread que, a partir de uma URL de imagem, obtém dados de EXIF das mesmas e os armazena no BD.
* `load_dw.py` é o script que popula a base de dados dimensional, o DWH.
* `create_tables.py` é o script que cria as tabelas do modelo relacional e dimensional no banco de dados.
* `pre_load_db.py` é o script que pre-carrega a base com uma execução anterior da ETL. Ele permite experimentar um DW já
com dados carregados de uma execução anterior.
* `dw_csv.py` exporta o banco de dados para arquivos CSV (execute `python3 main.py csv` para gerar a qualquer momento).

### modelo

Contém arquivos relacionados ao modelo de dados.

### docs

Documentos relacionados ao TCC.

### data

Datasets no format CSV.
