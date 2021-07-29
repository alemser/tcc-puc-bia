# tcc-puc-bia
TCC PUC Minas - Business Intelligence and Analytics

# Pré-requisitos

## Docker

É preciso ter o Docker instalado para executar os scripts, pois a base de dados é fornecida numa imagem.

## Python 3

Para a execução dos scripts de ETL é preciso ter o Python3 instalado (juntamente com o pip3).

# Entendendo a estrutura do projeto

## Diretórios

### Raiz

Contém o arquivo de entrada principal da ETL (main.py) e os o arquivo que descreve as bibliotecas
necessárias para os scripts Python rodarem (requirements.txt).

### etl

Contém os scripts de extração, transformação e carga.

* `ImageUrlExtractor.py` varre a base de imagens do flicker e armazena dados básicos como a URL da imagem, titulo e tags.
* `ExifWorker.py` é uma thread que, a partir de uma URL de imagem, obtém dos dados EXIF das mesmas e os armazena no BD.
* `LoadDW.py` é o script que popula a base de dados dimensional, o DWH.
* `PreLoadDB.py` é o script que pre-carrega a base com uma execução anterior da ETL. Ele permite experimentar um DW já
com dados carregados de uma execução anterior.

### modelo

Contém arquivos relacionados ao modelo de dados.

### docs

Documentos relacionados ao TCC.

# Preparando o ambiente para execução

Para executar os scripts de ETL é necessário colocar o banco de dados no ar (docker), obter as bibliotecas requeridas
pelos scripts (requirements.txt) e executar os scripts.

## Banco de dados

Para iniciar o banco de dados execute:

```
# diretorio usado para volume do BD
mkdir -p $HOME/docker/volumes/postgres

# Construindo a imagem
docker pull postgres

# Iniciando o container a partir da imagem
docker run --rm --name pg-docker -e POSTGRES_PASSWORD=docker -d -p 5432:5432 -v $HOME/docker/volumes/postgres:/var/lib/postgresql/data postgres
```

## Bibliotecas

Para instalar as bibliotecas requeridas execute:

`pip3 install -r requirements.txt`

## Script

Para executar o script de coleta de dados no Flickr, execute:

`python3 main.py`

Se por algum motivo desejar parar o script para continuar depois, execute:

`python3 main.py X`
