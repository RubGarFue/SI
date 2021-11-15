# -*- coding: utf-8 -*-

import os
import random
import sys, traceback
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, text
from sqlalchemy.sql import select

# configurar el motor de sqlalchemy
db_engine = create_engine("postgresql://alumnodb:alumnodb@localhost/si1", echo=False)
db_meta = MetaData(bind=db_engine)

def db_error(db_conn):
    if db_conn is not None:
        db_conn.close()
    print("Exception in DB access:")
    print("-"*60)
    traceback.print_exc(file=sys.stderr)
    print("-"*60)

    return 'Something is broken'


################# INDEX FUNCTIONS ################

# Devuelve todo el catálogo de películas (las 100 primeras)
def getCatalogue():
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        db_result = db_conn.execute("SELECT foo.movieid, movietitle, genrename\
                                     FROM\
                                        (SELECT *\
                                        FROM public.imdb_movies\
                                        ORDER BY movietitle\
                                        LIMIT 100) AS foo\
                                     INNER JOIN public.imdb_moviegenres\
                                     ON foo.movieid = imdb_moviegenres.movieid\
                                     INNER JOIN public.imdb_genres\
                                     ON imdb_moviegenres.genreid = imdb_genres.genreid\
                                     ORDER BY movietitle")
        
        db_conn.close()

        catalog = []

        for row in db_result:
            new_film = True
            pelicula = {'id': '', 'titulo': '', 'categoria': []}
            for pel in catalog:
                if row.movietitle == pel['titulo']:
                    new_film = False
                    pel['categoria'].append(row.genrename)
            if new_film:
                pelicula['id'] = int(row.movieid)
                pelicula['titulo'] = row.movietitle
                pelicula['categoria'].append(row.genrename)
                catalog.append(pelicula)
        
        return catalog
    except:
        return db_error(db_conn)


# Devuelve todos los generos disponibles
def getGenres():
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()
        db_result = db_conn.execute("SELECT genrename\
                                     FROM public.imdb_genres;")
        
        db_conn.close()

        genres = {genre[0] for genre in db_result}
        return genres
    except:
        return db_error(db_conn)


# Devuelve una película por id
def getMovie(movie_id):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        movie = dict()

        db_result = db_conn.execute("SELECT movie.movieid, movietitle, movie.year, price, directorname\
                                     FROM\
                                        (SELECT movieid, movietitle, year\
                                        FROM public.imdb_movies\
                                        WHERE movieid="+ str(movie_id) +") AS movie\
                                     INNER JOIN public.products\
                                     ON movie.movieid = products.movieid\
                                     INNER JOIN public.imdb_directormovies\
                                     ON movie.movieid = imdb_directormovies.movieid\
                                     INNER JOIN public.imdb_directors\
                                     ON imdb_directormovies.directorid = imdb_directors.directorid\
                                     LIMIT 1")
        
        result = db_result.all()[0]

        movie['id'] = result.movieid
        movie['titulo'] = result.movietitle
        movie['precio'] = result.price
        movie['director'] = result.directorname
        movie['anno'] = result.year
        # Sinopsis generica
        movie['sinopsis'] = 'Esta es la sinopsis de la película ' + movie['titulo']

        db_result = db_conn.execute("SELECT movie.movieid, genrename\
                                     FROM\
                                        (SELECT movieid\
                                        FROM public.imdb_movies\
                                        WHERE movieid=" + str(movie_id) + ") AS movie\
                                     INNER JOIN public.imdb_moviegenres\
                                     ON movie.movieid = imdb_moviegenres.movieid\
                                     INNER JOIN public.imdb_genres\
                                     ON imdb_moviegenres.genreid = imdb_genres.genreid")

        movie['categoria'] = []
        for row in db_result:
            movie['categoria'].append(row.genrename)

        db_result = db_conn.execute("SELECT movie.movieid, actorname\
                                     FROM\
                                        (SELECT movieid\
                                        FROM public.imdb_movies\
                                        WHERE movieid=" + str(movie_id) + ") AS movie\
                                     INNER JOIN public.imdb_actormovies\
                                     ON movie.movieid = imdb_actormovies.movieid\
                                     INNER JOIN public.imdb_actors\
                                     ON imdb_actormovies.actorid = imdb_actors.actorid")

        movie['actores'] = []
        for row in db_result:
            movie['actores'].append(row.actorname)
        
        db_conn.close()
        
        return movie
    except:
        return db_error(db_conn)


