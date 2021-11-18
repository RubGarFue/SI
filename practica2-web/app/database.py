# -*- coding: utf-8 -*-

import random
import sys, traceback
from sqlalchemy import create_engine
from sqlalchemy import MetaData


# configurar el motor de sqlalchemy
db_engine = create_engine("postgresql://alumnodb:alumnodb@localhost/si1", echo=False)
db_meta = MetaData(bind=db_engine)

# Maximo numero de peliculas a mostrar en el catalogo
LIMIT_MOVIES = '32'

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
def getCatalogue(search=None, genre=None):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        if search and genre:
            db_result = db_conn.execute("SELECT im.movieid, movietitle, genrename\
                                        FROM public.imdb_movies im \
                                        INNER JOIN public.imdb_moviegenres\
                                        ON im.movieid = imdb_moviegenres.movieid\
                                        INNER JOIN public.imdb_genres\
                                        ON imdb_moviegenres.genreid = imdb_genres.genreid \
                                        WHERE LOWER(movietitle) LIKE '%%" + search + "%%' \
                                        AND genrename = '"+ genre +"' \
                                        LIMIT " + LIMIT_MOVIES)
        elif search:
            db_result = db_conn.execute("SELECT im.movieid, movietitle, genrename\
                                        FROM public.imdb_movies im \
                                        INNER JOIN public.imdb_moviegenres\
                                        ON im.movieid = imdb_moviegenres.movieid\
                                        INNER JOIN public.imdb_genres\
                                        ON imdb_moviegenres.genreid = imdb_genres.genreid \
                                        WHERE LOWER(movietitle) LIKE '%%"+ search +"%%' \
                                        LIMIT " + LIMIT_MOVIES)
        elif genre:
            db_result = db_conn.execute("SELECT im.movieid, movietitle, genrename\
                                        FROM public.imdb_movies im \
                                        INNER JOIN public.imdb_moviegenres\
                                        ON im.movieid = imdb_moviegenres.movieid\
                                        INNER JOIN public.imdb_genres\
                                        ON imdb_moviegenres.genreid = imdb_genres.genreid \
                                        WHERE genrename = '"+ genre +"' \
                                        LIMIT " + LIMIT_MOVIES)
        else: 
            # all movies
            db_result = db_conn.execute("SELECT foo.movieid, movietitle, genrename\
                                        FROM\
                                            (SELECT *\
                                            FROM public.imdb_movies\
                                            LIMIT "+ LIMIT_MOVIES +") AS foo\
                                        INNER JOIN public.imdb_moviegenres\
                                        ON foo.movieid = imdb_moviegenres.movieid\
                                        INNER JOIN public.imdb_genres\
                                        ON imdb_moviegenres.genreid = imdb_genres.genreid")
        
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
                pelicula['poster'] = "static/img/movies/pulp-fiction.jpeg"
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
def update_cart(username, movieid, units, sum_units=False):
    customerid = customerid_from_username(username)
    orderid = get_orderid(customerid).first()
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()
        prod_id = db_conn.execute("SELECT prod_id\
                                   FROM public.products\
                                   WHERE movieid = '" + str(movieid) + "'").first()[0]
        price = db_conn.execute("SELECT price \
                                 FROM public.products \
                                 WHERE movieid = '" + str(movieid) + "'").first()[0]
        if not orderid:
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
            orderid = orderid.orderid
            db_result = db_conn.execute("SELECT * FROM orderdetail WHERE orderid = "+ str(orderid) +" AND prod_id = "+ str(prod_id) +"")
            if db_result.all():
                # Ya existen unidades de ese articulo en el carrito
                if sum_units:
                    db_conn.execute("UPDATE orderdetail \
                                     SET quantity = quantity + "+ str(units) +" \
                                     WHERE orderid = "+ str(orderid) +" \
                                     AND prod_id = "+ str(prod_id) +";")
                else:
                    db_conn.execute("UPDATE orderdetail \
                                     SET quantity = "+ str(units) +" \
                                     WHERE orderid = "+ str(orderid) +" \
                                     AND prod_id = "+ str(prod_id) +";")
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


