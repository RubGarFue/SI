-- d) procedimiento getTopSales
CREATE OR REPLACE FUNCTION getTopSales(year1 INT, year2 INT, OUT Year INT, OUT Film CHAR, OUT sales bigint) 
RETURNS SETOF record as $$
BEGIN
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

    RETURN QUERY (
        SELECT *
        FROM
            (SELECT DISTINCT ON (moviecount.year) moviecount.year::integer, movietitle::bpchar, max
            FROM
                (SELECT moviecount.year, MAX(count) AS max
                FROM moviecount
                GROUP BY moviecount.year) AS moviemax
            INNER JOIN moviecount
            ON moviecount.year = moviemax.year
            AND moviecount.count = moviemax.max

            WHERE moviemax.year BETWEEN year1 AND year2) AS foo

        ORDER BY max DESC
    );

    DROP VIEW moviecount;
END;
$$ LANGUAGE plpgsql;