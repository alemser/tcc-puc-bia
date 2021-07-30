DROP TABLE IF EXISTS "public"."d_camera";
-- This script only contains the table creation statements and does not fully represent the table in the database. It's still missing: indices, triggers. Do not use it as a backup.

-- Sequence and defined type
CREATE SEQUENCE IF NOT EXISTS d_camera_id_camera_seq;

-- Table Definition
CREATE TABLE "public"."d_camera" (
    "id_camera" int4 NOT NULL DEFAULT nextval('d_camera_id_camera_seq'::regclass),
    "nm_camera" varchar UNIQUE,
    "id_fabricante" int8,
    "id_tipo_camera" int8,
    PRIMARY KEY ("id_camera")
);

DROP TABLE IF EXISTS "public"."d_lente";
-- This script only contains the table creation statements and does not fully represent the table in the database. It's still missing: indices, triggers. Do not use it as a backup.

-- Sequence and defined type
CREATE SEQUENCE IF NOT EXISTS d_lente_id_lente_seq;

-- Table Definition
CREATE TABLE "public"."d_lente" (
    "id_lente" int4 NOT NULL DEFAULT nextval('d_lente_id_lente_seq'::regclass),
    "nm_modelo" varchar UNIQUE,
    "id_fabricante" int8,
    "id_tipo_lente" int8,
    PRIMARY KEY ("id_lente")
);

DROP TABLE IF EXISTS "public"."d_categoria";
-- This script only contains the table creation statements and does not fully represent the table in the database. It's still missing: indices, triggers. Do not use it as a backup.

-- Sequence and defined type
CREATE SEQUENCE IF NOT EXISTS d_categoria_id_categoria_seq;

-- Table Definition
CREATE TABLE "public"."d_categoria" (
    "id_categoria" int4 NOT NULL DEFAULT nextval('d_categoria_id_categoria_seq'::regclass),
    "nm_categoria" varchar UNIQUE,
    PRIMARY KEY ("id_categoria")
);

DROP TABLE IF EXISTS "public"."d_fabricante";
-- This script only contains the table creation statements and does not fully represent the table in the database. It's still missing: indices, triggers. Do not use it as a backup.

-- Sequence and defined type
CREATE SEQUENCE IF NOT EXISTS d_fabricante_id_fabricante_seq;

-- Table Definition
CREATE TABLE "public"."d_fabricante" (
    "id_fabricante" int4 NOT NULL DEFAULT nextval('d_fabricante_id_fabricante_seq'::regclass),
    "nm_fabricante" varchar UNIQUE,
    PRIMARY KEY ("id_fabricante")
);

DROP TABLE IF EXISTS "public"."d_imagem";
-- This script only contains the table creation statements and does not fully represent the table in the database. It's still missing: indices, triggers. Do not use it as a backup.

-- Sequence and defined type
CREATE SEQUENCE IF NOT EXISTS d_imagem_id_imagem_seq;

-- Table Definition
CREATE TABLE "public"."d_imagem" (
    "id_imagem" int4 NOT NULL DEFAULT nextval('d_imagem_id_imagem_seq'::regclass),
    "nm_url" varchar UNIQUE,
    "dt_imagem" timestamp,
    "de_titulo" varchar,
    "nm_tags" varchar,
    PRIMARY KEY ("id_imagem")
);

DROP TABLE IF EXISTS "public"."d_tipo_camera";
-- This script only contains the table creation statements and does not fully represent the table in the database. It's still missing: indices, triggers. Do not use it as a backup.

-- Sequence and defined type
CREATE SEQUENCE IF NOT EXISTS d_tipo_camera_id_tipo_camera_seq;

-- Table Definition
CREATE TABLE "public"."d_tipo_camera" (
    "id_tipo_camera" int4 NOT NULL DEFAULT nextval('d_tipo_camera_id_tipo_camera_seq'::regclass),
    "nm_tipo_camera" varchar UNIQUE,
    PRIMARY KEY ("id_tipo_camera")
);

DROP TABLE IF EXISTS "public"."d_tipo_lente";
-- This script only contains the table creation statements and does not fully represent the table in the database. It's still missing: indices, triggers. Do not use it as a backup.

-- Sequence and defined type
CREATE SEQUENCE IF NOT EXISTS d_tipo_lente_id_tipo_lente_seq;

-- Table Definition
CREATE TABLE "public"."d_tipo_lente" (
    "id_tipo_lente" int4 NOT NULL DEFAULT nextval('d_tipo_lente_id_tipo_lente_seq'::regclass),
    "nm_tipo_lente" varchar UNIQUE,
    PRIMARY KEY ("id_tipo_lente")
);

DROP TABLE IF EXISTS "public"."f_foto";
-- This script only contains the table creation statements and does not fully represent the table in the database. It's still missing: indices, triggers. Do not use it as a backup.

-- Sequence and defined type
CREATE SEQUENCE IF NOT EXISTS f_foto_id_foto_seq;

-- Table Definition
CREATE TABLE "public"."f_foto" (
    "id_foto" int4 NOT NULL DEFAULT nextval('f_foto_id_foto_seq'::regclass),
    "id_camera" int8 NOT NULL,
    "id_categoria" int8 NOT NULL,
    "id_lente" int8 NOT NULL,
    "id_imagem" int8 NOT NULL,
    "fl_flash" bool NOT NULL,
    "nu_abertura" numeric NOT NULL,
    "nu_tempo_exposicao" numeric NOT NULL,
    "nu_iso" numeric NOT NULL,
    "nu_distancia_focal" numeric NOT NULL,
    PRIMARY KEY ("id_foto","id_camera","id_categoria","id_lente","id_imagem")
);

DROP TABLE IF EXISTS "public"."t_fotografias";
-- This script only contains the table creation statements and does not fully represent the table in the database. It's still missing: indices, triggers. Do not use it as a backup.

-- Sequence and defined type
CREATE SEQUENCE IF NOT EXISTS t_fotografias_id_fotografia_seq;

-- Table Definition
CREATE TABLE "public"."t_fotografias" (
    "id_fotografia" int4 NOT NULL DEFAULT nextval('t_fotografias_id_fotografia_seq'::regclass),
    "de_titulo" varchar,
    "nm_url" varchar UNIQUE NOT NULL,
    "dt_coleta" timestamp,
    "dt_foto" timestamp,
    "tp_lente" varchar,
    "nm_lente" varchar,
    "nm_fabric_lente" varchar,
    "nu_dist_focal" numeric,
    "tp_camera" varchar,
    "nm_camera" varchar,
    "nm_fabric_camera" varchar,
    "nm_categoria_foto" varchar,
    "nu_abertura" numeric,
    "nu_tempo_exposicao" numeric,
    "nu_iso" numeric,
    "fl_flash" bool,
    "nm_tags" varchar,
    "fl_lido" bool DEFAULT false,
    "fl_falha_exif" bool DEFAULT false,
    "nu_dist_focal_35mmeq" numeric,
    PRIMARY KEY ("id_fotografia")
);