# Elimina el carrito actual de un usuario
def remove_user_cart(username):
    customerid = customerid_from_username(username)
    orderid = get_orderid(customerid).first()
    if not orderid:
        return
    orderid = orderid.orderid
    try:
        db_conn = None
        db_conn = db_engine.connect()
        db_conn.execute("DELETE FROM public.orderdetail \
                         WHERE orderid = "+ str(orderid))
        db_conn.execute("DELETE FROM public.orders \
                         WHERE orderid = "+ str(orderid))
        db_conn.close()
    except:
        db_error(db_conn)


# Elimina el articulo con id movieid del carrito de un usuario
def remove_from_cart(username, movieid):
    customerid = customerid_from_username(username)
    orderid = get_orderid(customerid).first()
    if not orderid:
        return
    orderid = orderid.orderid
    try:
        db_conn = None
        db_conn = db_engine.connect()
        db_result = db_conn.execute("DELETE FROM public.orderdetail \
                                     WHERE orderid = "+ str(orderid) +" \
                                     AND prod_id = (SELECT prod_id FROM public.products WHERE movieid="+ str(movieid) +" LIMIT 1)")
        db_conn.close()
    except:
        db_error(db_conn)


# Devuelve el orderid del pedido actual en el carrito
def get_orderid(customerid, open=True):
    try:
        db_conn = None
        db_conn = db_engine.connect()
        if not open:
            db_result = db_conn.execute("SELECT orderid \
                                         FROM public.orders \
                                         WHERE customerid = '" + str(customerid) + "' \
                                         AND status is not null;")
        else:
            db_result = db_conn.execute("SELECT orderid \
                                        FROM public.orders \
                                        WHERE customerid = '" + str(customerid) + "' \
                                        AND status is null;")
        return db_result
    except:
        db_error(db_conn)


# Devuelve el carrito del usuario
def get_cart(username):
    orderid = get_orderid(customerid_from_username(username)).first()
    if not orderid:
        return
    orderid = orderid.orderid
    try:
        db_conn = None
        db_conn = db_engine.connect()
        db_result = db_conn.execute("SELECT movietitle, o.price, o.quantity \
                                     FROM orderdetail o \
                                     INNER JOIN products p \
                                     ON o.prod_id=p.prod_id \
                                     INNER JOIN imdb_movies m \
                                     ON p.movieid=m.movieid \
                                     WHERE orderid = " + str(orderid))
        db_conn.close()

        cart = []
        for row in db_result:
            pelicula = dict()
            pelicula['titulo'] = row.movietitle
            pelicula['poster'] = "static/img/movies/pulp-fiction.jpeg"
            pelicula['cantidad'] = row.quantity
            pelicula['precio_u'] = float(row.price)
            cart.append(pelicula)
        
        return cart
    except:
        db_error(db_conn)


# Comprueba si hay suficientes unidades del producto solicitado
def check_stock(title, uds):
    try:
        db_conn = None
        db_conn = db_engine.connect()
        db_result = db_conn.execute("SELECT stock FROM inventory i \
                         INNER JOIN products p \
                         ON i.prod_id=p.prod_id \
                         INNER JOIN imdb_movies im \
                         ON p.movieid=im.movieid \
                         WHERE im.movietitle='"+ title +"'")
        db_conn.close()
        stock = int(db_result.first()[0])
        if stock < uds:
            return False
        return True
    except:
        db_error(db_conn)

############# LOYALTY AND BALANCE FUNCTIONS ################

# Devuelve el numero de puntos de un usuario
def get_puntos(username):
    try:
        db_conn = None
        db_conn = db_engine.connect()
        db_result = db_conn.execute("SELECT loyalty \
                                     FROM public.customers \
                                     WHERE username = '"+ username +"';")
        db_conn.close()
        return int(db_result.first()[0])
    except:
        db_error(db_conn)


