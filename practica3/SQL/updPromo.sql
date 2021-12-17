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

    -- Actualizamos orderdetail
    UPDATE orderdetail
    SET price = ROUND(CAST(products.price - products.price * 0.01 * NEW.promo AS NUMERIC))
    FROM customers, orders, products
    WHERE orders.customerid = NEW.customerid
    AND orders.orderid = orderdetail.orderid
    AND orderdetail.prod_id = products.prod_id
    AND orders.status IS NULL;
END;
$$ LANGUAGE plpgsql;

-- Creamos el trigger
CREATE TRIGGER updPromo_trigger
AFTER UPDATE OF promo ON customers
FOR EACH ROW
EXECUTE PROCEDURE updPromo();