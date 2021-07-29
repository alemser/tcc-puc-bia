CREATE TABLE t_fotografias (
                id_fotografia SERIAL NOT NULL,
                de_titulo VARCHAR  NULL,
                nm_url VARCHAR NOT  NULL UNIQUE,
                dt_coleta TIMESTAMP  NULL,
                dt_foto TIMESTAMP  NULL,
                tp_lente VARCHAR  NULL,
                nm_lente VARCHAR  NULL,
                nm_fabric_lente VARCHAR  NULL,
                nu_dist_focal DECIMAL NULL,
                tp_camera VARCHAR  NULL,
                nm_camera VARCHAR  NULL,
                nm_fabric_camera VARCHAR  NULL,
                nm_categoria_foto VARCHAR  NULL,
                nu_abertura DECIMAL  NULL,
                nu_tempo_exposicao DECIMAL  NULL,
                nu_iso DECIMAL  NULL,
                fl_flash BOOLEAN  NULL,
                nm_tags VARCHAR  NULL,
                fl_lido boolean default false,
                fl_falha_exif boolean default false,
                nu_dist_focal_35mmEq DECIMAL null,
                CONSTRAINT id_fotografias PRIMARY KEY (id_fotografia)
);

CREATE TABLE public.d_imagem (
                id_imagem serial NOT NULL,
                nm_url VARCHAR NOT NULL UNIQUE,
                dt_imagem TIMESTAMP,
                de_titulo VARCHAR,
                nm_tags VARCHAR,
                CONSTRAINT id_imagem PRIMARY KEY (id_imagem)
);

CREATE TABLE public.d_fabricante (
                id_fabricante SERIAL NOT NULL,
                nm_fabricante VARCHAR UNIQUE,
                CONSTRAINT id_fabricante PRIMARY KEY (id_fabricante)
);

CREATE TABLE public.d_categoria (
                id_categoria SERIAL NOT NULL,
                nm_categoria VARCHAR UNIQUE,
                CONSTRAINT id_categoria PRIMARY KEY (id_categoria)
);

CREATE TABLE public.d_tipo_camera (
                id_tipo_camera SERIAL NOT NULL,
                nm_tipo_camera VARCHAR,
                CONSTRAINT id_tipo_camera PRIMARY KEY (id_tipo_camera)
);

CREATE TABLE public.d_camera (
                id_camera SERIAL NOT NULL,
                nm_camera VARCHAR UNIQUE,
                id_fabricante BIGINT,
                id_tipo_camera BIGINT,
                CONSTRAINT id_camera PRIMARY KEY (id_camera)
);

CREATE TABLE public.d_tipo_lente (
                id_tipo_lente SERIAL NOT NULL,
                nm_tipo_lente VARCHAR UNIQUE,
                CONSTRAINT id_tipo_lente PRIMARY KEY (id_tipo_lente)
);


CREATE TABLE public.d_lente (
                id_lente SERIAL NOT NULL,
                nm_modelo VARCHAR NOT NULL UNIQUE,
                id_fabricante BIGINT,
                id_tipo_lente BIGINT,
                CONSTRAINT id_lente PRIMARY KEY (id_lente)
);

CREATE TABLE public.f_foto (
                id_foto SERIAL NOT NULL,
                id_camera BIGINT NOT NULL,
                id_categoria BIGINT NOT NULL,
                id_lente BIGINT NOT NULL,
                id_imagem BIGINT NOT NULL,
                fl_flash BOOLEAN NOT NULL,
                nu_abertura NUMERIC NOT NULL,
                nu_tempo_exposicao NUMERIC NOT NULL,
                nu_iso NUMERIC NOT NULL,
                nu_distancia_focal NUMERIC NOT NULL,
                CONSTRAINT id_foto PRIMARY KEY (id_foto, id_camera, id_categoria, id_lente, id_imagem)
);



ALTER TABLE public.f_foto ADD CONSTRAINT d_imagem_f_foto_fk
FOREIGN KEY (id_imagem)
REFERENCES public.d_imagem (id_imagem)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.d_camera ADD CONSTRAINT d_fabricante_d_camera_fk
FOREIGN KEY (id_fabricante)
REFERENCES public.d_fabricante (id_fabricante)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.d_lente ADD CONSTRAINT d_fabricante_d_lente_fk
FOREIGN KEY (id_fabricante)
REFERENCES public.d_fabricante (id_fabricante)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.f_foto ADD CONSTRAINT d_categoria_f_foto_fk
FOREIGN KEY (id_categoria)
REFERENCES public.d_categoria (id_categoria)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.d_camera ADD CONSTRAINT d_tipo_camera_d_camera_fk
FOREIGN KEY (id_tipo_camera)
REFERENCES public.d_tipo_camera (id_tipo_camera)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.f_foto ADD CONSTRAINT d_camera_f_foto_fk
FOREIGN KEY (id_camera)
REFERENCES public.d_camera (id_camera)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.d_lente ADD CONSTRAINT d_tipo_lente_d_lente_fk
FOREIGN KEY (id_tipo_lente)
REFERENCES public.d_tipo_lente (id_tipo_lente)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.f_foto ADD CONSTRAINT d_lente_f_foto_fk
FOREIGN KEY (id_lente)
REFERENCES public.d_lente (id_lente)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;
