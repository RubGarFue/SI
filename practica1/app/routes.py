#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app
from flask import render_template, request, url_for, redirect, session, flash
from hashlib import blake2b
from datetime import date
import json
import os
import sys
import random


@app.route('/')
@app.route('/index', methods=['GET','POST'])
def index():
    print(url_for('static', filename='css/style.css'), file=sys.stderr)
    
    catalogue = get_movies()

    # CARGAR CATEGORIAS DISPONIBLES
    genres = set()
    for mov in catalogue:
        genres.update(mov['categoria'])
    genres = sorted(genres)

    # BUSCADOR
    if request.method == 'POST':
        if request.form['search-button'] == 'search':
            # search bar
            text = request.form['search-text']
            catalogue = [mov for mov in catalogue if text.lower() in mov['titulo'].lower()]

            # filter genre
            genre = request.form.get('filter')
            if genre: 
                catalogue = [mov for mov in catalogue if genre in mov['categoria']]

            # update subtitle
            subtitle = "Resultados"
            if text:
                subtitle += " para '" + text  + "'" 
            if genre:
                subtitle += " de la categoría " + genre.lower() 

            return render_template('index.html', title="VIDEOCLUB", subtitle=subtitle, genres=genres, movies=catalogue)

    return render_template('index.html', subtitle="Cartelera actual", genres=genres, movies=catalogue)


@app.route('/login', methods=['GET'])
def show_login():
    return render_template('login.html', title="Videoclub - Iniciar sesión")


@app.route('/login', methods=['POST'])
def login():
    message=""
    salt = "laurayrubensonlosmejores"

    username = request.form['username']
    password = request.form['password']

    password += salt

    if os.path.isdir('app/usuarios/' + username):
        hash = blake2b()
        hash.update(password.encode('utf8'))
        password = '{0}'.format(hash.hexdigest())

        file = open('app/usuarios/' + username + '/data.dat', 'r')
        password_check = file.readlines()[1][:-1]
        file.close()

        if password != password_check:
            message = "La contraseña no es correcta"
            return render_template('login.html', title="Videoclub - Iniciar sesión", message=message)
        
        # Hacemos que la sea propia del usuario
        _user_shopping_cart(username)

        session['usuario'] = username
        session.modified = True

        return redirect(url_for('index'))
    
    else:
        message = "No existe el usuario introducido"

        return render_template('login.html', title="Videoclub - Iniciar sesión", message=message)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('usuario', None)
    #session.pop('shopping_cart')
    session.modified = True
    return redirect(url_for('index'))


@app.route('/register', methods=['GET'])
def show_register():
    return render_template('register.html', title="Videoclub - Registro")


@app.route('/register', methods=['POST'])
def register():
    message=""
    salt = "laurayrubensonlosmejores"

    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    credit_card = request.form['credit-card']
    direction = request.form['direction']

    password += salt

    if os.path.isdir('app/usuarios/' + username):
        message = "El usuario introducido ya existe"
        return render_template('register.html', title="Videoclub - Registro", message=message)

    os.mkdir('app/usuarios/' + username)

    file = open('app/usuarios/' + username + '/data.dat', 'w')
    file.write(username + '\n')

    hash = blake2b()
    hash.update(password.encode('utf8'))
    file.write('{0}'.format(hash.hexdigest()) + '\n')

    file.write(email + '\n' + direction + '\n' + credit_card + '\n')
    file.write(str(random.randint(0, 100)))

    file.write('\n0')

    file.close()

    # Creamos un historial json
    file = open('app/usuarios/' + username + '/historial.json', 'w')
    
    file.write('{\n\t\"compras\": []\n}')

    file.close()

    # Creamos una cesta de la compra json
    file = open('app/usuarios/' + username + '/shopping_cart.json', 'w')
    
    file.write('{\n\t\"articulos\": []\n}')

    file.close()
    
    return render_template('login.html', title="Videoclub - Iniciar sesión", message=message)


@app.route('/movie/<int:movie_id>', methods=['GET', 'POST'])
def movie(movie_id):
    catalogue = get_movies()
    peli = catalogue[movie_id]

    # Add to cart
    if request.method == "POST":
        if request.form['add-to-cart'] == 'add':
            units = int(request.form['units'])
            
            # Leemos el json
            file_data = _read_shopping_cart()
            
            # Si la pelicula esta actualizamos unidades
            new_film = True
            for articulo in file_data['articulos']:
                if articulo['titulo'] == peli['titulo']:
                    articulo['cantidad'] += units
                    new_film = False
                    break
            
            # Si no añadimos nueva entrada
            if new_film:
                articulo = {'titulo': peli['titulo'],
                            'poster': peli['poster'],
                            'cantidad': units,
                            'precio_u': peli['precio']}
                
                file_data['articulos'].append(articulo)
            
            # Escribimos el json
            _write_shopping_cart(file_data)

            '''
            units = int(request.form['units'])
            if session.get('shopping_cart'):
                session['shopping_cart'][movie_id] = session['shopping_cart'].get(movie_id,0) + units
            else:
                session['shopping_cart'] = {movie_id: units}
            session.modified=True
            '''
    return render_template('movie.html', title="Videoclub - " + peli["titulo"], movie=peli)


