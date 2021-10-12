#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app
from flask import render_template, request, url_for, redirect, session
from hashlib import blake2b
import json
import os
import sys
import random


@app.route('/')
@app.route('/index')
def index():
    print(url_for('static', filename='css/style.css'), file=sys.stderr)
    catalogue_data = open(os.path.join(
        app.root_path, 'catalogue/catalogue.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)
    return render_template('index.html', title="VIDEOCLUB", movies=catalogue['peliculas'])


@app.route('/login', methods=['GET'])
def show_login():
    return render_template('login.html', title="Videoclub - Iniciar sesión")

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if os.path.isdir('usuarios/' + username):
        hash = blake2b()
        hash.update(password.encode('utf8'))
        password = '{0}'.format(hash.hexadigest())

        file = open('usuarios/' + username + '/data.dat', 'r')
        password_check = file.readlines()[1]
        file.close()

        if password != password_check:
            return render_template('login.html', title="Videoclub - Iniciar sesión")
        
        session['usuario'] = username
        session.modified = True

        return redirect(url_for('index'))
    
    else:
        return render_template('login.html', title="Videoclub - Iniciar sesión")


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('usuario', None)
    return redirect(url_for('index'))


@app.route('/register', methods=['GET'])
def show_register():
    return render_template('register.html', title="Videoclub - Registro")

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    password_confirm = request.form['password_confirm']
    email = request.form['email']
    credit_card = request.form['credit_card']
    direction = request.form['direction']

    os.mkdir('usuarios/' + username)

    file = open('usuarios/' + username + '/data.dat', 'w')
    file.write(username + '\n')

    hash = blake2b()
    hash.update(password.encode('utf8'))
    file.write('{0}'.format(hash.hexadigest()) + '\n')

    file.write(email + '\n' + credit_card + '\n')
    file.write(str(random.randint(0, 100)))

    file.close()

    return render_template('login.html', title="Videoclub - Iniciar sesión")


@app.route('/movie/<movie_id>', methods=['GET', 'POST'])
def movie(movie_id):
    catalogue_data = open(os.path.join(
        app.root_path, 'catalogue/catalogue.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)
    peli = catalogue["peliculas"][int(movie_id)]
    return render_template('movie.html', title="Videoclub - " + peli["titulo"], movie=peli)


@app.route('/history', methods=['GET', 'POST'])
def history():
    return render_template('history.html', title="Videoclub - Historial de compras")


@app.route('/shopping-cart', methods=['GET', 'POST'])
def shopping_cart():
    return render_template('shopping-cart.html', title="Videoclub - Carrito de la compra")



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
