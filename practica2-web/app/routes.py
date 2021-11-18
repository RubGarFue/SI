#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app
from app import database
from flask import render_template, request, url_for, redirect, session
from hashlib import blake2b
from datetime import date
import json
import os
import sys
import random


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    print(url_for('static', filename='css/style.css'), file=sys.stderr)

    # CARGAR CATEGORIAS DISPONIBLES
    genres = sorted(database.getGenres())

    # CARGAR CATALOGO
    catalogue = database.getCatalogue()

    # BUSCADOR
    if request.method == 'POST':
        if request.form['search-button'] == 'search':
            # search and filter
            text = request.form['search-text'].lower()
            genre = request.form.get('filter')
            if text and genre:
                new_catalogue = database.getCatalogue(search=text, genre=genre)
            elif text:
                new_catalogue = database.getCatalogue(search=text.lower())
            elif genre:
                new_catalogue = database.getCatalogue(genre=genre)
            else:
                new_catalogue = catalogue

            # update subtitle
            subtitle = "Resultados"
            if text:
                subtitle += " para '" + text + "'"
            if genre:
                subtitle += " de la categoría " + genre.lower()

            return render_template('index.html', title="VIDEOCLUB",
                                   subtitle=subtitle, genres=genres,
                                   movies=new_catalogue)

    return render_template(
        'index.html', subtitle="Cartelera actual", genres=genres,
        movies=catalogue)


@app.route('/login', methods=['GET'])
def show_login():
    return render_template('login.html', title="Videoclub - Iniciar sesión")


@app.route('/login', methods=['POST'])
def login():
    message = ""
    salt = "laurayrubensonlosmejores"

    username = request.form['username']
    password = request.form['password']

    #password += salt

    # Comprobamos que el usuario introducido existe en la carpeta "usuarios"
    if database.userExists(username):
        # Comprobamos que el formato de usuario sea correcto
        if not database.checkUser(username, password):
            message = "La contraseña no es correcta"
            return render_template(
                'login.html', title="Videoclub - Iniciar sesión",
                message=message)

        # Hacemos que la sea propia del usuario
        _user_shopping_cart(username)

        # Modificamos la sesión y volvemos a index
        session['usuario'] = username
        session.modified = True

        return redirect(url_for('index'))

    else:
        # Si no existe mesnaje de error y retornamos
        message = "No existe el usuario introducido"

        return render_template(
            'login.html', title="Videoclub - Iniciar sesión", message=message)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('usuario', None)
    session.modified = True
    return redirect(url_for('index'))


@app.route('/register', methods=['GET'])
def show_register():
    return render_template('register.html', title="Videoclub - Registro")


@app.route('/register', methods=['POST'])
def register():
    message = ""
    salt = "laurayrubensonlosmejores"

    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    credit_card = request.form['credit-card']
    direction = request.form['direction']

    #password += salt

    # Comprobamos si el usuario ya existe en la carpeta "usuarios"
    if database.userExists(username):
        message = "El usuario introducido ya existe"
        return render_template(
            'register.html', title="Videoclub - Registro", message=message)

    # Creamos una carpeta con el nombre del usuario
    #os.mkdir('app/usuarios/' + username)

    # Registramos el nuevo usuario
    database.register(username, password, email, credit_card, direction)

    # Creamos un historial json
    #file = open('app/usuarios/' + username + '/historial.json', 'w')

    #file.write('{\n\t\"compras\": []\n}')

    #file.close()

    # Creamos una cesta de la compra json
    file = open('app/usuarios/' + username + '/shopping_cart.json', 'w')

    file.write('{\n\t\"articulos\": []\n}')

    file.close()

    return render_template(
        'login.html', title="Videoclub - Iniciar sesión", message=message)


@app.route('/movie/<int:movie_id>', methods=['GET', 'POST'])
def movie(movie_id):
    peli = database.getMovie(movie_id)

    peli["poster"] = "static/img/movies/pulp-fiction.jpeg"

    # Add to cart
    if request.method == "POST":
        if request.form['add-to-cart'] == 'add':
            units = int(request.form['units'])
            # Leemos el json
            #file_data = _read_shopping_cart()
            if 'usuario' not in session:
                with open('app/shopping_cart/shopping_cart.json', 'r+') as file:
                    file_data = json.load(file)

                # Si la pelicula esta actualizamos unidades
                new_film = True
                for articulo in file_data['articulos']:
                    if articulo['titulo'] == peli['titulo']:
                        articulo['cantidad'] += units
                        new_film = False
                        break
                # Si no añadimos nueva entrada
                if new_film:
                    articulo = {'id': peli['id'],
                                'titulo': peli['titulo'],
                                'poster': peli['poster'],
                                'cantidad': units,
                                'precio_u': float(peli['precio'])}

                    file_data['articulos'].append(articulo)

                # Escribimos el json
                with open('app/shopping_cart/shopping_cart.json', 'w') as file:
                    json.dump(file_data, file)
            else:
                database.update_cart(session['usuario'], peli['id'], units, True)

            #_write_shopping_cart(file_data)
    return render_template(
        'movie.html', title="Videoclub - " + peli["titulo"], movie=peli)