@app.route('/history', methods=['GET', 'POST'])
def history():
    if 'usuario' not in session:
        return render_template('login.html', title="Videoclub - Iniciar sesión", message="")

    # Update data.dat (saldo)
    with open('app/usuarios/' + session['usuario'] + '/data.dat', 'r') as file:
        data = file.readlines()
    
    saldo = float(data[-2])
    puntos = data[-1]

    # update balance
    if request.method == "POST":
        if request.form['add-balance-button'] == 'add':
            amount = round(float(request.form['add-balance']),2)
            saldo = str(saldo + amount)
            data[-2] = saldo + '\n'
            data[-1] = puntos

            with open('app/usuarios/' + session['usuario'] + '/data.dat', 'w') as file:
                file.writelines(data)

    history = get_history(session['usuario'])
    return render_template('history.html', saldo=saldo, puntos=puntos, compras=history)


@app.route('/shopping-cart', methods=['GET', 'POST'])
def shopping_cart():
    catalogue = get_movies()
    
    # Leemos el json
    file_data = _read_shopping_cart()

    # Si no hay articulos devolvemos cesta vacia
    if not file_data['articulos']:
        return render_template('shopping-cart.html', message="")
    
    # Si hay articulos los ponemos en my_movies
    my_movies = []
    for articulo in file_data['articulos']:
        my_movies.append(articulo)
    
    '''
    if not session.get('shopping_cart'):
        return render_template('shopping-cart.html', message="")
    my_movies = []
    for movie_ind, units in session['shopping_cart'].items():
        movie = catalogue[int(movie_ind)]
        movie['unidades'] = units
        my_movies.append(movie)
    '''
    
    if request.method == 'GET':
        return render_template('shopping-cart.html', products=my_movies, message="")
    
    if request.method == 'POST':
        #comprobamos si estamos logeados
        if 'usuario' not in session:
            return render_template('login.html', title="Videoclub - Iniciar sesión", message="")
        
        # Comprobamos si el usuario tiene el saldo suficiente
        with open('app/usuarios/' + session['usuario'] + '/data.dat', 'r') as file:
            saldo = float(file.readlines()[-2][:-1])
        
        precio_total = 0
        
        shopping_cart_data = _read_shopping_cart()

        for articulo in shopping_cart_data['articulos']:
            precio = float(articulo['precio_u'])
            uds = int(articulo['cantidad'])

            precio_total += precio * uds

        '''
        for movie_id, items in session['shopping_cart'].items():
            
            precio = movie['precio']
            uds = items

            precio_total += precio*uds
        '''
            
        if saldo < precio_total:
            message = "No tiene el saldo suficiente para realizar la compra"
            return render_template('shopping-cart.html', products=my_movies, message=message)

        # Abrimos el archivo json
        file = open('app/usuarios/' + session['usuario'] + '/historial.json', 'r+')
        file_data = json.load(file)

        #comprobamos si ya se han hecho compras durante el día
        fecha = date.today()
        fecha = fecha.strftime('%d/%m/%Y')

        try:
            if fecha not in file_data['compras'][-1].values():
                file_data['compras'].append({"fecha": fecha, "articulos": []})
        except IndexError:
            file_data['compras'].append({"fecha": fecha, "articulos": []})

        # escribimos cada artículo
        # articulo representa un articulo del shopping_cart y movie_hist una peliucla del historial
        for articulo in shopping_cart_data['articulos']:
            new_film = True

            for movie_hist in file_data['compras'][-1]['articulos']:
                if articulo['titulo'] == movie_hist['titulo']:
                    movie_hist['cantidad'] += articulo['cantidad']
                    new_film = False
                    break
            
            if not new_film:
                continue

            file_data['compras'][-1]['articulos'].append(articulo)
        
        '''
        for movie_id , items in session['shopping_cart'].items():
            nueva_peli = 1

            movie = get_movies()[int(movie_id)]
            titulo = movie['titulo']
            poster = movie['poster']
            precio = movie['precio']
            uds = items

            for articulo in file_data['compras'][-1]['articulos']:
                if titulo in articulo.values():
                    articulo['cantidad'] += uds
                    nueva_peli = 0
                    break
            
            if nueva_peli == 0:
                continue

            articulo = {"titulo": titulo, "poster": poster, "cantidad": uds, "precio_u": precio}
            file_data['compras'][-1]['articulos'].append(articulo)
        '''
        
        file.close()
        
        with open('app/usuarios/' + session['usuario'] + '/historial.json', 'w') as file:
            json.dump(file_data, file)

        # Actualizamos el data.dat (saldo y puntos)
        with open('app/usuarios/' + session['usuario'] + '/data.dat', 'r') as file_dat:
            data = file_dat.readlines()
        
        data[-2] = str(round(float(data[-2]) - precio_total, 2)) + '\n'
        data[-1] = str(int(data[-1]) + int(0.05*precio_total))

        with open('app/usuarios/' + session['usuario'] + '/data.dat', 'w') as file_dat:
            file_dat.writelines(data)
        
        # Vaciamos el historial
        file = open('app/usuarios/' + session['usuario'] + '/shopping_cart.json', 'w')
    
        file.write('{\n\t\"articulos\": []\n}')

        file.close()

        # Vaciamos la shoopping_cart
        #session.pop('shopping_cart')
        #session.modified = True

        return redirect(url_for('index'))


