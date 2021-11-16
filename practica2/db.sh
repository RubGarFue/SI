dropdb -U alumnodb -h localhost si1
createdb -U alumnodb -h localhost si1 
gunzip -c dump_v1.4.sql.gz | psql -U alumnodb -h localhost si1
psql si1 -U alumnodb -h localhost -f SQL/setPrice.sql
psql si1 -U alumnodb -h localhost -f SQL/setOrderAmount.sql
psql si1 -U alumnodb -h localhost -f SQL/actualiza.sql
psql si1 -U alumnodb -h localhost -f SQL/updOrders.sql
psql si1 -U alumnodb -h localhost -f SQL/updInventoryAndCustomer.sql
psql si1 -U alumnodb -h localhost -f SQL/getTopActors.sql
psql si1 -U alumnodb -h localhost -f SQL/getTopSales.sql