# -*- coding: utf-8 -*-

import os
import sys, traceback, time

from sqlalchemy import create_engine
from pymongo import MongoClient

# configurar el motor de sqlalchemy
db_engine = create_engine("postgresql://alumnodb:alumnodb@localhost/si1", echo=False, execution_options={"autocommit":False})

# Crea la conexión con MongoDB
mongo_client = MongoClient()

def getMongoCollection(mongoDB_client):
    mongo_db = mongoDB_client.si1
    return mongo_db.topUK

def mongoDBCloseConnect(mongoDB_client):
    mongoDB_client.close()

def dbConnect():
    return db_engine.connect()

def dbCloseConnect(db_conn):
    db_conn.close()

def dbError(db_conn):
    if db_conn is not None:
            db_conn.close()
    print("Exception in DB access:")
    print("-"*60)
    traceback.print_exc(file=sys.stderr)
    print("-"*60)
  
def delCity(city, bFallo, bSQL, duerme, bCommit):
    
    # Array de trazas a mostrar en la página
    dbr=[]

    # - ordenar consultas según se desee provocar un error (bFallo True) o no
    # - ejecutar commit intermedio si bCommit es True
    # - usar sentencias SQL ('BEGIN', 'COMMIT', ...) si bSQL es True
    # - suspender la ejecución 'duerme' segundos en el punto adecuado para forzar deadlock
    # - ir guardando trazas mediante dbr.append()
    
    try:
        #TODO: meter el sleep somewhere
        db_conn = dbConnect()
        trans = beginTransaction(db_conn, bSQL)
        dbr.append("Comienza la transaccion")
        if bFallo:
            dbr.append("Transaccion con fallo")
            # apartado e) borrado de registro en orden incorrecto
            delOrderDetail(db_conn, city) # orden correcto
            dbr.append("Borrado en la tabla orderdetail con exito")
            if bCommit:
                dbr.append("Commit intermedio")
                commitTransaction(db_conn, trans)
                beginTransaction(db_conn, bSQL)
            delCustomer(db_conn, city) # fallo restriccion foreign key
            dbr.append("Borrado en la tabla customers con exito")
            delOrder(db_conn, city)
            dbr.append("Borrado en la tabla orders con exito")
        else:
            # Orden correcto
            delOrderDetail(db_conn, city)
            dbr.append("Borrado en la tabla orderdetail con exito")
            delOrder(db_conn, city)
            dbr.append("Borrado en la tabla orders con exito")
            delCustomer(db_conn, city)
            dbr.append("Borrado en la tabla customers con exito")
    except Exception as e:
        rollbackTransaction(db_conn, trans)
        dbr.append("Ha ocurrido un error: rollback de la transaccion")
    else:
        commitTransaction(db_conn, trans)
        dbr.append("Todo OK: commit de la transaccion")

    dbCloseConnect(db_conn)
        
    return dbr


def delOrderDetail(db_conn, city):
    db_conn.execute("DELETE FROM orderdetail od \
                     USING orders o, customers c \
                     WHERE c.customerid=o.customerid \
                     AND o.orderid=od.orderid \
                     AND c.city='" + city + "'")
        

def delOrder(db_conn, city):
    db_conn.execute("DELETE FROM orders o \
                     USING customers c \
                     WHERE c.customerid=o.customerid \
                     AND c.city='" + city + "'")


def delCustomer(db_conn, city):
    db_conn.execute("DELETE FROM customers \
                     WHERE city='" + city + "'")


def beginTransaction(db_conn, bSQL):
    if bSQL:
        db_conn.execute("BEGIN")
    else:
        return db_conn.begin()
        
def commitTransaction(db_conn, trans):
    if trans:
        trans.commit()
    else:
        db_conn.execute("COMMIT")
        
def rollbackTransaction(db_conn, trans):
    if trans:
        trans.rollback()
    else:
        db_conn.execute("ROLLBACK")