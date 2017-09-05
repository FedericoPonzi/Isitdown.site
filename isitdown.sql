--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: pings; Type: TABLE; Schema: public; Owner: isitdownu; Tablespace: 
--

CREATE TABLE pings (
    id integer NOT NULL,
    f character varying(120),
    t character varying(120),
    at timestamp without time zone,
    down boolean DEFAULT false NOT NULL
);


ALTER TABLE public.pings OWNER TO isitdownu;

--
-- Name: pings_id_seq; Type: SEQUENCE; Schema: public; Owner: isitdownu
--

CREATE SEQUENCE pings_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pings_id_seq OWNER TO isitdownu;

--
-- Name: pings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: isitdownu
--

ALTER SEQUENCE pings_id_seq OWNED BY pings.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: isitdownu
--

ALTER TABLE ONLY pings ALTER COLUMN id SET DEFAULT nextval('pings_id_seq'::regclass);


--
-- Name: pings_pkey; Type: CONSTRAINT; Schema: public; Owner: isitdownu; Tablespace: 
--

ALTER TABLE ONLY pings
    ADD CONSTRAINT pings_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

