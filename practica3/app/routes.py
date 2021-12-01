#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app
from app import database
from flask import render_template, request, url_for
import re


@app.route('/', methods=['POST','GET'])
@app.route('/index', methods=['POST','GET'])
def index():
    return render_template('index.html')


@app.route('/borraCiudad', methods=['POST','GET'])
def borraCiudad():
    if 'city' in request.form:
        city    = request.form["city"]
        bSQL    = request.form["txnSQL"]
        bCommit = "bCommit" in request.form
        bFallo  = "bFallo"  in request.form
        duerme  = request.form["duerme"]
        dbr = database.delCity(city, bFallo, bSQL=='1', int(duerme), bCommit)
        return render_template('borraCiudad.html', dbr=dbr)
    else:
        return render_template('borraCiudad.html')

    
@app.route('/topUK', methods=['POST','GET'])
def topUK():
    colUK = database.getMongoCollection(database.mongo_client)

    query_a = {"genres": "Sci-Fi", "year": {"$gt": 1993, "$lt": 1999}}
    result_a = colUK.find(query_a)
    movies_a = [mov for mov in result_a]

    query_b = {"movietitle": {"$regex": '^.*, The$'}, "genres": "Drama", "year": 1998}
    result_b = colUK.find(query_b)
    movies_b = [mov for mov in result_b]

    query_c = {"$and": [{"actors": "Roberts, Julia"}, {"actors": "Baldwin, Alec"}]}
    result_c = colUK.find(query_c)
    movies_c = [mov for mov in result_c]

    movies=[movies_a, movies_b, movies_c]
    return render_template('topUK.html', movies=movies)