################# LOGIN FUNCTIONS #####################

# Comprueba si el usuario introducido es correcto (usuario y contrasenna)
def checkUser(username, password):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        db_result = db_conn.execute("SELECT *\
                                     FROM public.customers\
                                     WHERE username = '" + username + "'\
                                     AND password = '" + password + "'")
        
        db_conn.close()
        
        if not db_result.all():
            return False

        return True
    except:
        return db_error(db_conn)


################# REGISTER FUNCTIONS #####################

# Comprueba si existe un usuario
def userExists(username):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        db_result = db_conn.execute("SELECT *\
                                     FROM public.customers\
                                     WHERE username = '" + username + "'")
        
        db_conn.close()
        
        if not db_result.all():
            return False

        return True
    except:
        return db_error(db_conn)

# Registra a un usuario
def register(username, password, email, credit_card, direction):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        db_result = db_conn.execute("SELECT COUNT(*) FROM public.customers")
        customerid = db_result.all()[0].count + 1

        db_conn.execute("INSERT INTO public.customers (customerid, address1, email, creditcard, username, password, loyalty, balance)\
                         VALUES ('" + str(customerid) + "', '" + direction + "', '" + email + "', '" + credit_card +
                         "', '" + username + "', '" + password + "', '0', '" + str(random.randint(0, 100)) + "');")
        
        db_conn.close()
        
        return None
    except:
        return db_error(db_conn)


############### SHOPPING CART FUNCTIONS #####################
def update_cart(username, movieid, units):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()
        customerid = db_conn.execute("SELECT customerid\
                                     FROM public.customers\
                                     WHERE username = '" + username + "'").first()[0]
        prod_id = db_conn.execute("SELECT prod_id\
                                   FROM public.products\
                                   WHERE movieid = '" + str(movieid) + "'").first()[0]
        price = db_conn.execute("SELECT price \
                                 FROM public.products \
                                 WHERE movieid = '" + str(movieid) + "'").first()[0]
        db_result = db_conn.execute("SELECT orderid \
                                     FROM public.orders \
                                     WHERE customerid = '" + str(customerid) + "' \
                                     AND status is null;")
        orderid = db_result.fetchone()
        if orderid == None:
            # New order
            orderid = db_conn.execute("SELECT MAX(orderid)+1 FROM public.orders;").first()[0]
            db_conn.execute("INSERT INTO public.orders \
                             VALUES (" + str(orderid) + ", NOW()::date, " + str(customerid) + ", 0, 15, 0, null);")
            db_conn.execute("INSERT INTO public.orderdetail \
                             VALUES ("+ str(orderid)+", \
                                     "+ str(prod_id) +", \
                                     "+ str(price) +", \
                                     "+ str(units)+");")
        else:
            # Carrito ya existia
            orderid = orderid[0]
            db_result = db_conn.execute("SELECT * from orderdetail WHERE orderid = "+ str(orderid) +" AND prod_id = "+ str(prod_id) +"")
            if db_result.all():
                # Ya existen unidades de ese articulo en el carrito
                db_conn.execute("UPDATE orderdetail \
                                 SET quantity = quantity + "+ str(units) +" \
                                 WHERE orderid = "+ str(orderid) +";")
            else:
                # nueva entrada en orderdetail
                db_conn.execute("INSERT INTO public.orderdetail \
                                 VALUES ("+ str(orderid)+", \
                                         "+ str(prod_id) +", \
                                         "+ str(price) +", \
                                         "+ str(units)+");")

        db_conn.close()
        return True
    except:
        return db_error(db_conn)


################# AUXILIARY FUNCTIONS #####################

# Devuelve el top actores de un género concreto
def getTopActors(genre = 'Action'):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        db_result = db_conn.execute("SELECT * FROM getTopActors('" + genre + "') LIMIT 10")
        
        db_conn.close()
        
        return list(db_result)
    except:
        return db_error(db_conn)