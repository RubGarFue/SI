-- e) procedimiento getTopActors
CREATE OR REPLACE FUNCTION getTopActors(genre CHAR, OUT Actor char, OUT Num INT, OUT Debut INT, OUT Film CHAR, OUT Director CHAR) 
RETURNS SETOF record as $$
BEGIN
    CREATE VIEW genreactorsgenres
    AS

    SELECT imdb_actors.actorname, imdb_movies.year, imdb_movies.movietitle, imdb_directors.directorname, imdb_moviegenres.genre
    FROM public.imdb_actors
        INNER JOIN public.imdb_actormovies
        ON imdb_actors.actorid = imdb_actormovies.actorid
        INNER JOIN public.imdb_moviegenres
        ON imdb_actormovies.movieid = imdb_moviegenres.movieid
        INNER JOIN public.imdb_directormovies
        ON imdb_actormovies.movieid = imdb_directormovies.movieid
        INNER JOIN public.imdb_movies
        ON imdb_actormovies.movieid = imdb_movies.movieid
        INNER JOIN public.imdb_directors
        ON imdb_directormovies.directorid = imdb_directors.directorid
    ORDER BY imdb_actors.actorname, imdb_movies.year;

    RETURN QUERY (
        SELECT *
        FROM
            (SELECT DISTINCT ON (genreactors.actorname) genreactors.actorname::bpchar, actorcount.count::integer, genreactors.year::integer, genreactors.movietitle::bpchar, genreactors.directorname::bpchar
            FROM
                (SELECT actorname, year, movietitle, directorname
                FROM genreactorsgenres
                WHERE genreactorsgenres.genre = $1) AS genreactors
            INNER JOIN
                (SELECT genreactors.actorname, COUNT(*) AS count
                FROM
                    (SELECT actorname, year, movietitle, directorname
                    FROM genreactorsgenres
                    WHERE genreactorsgenres.genre = $1) AS genreactors
                GROUP BY genreactors.actorname
                HAVING COUNT(*) > 4
                ORDER BY count DESC) AS actorcount
            ON genreactors.actorname = actorcount.actorname) AS foo
        ORDER BY count DESC
    );
	
    DROP VIEW genreactorsgenres;
END;
$$ LANGUAGE plpgsql;