@app.route('/history', methods=['GET', 'POST'])
def history():
    if 'usuario' not in session:
        return render_template(
            'login.html', title="Videoclub - Iniciar sesión", message="")

    # Update data.dat (saldo)
    #with open('app/usuarios/' + session['usuario'] + '/data.dat', 'r') as file:
    #    data = file.readlines()

    #saldo = float(data[-2])
    #puntos = data[-1]
    saldo = database.get_saldo(session['usuario'])
    puntos = database.get_puntos(session['usuario'])

    # update balance
    if request.method == "POST":
        if request.form['add-balance-button'] == 'add':
            amount = float(request.form['add-balance'])
            database.update_saldo(session['usuario'], round(float(amount),2), True)
            saldo = database.get_saldo(session['usuario'])
            #saldo = str(round(saldo + amount, 2))
            #data[-2] = saldo + '\n'
            #data[-1] = puntos

            #with open('app/usuarios/' + session['usuario'] + '/data.dat',
            #          'w') as file:
            #    file.writelines(data)

    #history = get_history(session['usuario'])
    history = database.get_history(session['usuario'])
    return render_template('history.html', saldo=saldo,
                           puntos=puntos, compras=history)


@app.route('/shopping-cart', methods=['GET', 'POST'])
def shopping_cart():
    if 'usuario' in session:
        # Leemos carrito de la base de datos
        my_movies = database.get_cart(session['usuario'])

        # Si no hay articulos devolvemos cesta vacia
        if not my_movies:
            return render_template('shopping-cart.html', message="")
    else:
        # Leemos carrito del json
        file_data = _read_shopping_cart()

        # Si no hay articulos devolvemos cesta vacia
        if not file_data['articulos']:
            return render_template('shopping-cart.html', message="")

        # Si hay articulos los ponemos en my_movies
        my_movies = []
        for articulo in file_data['articulos']:
            my_movies.append(articulo)

    if request.method == 'GET':
        return render_template('shopping-cart.html',
                                products=my_movies, message="")

    if request.method == 'POST':
        # comprobamos si estamos logeados
        if 'usuario' not in session:
            return render_template(
                'login.html', title="Videoclub - Iniciar sesión", message="")


        # Obtenemos el precio total de la compra
        #shopping_cart_data = _read_shopping_cart()

        # Calculamos el precio total de los artículos 
        # y comprobamos si hay articulos suficientes en inventory
        precio_total = 0
        #for articulo in shopping_cart_data['articulos']:
        for articulo in my_movies:
            precio = float(articulo['precio_u'])
            uds = int(articulo['cantidad'])
            precio_total += precio * uds
            if not database.check_stock(articulo['titulo'], uds):
                message = "No disponemos de " + str(uds) + " unidades del articulo '"+ articulo['titulo'] +"'\nLo sentimos :("
                return render_template(
                    'shopping-cart.html', products=my_movies, message=message)

        #with open('app/usuarios/' + session['usuario'] + '/data.dat',
        #          'r') as file:
        #    data = file.readlines()
        #    saldo = float(data[-2][:-1])
        #    puntos = int(data[-1])
        saldo = database.get_saldo(session['usuario'])
        puntos = database.get_puntos(session['usuario'])

        method = request.form['payment-method']
        if method == "puntos":
            # Comprobamos si el usuario tiene puntos suficientes
            if puntos < round(precio_total * 100, 2):
                message = "No tiene los puntos suficientes para realizar la c"\
                          "ompra (100 puntos equivalen a 1e)"
                return render_template(
                    'shopping-cart.html', products=my_movies, message=message)
            #new_saldo = saldo
            #new_puntos = int(puntos - precio_total * 100)
            database.update_puntos(session['usuario'], int(puntos - precio_total * 100))
        elif method == "saldo":
            # Comprobamos si el usuario tiene el saldo suficiente
            if saldo < precio_total:
                message = "No tiene el saldo suficiente para realizar la comp"\
                          "ra"
                return render_template(
                    'shopping-cart.html', products=my_movies, message=message)
            #new_saldo = saldo - precio_total
            #new_puntos = puntos
            database.update_saldo(session['usuario'], saldo - precio_total)

        # Sumamos puntos por la compra
        #new_puntos += int(0.05 * precio_total)
        database.update_puntos(session['usuario'], int(0.05 * precio_total), True)

        # Abrimos el archivo json
        #file = open(
        #    'app/usuarios/' +
        #    session['usuario'] +
        #    '/historial.json',
        #    'r+')
        #file_data = json.load(file)

        database.set_order_paid(session['usuario'])
        # comprobamos si ya se han hecho compras durante el día
        #fecha = date.today()
        #fecha = fecha.strftime('%d/%m/%Y')

        #try:
        #    if fecha not in file_data['compras'][-1].values():
        #        file_data['compras'].append({"fecha": fecha, "articulos": []})
        #except IndexError:
        #    file_data['compras'].append({"fecha": fecha, "articulos": []})

        # escribimos cada artículo
        # articulo representa un articulo del shopping_cart y movie_hist una
        # peliucla del historial
        #for articulo in shopping_cart_data['articulos']:
        #for articulo in my_movies:
        #    new_film = True

        #    for movie_hist in file_data['compras'][-1]['articulos']:
        #        if articulo['titulo'] == movie_hist['titulo']:
        #            movie_hist['cantidad'] += articulo['cantidad']
        #            new_film = False
        #            break

        #    if not new_film:
        #        continue

        #    file_data['compras'][-1]['articulos'].append(articulo)
        #file.close()

        #with open('app/usuarios/' + session['usuario'] + '/historial.json',
        #          'w') as file:
        #    json.dump(file_data, file)

        # Actualizamos el data.dat (saldo y puntos)
        #with open('app/usuarios/' + session['usuario'] + '/data.dat',
        #          'r') as file_dat:
        #    data = file_dat.readlines()

        #data[-2] = str(round(new_saldo, 2)) + '\n'
        #data[-1] = str(new_puntos)

        #with open('app/usuarios/' + session['usuario'] + '/data.dat',
        #          'w') as file_dat:
        #    file_dat.writelines(data)

        # Vaciamos el historial
        #file = open(
        #    'app/usuarios/' +
        #    session['usuario'] +
        #    '/shopping_cart.json',
        #    'w')

        #file.write('{\n\t\"articulos\": []\n}')
        #file.close()

        return redirect(url_for('index'))


