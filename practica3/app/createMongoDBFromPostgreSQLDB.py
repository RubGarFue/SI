import database


def getSQLdata():
    try:
        db_conn = database.dbConnect()
        db_result = db_conn.execute("SELECT m.movieid, m.movietitle, m.\"year\" FROM imdb_movies m \
                                     INNER JOIN imdb_moviecountries mc \
                                     ON m.movieid = mc.movieid \
                                     WHERE mc.country = 'UK' \
                                     ORDER BY m.\"year\" DESC \
                                     LIMIT 400;")
        database.dbCloseConnect(db_conn)
        result = [{column: value for column, value in row._mapping.items()} for row in db_result]
        #return result
        for movie in result:
            movieid = str(movie['movieid'])
            movie['movietitle'] = movie['movietitle'].replace(' (' + movie['year'] + ')', '')
            movie['year'] = int(movie['year'])
            movie['genres'] = getMovieGenres(movieid)
            movie['directors'] = getMovieDirectors(movieid)
            movie['actors'] = getMovieActors(movieid)
            movie['most_related_movies'] = getMostRelatedMovies(movieid)
            movie['related_movies'] = getRelatedMovies(movieid)
        return result
    except:
        database.dbError(db_conn)


def getMovieGenres(movieid):
    try:
        db_conn = database.dbConnect()
        db_result = db_conn.execute("SELECT genre \
                                     FROM imdb_moviegenres \
                                     WHERE movieid = " + movieid)
        database.dbCloseConnect(db_conn)
        return [row[0] for row in db_result]
    except:
        database.dbError(db_conn)


def getMovieDirectors(movieid):
    try:
        db_conn = database.dbConnect()
        db_result = db_conn.execute("SELECT d.directorname \
                                     FROM imdb_directors d \
                                     INNER JOIN imdb_directormovies dm \
                                     ON d.directorid=dm.directorid \
                                     WHERE movieid = " + movieid)
        database.dbCloseConnect(db_conn)
        return [row[0] for row in db_result]
    except:
        database.dbError(db_conn)


def getMovieActors(movieid):
    try:
        db_conn = database.dbConnect()
        db_result = db_conn.execute("SELECT a.actorname \
                                     FROM imdb_actors a \
                                     INNER JOIN imdb_actormovies am \
                                     ON a.actorid =am.actorid \
                                     WHERE movieid = " + movieid)
        database.dbCloseConnect(db_conn)
        return [row[0] for row in db_result]
    except:
        database.dbError(db_conn)


def getMostRelatedMovies(movieid):
    return []


def getRelatedMovies(movieid):
    return []


def createMongoDBFromPostgreSQLDB():
    myClient = database.mongo_client

    # Borrar la base de datos si ya existe
    if 'si1' in myClient.list_database_names():
        myClient.drop_database('si1')
    
    mongodb = myClient['si1']
    ukcol = mongodb['topUK']
    data = getSQLdata()
    ukcol.insert_many(data)

    database.mongoDBCloseConnect(myClient)


if __name__ == "__main__":
    createMongoDBFromPostgreSQLDB()