
CREATE TABLE public.t_fotografias (
                id_fotografia SERIAL,
                de_titulo VARCHAR,
                nm_url VARCHAR NOT NULL,
                dt_coleta TIMESTAMP,
                tp_lente VARCHAR,
                nm_lente VARCHAR,
                nm_fabric_lente VARCHAR,
                nu_dist_focal_lente INT[],
                tp_camera VARCHAR,
                nm_camera VARCHAR,
                nm_fabric_camera VARCHAR,
                nm_categoria_foto VARCHAR,
                nu_abertura NUMERIC,
                nu_tempo_exposicao NUMERIC,
                nu_iso NUMERIC,
                fl_flash BOOLEAN,
                nm_tags VARCHAR,
                nu_dist_focal_lente_35mmEq NUMERIC,
                CONSTRAINT id_fotografias PRIMARY KEY (id_fotografia)
);

CREATE TABLE public.d_imagem (
                id_imagem serial BIGINT NOT NULL,
                nm_url VARCHAR,
                dt_imagem TIMESTAMP,
                de_titulo VARCHAR,
                CONSTRAINT id_imagem PRIMARY KEY (id_imagem)
);

CREATE TABLE public.d_fabricante (
                id_fabricante serial NOT NULL,
                nm_fabricante VARCHAR,
                CONSTRAINT id_fabricante PRIMARY KEY (id_fabricante)
);

CREATE TABLE public.d_categoria (
                id_categoria SERIAL NOT NULL,
                nm_categoria VARCHAR,
                CONSTRAINT id_categoria PRIMARY KEY (id_categoria)
);

CREATE TABLE public.d_tipo_camera (
                id_tipo_camera SERIAL NOT NULL,
                nm_tipo_camera VARCHAR,
                CONSTRAINT id_tipo_camera PRIMARY KEY (id_tipo_camera)
);

CREATE TABLE public.d_camera (
                id_camera SERIAL NOT NULL,
                nm_camera VARCHAR,
                id_fabricante BIGINT,
                id_tipo_camera BIGINT,
                CONSTRAINT id_camera PRIMARY KEY (id_camera)
);

CREATE TABLE public.d_tipo_lente (
                id_tipo_lente SERIAL NOT NULL,
                nm_tipo_lente VARCHAR,
                CONSTRAINT id_tipo_lente PRIMARY KEY (id_tipo_lente)
);


CREATE TABLE public.d_lente (
                id_lente SERIAL NOT NULL,
                ar_distancia_focal INT[],
                nm_modelo VARCHAR,
                id_fabricante BIGINT,
                id_tipo_lente BIGINT,
                CONSTRAINT id_lente PRIMARY KEY (id_lente)
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