def _user_shopping_cart(username):
    # Comprobamos si la cesta sin usuario no esta vacia
    file_data = _read_shopping_cart()['articulos']
    if not file_data: 
        return

    database.remove_user_cart(username)
    for article in file_data:
        database.update_cart(username, article['id'], article['cantidad'])

    # Limpiamos el json antigo
    file = open('app/shopping_cart/shopping_cart.json', 'w')
    file.write('{\n\t\"articulos\": []\n}')
    file.close()


def _read_shopping_cart():
    path = 'app/shopping_cart/shopping_cart.json'

    with open(path, 'r+') as file:
        file_data = json.load(file)

    return file_data


def _write_shopping_cart(file_data):
    if 'usuario' not in session:
        path = 'app/shopping_cart/shopping_cart.json'
    else:
        path = 'app/usuarios/' + session['usuario'] + '/shopping_cart.json'

    with open(path, 'w') as file:
        json.dump(file_data, file)

    return


@app.route('/shopping-cart/update/<string:titulo>', methods=['GET', 'POST'])
def shopping_cart_update(titulo):
    if request.method == "POST":

        if request.form['update'] == 'update':
            units = int(request.form['units'])

            if 'usuario' in session:
                movieid = database.movieid_from_title(titulo)
                database.update_cart(session['usuario'], movieid, units)
            else:
                file_data = _read_shopping_cart()
                for articulo in file_data['articulos']:
                    if articulo['titulo'] == titulo:
                        articulo['cantidad'] = units
                        break
                _write_shopping_cart(file_data)

        elif request.form['update'] == 'remove':
            if 'usuario' in session:
                movieid = database.movieid_from_title(titulo)
                database.remove_from_cart(session['usuario'], movieid)
            else:
                file_data = _read_shopping_cart()
                for articulo in file_data['articulos']:
                    if articulo['titulo'] == titulo:
                        file_data['articulos'].remove(articulo)
                        break
                _write_shopping_cart(file_data)

        return redirect(url_for('shopping_cart'))


def get_movies():
    catalogue_data = open(os.path.join(
        app.root_path, 'catalogue/catalogue.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)
    return catalogue["peliculas"]


def get_history(user):
    history_data = open(os.path.join(
        app.root_path, 'usuarios/' + user + '/historial.json'),
        encoding="utf-8").read()
    history = json.loads(history_data)
    return history['compras']


@app.route('/numusers')
def numusers():
    return str(random.randint(1, 100))
