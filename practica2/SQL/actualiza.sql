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


-- Llamada al procedimiento 'setOrderAmount'
SELECT setOrderAmount();


-- f) atributos multivaluados en relacinoes

-- moviegenres
CREATE TABLE public.imdb_genres (
    genreid serial4 NOT NULL,
    genrename VARCHAR(32) NOT NULL,
    PRIMARY KEY (genreid)
);

INSERT INTO public.imdb_genres (genrename)
SELECT DISTINCT genre FROM public.imdb_moviegenres 
ORDER BY genre;

ALTER TABLE public.imdb_moviegenres 
ADD COLUMN genreid int;

UPDATE public.imdb_moviegenres
SET genreid = imdb_genres.genreid
FROM public.imdb_genres
WHERE imdb_moviegenres.genre = imdb_genres.genrename;

ALTER TABLE public.imdb_moviegenres
DROP COLUMN genre;

ALTER TABLE public.imdb_moviegenres 
ADD FOREIGN KEY (genreid) REFERENCES public.imdb_genres;

-- moviecountries
CREATE TABLE public.imdb_countries (
    countryid serial4 NOT NULL,
    country VARCHAR(32) NOT NULL,
    PRIMARY KEY (countryid)
);

INSERT INTO public.imdb_countries (country)
SELECT DISTINCT country FROM public.imdb_moviecountries
ORDER BY country;

ALTER TABLE public.imdb_moviecountries
ADD COLUMN countryid int;

UPDATE public.imdb_moviecountries
SET countryid = imdb_countries.countryid
FROM public.imdb_countries
WHERE imdb_moviecountries.country = imdb_countries.country;

ALTER TABLE public.imdb_moviecountries
DROP COLUMN country;

ALTER TABLE public.imdb_moviecountries 
ADD FOREIGN KEY (countryid) REFERENCES public.imdb_countries;

-- movielanguages
CREATE TABLE public.imdb_languages (
    languageid serial4 NOT NULL,
    language VARCHAR(32) NOT NULL,
    PRIMARY KEY (languageid)
);

INSERT INTO public.imdb_languages (language)
SELECT DISTINCT language FROM public.imdb_movielanguages
ORDER BY language;

ALTER TABLE public.imdb_movielanguages
ADD COLUMN languageid int;

UPDATE public.imdb_movielanguages
SET languageid = imdb_languages.languageid
FROM public.imdb_languages
WHERE imdb_movielanguages.language = imdb_languages.language;

ALTER TABLE public.imdb_movielanguages
DROP COLUMN language;

ALTER TABLE public.imdb_movielanguages
ADD FOREIGN KEY (languageid) REFERENCES public.imdb_languages;


