# diretorio usado para volume do BD
mkdir -p $HOME/docker/volumes/postgres

# Construindo a imagem
docker pull postgres

# Iniciando o container a partir da imagem
docker run --rm --name pg-docker -e POSTGRES_PASSWORD=docker -d -p 5432:5432 -v $HOME/docker/volumes/postgres:/var/lib/postgresql/data postgres