# Actualiza los puntos de un usuario
def update_puntos(username, puntos, sum_puntos=False):
    try:
        db_conn = None
        db_conn = db_engine.connect()
        if sum_puntos:
            db_conn.execute("UPDATE public.customers \
                             SET loyalty = loyalty + "+ str(puntos) +" \
                             WHERE username = '"+ username +"';")
        else:
            db_conn.execute("UPDATE public.customers \
                                        SET loyalty = "+ str(puntos) +" \
                                        WHERE username = '"+ username +"';")
        db_conn.close()
    except:
        db_error(db_conn)


# Devuelve el saldo de un usuario
def get_saldo(username):
    try:
        db_conn = None
        db_conn = db_engine.connect()
        db_result = db_conn.execute("SELECT balance \
                                     FROM public.customers \
                                     WHERE username = '"+ username +"';")
        db_conn.close()
        return round(float(db_result.first()[0]),2)
    except:
        db_error(db_conn)


# Actualiza el saldo de un usuario
def update_saldo(username, saldo, sum_saldo=False):
    try:
        db_conn = None
        db_conn = db_engine.connect()
        if sum_saldo:
            db_conn.execute("UPDATE public.customers \
                             SET balance = balance + "+ str(saldo) +" \
                             WHERE username = '"+ username +"';")
        else:
            db_conn.execute("UPDATE public.customers \
                             SET balance = "+ str(saldo) +" \
                             WHERE username = '"+ username +"';")
        db_conn.close()
    except:
        db_error(db_conn)


def set_order_paid(username):
    orderid = get_orderid(customerid_from_username(username)).first()
    if not orderid:
        return
    orderid = orderid.orderid
    try:
        db_conn = None
        db_conn = db_engine.connect()
        db_conn.execute("UPDATE public.orders \
                         SET status = 'Paid' \
                         WHERE orderid = '"+ str(orderid) +"';")
        db_conn.close()
    except:
        db_error(db_conn)

################# HISTORY FUNCTIONS #######################
def get_history(username):
    customerid = customerid_from_username(username)
    orderid = get_orderid(customerid, False)
    if not orderid:
        return
    orderid = [id[0] for id in orderid.all()]
    try:
        db_conn = None
        db_conn = db_engine.connect()
        compras = []
        for id in orderid:
            fecha = db_conn.execute("SELECT orderdate FROM orders WHERE orderid=" + str(id)).first()[0]
            status = db_conn.execute("SELECT status FROM orders WHERE orderid=" + str(id)).first()[0]
            db_result = db_conn.execute("SELECT movietitle, o.price, o.quantity\
                                         FROM orderdetail o \
                                         INNER JOIN products p \
                                         ON o.prod_id=p.prod_id \
                                         INNER JOIN imdb_movies m \
                                         ON p.movieid=m.movieid \
                                         WHERE o.orderid = " + str(id))
            compra = {"orderid": id, "fecha": fecha, "status": status, "articulos": []}
            for row in db_result:
                pelicula = dict()
                pelicula["titulo"] = row.movietitle
                pelicula["poster"] = "static/img/movies/pulp-fiction.jpeg"
                pelicula["cantidad"] = row.quantity
                pelicula["precio_u"] = round(float(row.price),2)
                compra["articulos"].append(pelicula)

            compras.append(compra)

        db_conn.close()
        
        compras = sorted(compras, key=lambda d: d["fecha"], reverse=True)
        return compras
    except:
        db_error(db_conn)


################# AUXILIARY FUNCTIONS #####################

# Devuelve el customerid dado el username
def customerid_from_username(username):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()
        customerid = db_conn.execute("SELECT customerid\
                                     FROM public.customers\
                                     WHERE username = '" + username + "'").first()[0]
        db_conn.close()
        return customerid
    except:
        db_error(db_conn)


# Devuelve el customerid dado el username
def movieid_from_title(title):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()
        movieid = db_conn.execute("SELECT movieid\
                                   FROM public.imdb_movies\
                                   WHERE movietitle = '" + title.replace("'","''") + "';").first()[0]
        db_conn.close()
        return movieid
    except:
        db_error(db_conn)


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