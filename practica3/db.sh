dropdb -U alumnodb -h localhost si1
createdb -U alumnodb -h localhost si1 
gunzip -c dump_v1.5-P3.sql.gz | psql -U alumnodb -h localhost si1