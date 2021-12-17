-- Apartado I

-- Creamos la columna promo
ALTER TABLE customers
ADD promo float DEFAULT 0;

-- Creamos el procedimiento almacenado que sera llamado por el trigger
CREATE OR REPLACE FUNCTION updPromo() RETURNS TRIGGER AS $$
BEGIN
    -- Actualizamos netamount
    UPDATE orders
    SET netamount = ROUND(CAST(netamount - netamount * 0.01 * NEW.promo AS NUMERIC), 2)
    WHERE customerid = NEW.customerid
    AND status IS NULL;

    -- Aqui para hacer deadlock
    PERFORM pg_sleep(10);

    -- Actualizamos totalamount
    UPDATE public.orders
    SET totalamount = ROUND(netamount * (1 + tax/100), 2)
    WHERE totalamount IS NULL;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Creamos el trigger
CREATE TRIGGER updPromo_trigger
AFTER UPDATE OF promo ON customers
FOR EACH ROW
EXECUTE PROCEDURE updPromo();


-- ESTO NO VA AQUI, ES SIMPLEMENTE PARA EJECUTAR EL APARTADO I
UPDATE orders
SET status = NULL
WHERE orderid = 1
OR orderid = 7
OR orderid = 23;


ERROR:  deadlock detected
DETAIL:  Process 15050 waits for ShareLock on transaction 11512; blocked by process 16314.
Process 16314 waits for ShareLock on transaction 11521; blocked by process 15050.
HINT:  See server log for query details.
CONTEXT:  while updating tuple (1686,19) in relation "orders"
SQL statement "UPDATE orders
    SET netamount = ROUND(CAST(netamount - netamount * 0.01 * NEW.promo AS NUMERIC), 2)
    WHERE customerid = NEW.customerid
    AND status IS NULL"
PL/pgSQL function updpromo() line 7 at SQL statement
SQL state: 40P01