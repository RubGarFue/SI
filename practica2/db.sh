dropdb -U alumnodb -h localhost si1
createdb -U alumnodb -h localhost si1 
gunzip -c dump_v1.4.sql.gz | psql -U alumnodb -h localhost si1
#psql si1 -U alumnodb -h localhost -f SQL/actualiza.sql