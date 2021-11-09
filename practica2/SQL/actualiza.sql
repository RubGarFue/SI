-- Conectar actor y movies
ALTER TABLE public.imdb_actormovies
ADD FOREIGN KEY (actorid) REFERENCES public.imdb_actors;

ALTER TABLE public.imdb_actormovies
ADD FOREIGN KEY (movieid) REFERENCES public.imdb_movies;

-- Conectar inventory y products
ALTER TABLE public.inventory 
ADD FOREIGN KEY (prod_id) REFERENCES public.products
ON DELETE cascade;

-- Conectar products y order
ALTER TABLE public.orderdetail
ADD FOREIGN KEY (prod_id) REFERENCES public.products;

ALTER TABLE public.orderdetail
ADD FOREIGN KEY (orderid) REFERENCES public.orders;

-- Conectar orders y customers
ALTER TABLE public.orders
ADD FOREIGN KEY (customerid) REFERENCES public.customers;


-- Añadir ON DELETE cascade en products
ALTER TABLE public.products
DROP CONSTRAINT products_movieid_fkey;

ALTER TABLE public.products
ADD FOREIGN KEY (movieid) REFERENCES public.imdb_movies
ON DELETE cascade;

-- Eliminamos columnas innecesarias de customer
ALTER TABLE public.customers
DROP COLUMN firstname, 
DROP COLUMN lastname,
DROP COLUMN address2,
DROP COLUMN city,
DROP COLUMN state,
DROP COLUMN zip,
DROP COLUMN country,
DROP COLUMN region,
DROP COLUMN phone,
DROP COLUMN creditcardtype,
DROP COLUMN creditcardexpiration,
DROP COLUMN age,
DROP COLUMN income,
DROP COLUMN gender;

-- Eliminamos la columna issuspended de movie
ALTER TABLE public.imdb_movies
DROP COLUMN issuspended;


-- ALERTS TABLE
CREATE TABLE public.alerts (
    prod_id integer PRIMARY KEY NOT null,
    end_date timestamp NOT NULL
);
ALTER TABLE public.alerts
OWNER TO alumnodb;
ALTER TABLE public.alerts
ADD FOREIGN KEY (prod_id) REFERENCES public.products;

-- Trigger parra actualizar tabla alerts
CREATE OR REPLACE FUNCTION setOutOfStockDate () RETURNS TRIGGER as $$
BEGIN  
    IF NEW.stock = 0 THEN
        INSERT INTO public.alerts(prod_id, end_date)
        VALUES (OLD.prod_id, NOW()::timestamp);
    END IF;
   	RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER alertTrigger
AFTER UPDATE OF stock ON public.inventory
FOR EACH ROW
EXECUTE PROCEDURE setOutOfStockDate();


-- 'loyalty' en tabla 'customers'
ALTER TABLE public.customers
ADD loyalty integer NOT NULL DEFAULT(0);

-- 'balance' en tabla 'customers'
ALTER TABLE public.customers
ADD balance real NOT NULL DEFAULT(0);

-- procedimiento para inicializar el campo 'balance' de 'customers'
CREATE OR REPLACE FUNCTION setCustomersBalance (IN initialBalance bigint) RETURNS void as $$
BEGIN
    UPDATE public.customers
    SET balance = ROUND(CAST(random()*initialBalance AS NUMERIC), 2);
END;
$$ LANGUAGE plpgsql;

-- Llamada a procedimiento 'setCustomersBalance'
SELECT setCustomersBalance(100);


-- c) procedimiento setOrderAmount
-- TODO: No se si se puede poner todo en un mismo update (por los WHERE * IS NULL)
CREATE OR REPLACE FUNCTION setOrderAmount() RETURNS void as $$
BEGIN
    UPDATE public.orders
    SET netamount = TOTAL.total
    FROM
        (SELECT orders.orderid, SUM(orderdetail.price) AS total
        FROM public.orders, public.orderdetail
        WHERE orders.orderid = orderdetail.orderid
        GROUP BY orders.orderid) AS TOTAL
    WHERE orders.orderid = TOTAL.orderid
    AND netamount IS NULL;

    UPDATE public.orders
    SET totalamount = netamount + tax
    WHERE totalamount IS NULL;
END;
$$ LANGUAGE plpgsql;

-- Llamada al procedimiento 'setOrderAmount'
SELECT setOrderAmount();


-- d) procedimiento getTopSales
CREATE OR REPLACE FUNCTION getTopSales(year1 INT, year2 INT, OUT Year INT, OUT Film CHAR, OUT sales bigint) as $$
BEGIN
-- !! EL UNICO PROBLEMA DE ESTA FUNCION ES QUE AL HACER EL OUT Y AL MOSTRAR EL RESULTADO DE LA FUNCION SOLO DA LA PRIMERA
-- !! COLUMNA, PERO EL SEGUNDO SELECT SÍ QUE DA UNA TABLA CON LAS PELICULAS MAS COMPRADAS ENTRE DOS AÑOS DADOS
    CREATE VIEW moviecount
    AS

    SELECT movietitle, year, COUNT(*) AS count
    FROM
        (SELECT imdb_movies.movietitle, DATE_PART('year', orders.orderdate) as year
        FROM public.orders INNER JOIN public.orderdetail
        ON orders.orderid = orderdetail.orderid
        INNER JOIN public.products
        ON products.prod_id = orderdetail.prod_id
        INNER JOIN public.imdb_movies
        ON imdb_movies.movieid = products.movieid) AS foo
    GROUP BY movietitle, year;

    SELECT moviecount.year::INT, movietitle, max
    INTO Year, Film, sales
    FROM
        (SELECT moviecount.year, MAX(count) AS max
        FROM moviecount
        GROUP BY moviecount.year) AS moviemax
    INNER JOIN moviecount
    ON moviecount.year = moviemax.year
    AND moviecount.count = moviemax.max

    WHERE moviemax.year BETWEEN year1 AND year2

    ORDER BY max DESC;

    DROP VIEW moviecount;
END;
$$ LANGUAGE plpgsql;