CREATE USER devpg;
ALTER USER devpg PASSWORD 'devpg1p';

CREATE DATABASE default_db;
GRANT ALL PRIVILEGES ON DATABASE default_db TO devpg;

GRANT ALL PRIVILEGES ON TABLE uxp_entity TO devpg;

-- CREATE DATABASE registry_prom;
-- GRANT ALL PRIVILEGES ON DATABASE registry_prom TO postgres;

-- CREATE DATABASE registry_test;
-- GRANT ALL PRIVILEGES ON DATABASE registry_test TO postgres;

-- CREATE DATABASE apptool_test;
-- GRANT ALL PRIVILEGES ON DATABASE apptool_test TO postgres;

-- CREATE DATABASE apptool_prom;
-- GRANT ALL PRIVILEGES ON DATABASE apptool_prom TO postgres;