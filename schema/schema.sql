CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE TYPE verification_status AS ENUM ('verified','potential','pending','unusable');
CREATE TYPE access_class AS ENUM ('public','authorized','restricted','private');
CREATE TYPE operational_status AS ENUM ('operational','limited','closed','unknown');
CREATE TABLE IF NOT EXISTS data_sources (
 id text PRIMARY KEY, authority text NOT NULL, title text NOT NULL, service_url text,
 license_note text, source_crs text, scope_note text, last_checked timestamptz,
 created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS map_layers (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), source_id text REFERENCES data_sources(id),
 municipality text NOT NULL, theme text NOT NULL, source_layer_id integer,
 title text NOT NULL, geometry_type text, source_updated_at timestamptz,
 retrieved_at timestamptz, output_crs text DEFAULT 'EPSG:4326',
 verification verification_status NOT NULL DEFAULT 'pending',
 geom geometry(Geometry,4326), attributes jsonb NOT NULL DEFAULT '{}'::jsonb,
 source_url text, license_note text, created_at timestamptz DEFAULT now()
);
CREATE INDEX IF NOT EXISTS map_layers_geom_gix ON map_layers USING gist(geom);
CREATE INDEX IF NOT EXISTS map_layers_theme_idx ON map_layers(theme,municipality);
CREATE TABLE IF NOT EXISTS places (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), name text NOT NULL, category text NOT NULL,
 subcategory text, municipality text NOT NULL, address text, phone_public text,
 website text, opening_hours text, access access_class NOT NULL DEFAULT 'public',
 status operational_status NOT NULL DEFAULT 'unknown', verification verification_status NOT NULL DEFAULT 'pending',
 confidence smallint NOT NULL DEFAULT 0 CHECK(confidence BETWEEN 0 AND 100),
 capacity integer, accessibility jsonb NOT NULL DEFAULT '{}'::jsonb,
 potable_water boolean, solar_power boolean, public_charging boolean,
 geom geometry(Point,4326) NOT NULL, source_id text REFERENCES data_sources(id),
 source_url text, evidence text, last_verified timestamptz, next_review timestamptz,
 visibility text NOT NULL DEFAULT 'public' CHECK(visibility IN ('public','private')),
 created_at timestamptz DEFAULT now(), updated_at timestamptz DEFAULT now()
);
CREATE INDEX IF NOT EXISTS places_geom_gix ON places USING gist(geom);
CREATE INDEX IF NOT EXISTS places_category_idx ON places(category,municipality,status);
CREATE TABLE IF NOT EXISTS route_segments (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), name text, municipality text NOT NULL,
 route_class text NOT NULL CHECK(route_class IN ('official','calculated','field_checked','proposed')),
 status operational_status NOT NULL DEFAULT 'unknown', surface text, slope_percent numeric,
 accessible boolean, hazard_review text NOT NULL DEFAULT 'not_assessed',
 verification verification_status NOT NULL DEFAULT 'pending', geom geometry(LineString,4326) NOT NULL,
 source_url text, last_verified timestamptz
);
CREATE INDEX IF NOT EXISTS route_segments_geom_gix ON route_segments USING gist(geom);
CREATE TABLE IF NOT EXISTS verification_log (
 id bigserial PRIMARY KEY, object_type text NOT NULL, object_id text NOT NULL,
 old_status text, new_status text NOT NULL, method text NOT NULL,
 evidence_url text, notes text, verified_by text, verified_at timestamptz DEFAULT now()
);
CREATE TABLE IF NOT EXISTS private_assets (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), owner_id text NOT NULL,
 asset_type text NOT NULL, label text NOT NULL, quantity numeric, unit text,
 notes text, geom geometry(Point,4326), encrypted_payload text,
 updated_at timestamptz DEFAULT now()
);
COMMENT ON TABLE private_assets IS 'No exponer por API pública. Direcciones y ubicaciones privadas no deben publicarse.';