def _user_shopping_cart(user):
    
    # Movemos el json a la carpeta de usuario
    path_src = 'app/shopping_cart/shopping_cart.json'
    path_dst = 'app/usuarios/' + user + '/shopping_cart.json'

    # Comprobamos si la cesta sin usuario no esta vacia
    if _read_shopping_cart()['articulos']:
        os.replace(path_src, path_dst)

        # Creamos un nuevo json
        file = open('app/shopping_cart/shopping_cart.json', 'w')
        
        file.write('{\n\t\"articulos\": []\n}')

        file.close()
    return

def _read_shopping_cart():
    if 'usuario' not in session:
        path = 'app/shopping_cart/shopping_cart.json'
    else:
        path = 'app/usuarios/' + session['usuario'] + '/shopping_cart.json'

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
    #!! Seria mejor cambiar el argumento de entrada movie_id por titulo
    #for pelicula in get_movies():
    #    if pelicula['id'] == movie_id:
    #        titulo = pelicula['titulo']

    if request.method == "POST":
        # Leemos el json
        file_data = _read_shopping_cart()

        if request.form['update'] == 'update':
            units = int(request.form['units'])
            
            for articulo in file_data['articulos']:
                if articulo['titulo'] == titulo:
                    articulo['cantidad'] = units
                    break

        elif request.form['update'] == 'remove':
            for articulo in file_data['articulos']:
                if articulo['titulo'] == titulo:
                    file_data['articulos'].remove(articulo)
                    break
        
        # Escribimos el json
        _write_shopping_cart(file_data)

        return redirect(url_for('shopping_cart'))
        '''
        if request.form['update'] == 'update':
            units = int(request.form['units'])
            session['shopping_cart'][movie_id] = units
            session.modified=True
        elif request.form['update'] == 'remove':
            session['shopping_cart'].pop(movie_id)
            session.modified=True
        return redirect(url_for('shopping_cart'))
        '''


def get_movies():
    catalogue_data = open(os.path.join(
        app.root_path, 'catalogue/catalogue.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)
    return catalogue["peliculas"]


def get_history(user):
    history_data = open(os.path.join(
        app.root_path, 'usuarios/' + user + '/historial.json'), encoding="utf-8").read()
    history = json.loads(history_data)
    return history['compras']


@app.route('/numusers')
def numusers():
    return str(random.randint(1,100))


'''
@app.route('/login', methods=['GET', 'POST'])
def login():
    # doc sobre request object en http://flask.pocoo.org/docs/1.0/api/#incoming-request-data
    if 'username' in request.form:
        # aqui se deberia validar con fichero .dat del usuario
        if request.form['username'] == 'pp':
            session['usuario'] = request.form['username']
            session.modified=True
            # se puede usar request.referrer para volver a la pagina desde la que se hizo login
            return redirect(url_for('index'))
        else:
            # aqui se le puede pasar como argumento un mensaje de login invalido
            return render_template('login.html', title = "Sign In")
    else:
        # se puede guardar la pagina desde la que se invoca 
        session['url_origen']=request.referrer
        session.modified=True        
        # print a error.log de Apache si se ejecuta bajo mod_wsgi
        print (request.referrer, file=sys.stderr)
        return render_template('login.html', title = "Sign In")

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('usuario', None)
    return redirect(url_for('index'))
'''
