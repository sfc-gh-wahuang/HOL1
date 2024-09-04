USE ROLE USERADMIN;
CREATE ROLE HOL1;
GRANT ROLE HOL1 TO USER WHUANG;
USE ROLE SYSADMIN;
CREATE OR REPLACE WAREHOUSE HOL1_WH WAREHOUSE_SIZE=XSMALL INITIALLY_SUSPENDED=TRUE;
GRANT USAGE ON WAREHOUSE HOL1_WH TO ROLE HOL1;
USE ROLE HOL1;
USE WAREHOUSE HOL1_WH;
USE ROLE SYSADMIN;
CREATE DATABASE IF NOT EXISTS HOL1_DB;
GRANT OWNERSHIP ON DATABASE HOL1_DB TO ROLE HOL1;
USE ROLE HOL1;
CREATE SCHEMA IF NOT EXISTS HOL1_DB.HOL1_SCHEMA;
CREATE OR REPLACE STAGE HOL1_DB.HOL1_SCHEMA.ML_PROCS;
CREATE OR REPLACE STAGE HOL1_DB.HOL1_SCHEMA.DATA_STAGE;

-- upload util functions to stage for later use
PUT file://src/utils.py @ML_PROCS;