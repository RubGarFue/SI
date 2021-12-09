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

        movie_genres = _getMostRelatedAux()

        for movie in result:
            movieid = str(movie['movieid'])
            ind = movie['movietitle'].rfind('(')
            movie['movietitle'] = movie['movietitle'][:ind-1], 
            movie['year'] = int(movie['year'])
            movie['genres'] = getMovieGenres(movieid)
            movie['directors'] = getMovieDirectors(movieid)
            movie['actors'] = getMovieActors(movieid)

            resultMostRelatedAndRelated = getMostRelatedAndRelatedMovies(movieid, movie_genres)

            movie['most_related_movies'] = resultMostRelatedAndRelated[0]
            if resultMostRelatedAndRelated[1] != None:
                movie['related_movies'] = resultMostRelatedAndRelated[1]
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

def _getMostRelatedAux():
    try:
        db_conn = database.dbConnect()
        db_result = db_conn.execute("SELECT m.movieid, m.movietitle, genre, m.year\
                                     FROM\
                                        (SELECT imdb_movies.movieid, movietitle, year FROM imdb_movies\
                                         INNER JOIN imdb_moviecountries\
                                         ON imdb_movies.movieid = imdb_moviecountries.movieid\
                                         WHERE imdb_moviecountries.country = 'UK'\
                                         ORDER BY year DESC\
                                         LIMIT 400) AS m\
                                     INNER JOIN imdb_moviegenres\
                                     ON imdb_moviegenres.movieid = m.movieid\
                                     ORDER BY movieid")
        database.dbCloseConnect(db_conn)
    except:
        database.dbError(db_conn)
    
    movie_genres = []

    movie = None

    for row in db_result:
        ind = row[1].rfind('(')
        movietitle = row[1][:ind-1] 
        if not movie:
            movie = {'movieid': row[0], 'movietitle': movietitle, 'genres': [row[2]], "year": row[3]}
            continue
        if movietitle == movie['movietitle']:
            movie['genres'].append(row[2])
        else:
            movie_genres.append(movie)
            movie = {'movieid': row[0], 'movietitle': movietitle, 'genres': [row[2]], "year": row[3]}
    
    return movie_genres

def getMostRelatedAndRelatedMovies(movieid, movie_genres):
    genremovie = []

    try:
        db_conn = database.dbConnect()
        db_result = db_conn.execute("SELECT genre\
                                     FROM imdb_movies\
                                     INNER JOIN imdb_moviegenres\
                                     ON imdb_movies.movieid = imdb_moviegenres.movieid\
                                     WHERE imdb_movies.movieid = " + movieid)
        database.dbCloseConnect(db_conn)
    except:
        database.dbError(db_conn)
    
    for row in db_result:
        genremovie.append(row[0])
    
    mostRelated = []
    related = []

    coincidence = len(genremovie)

    for movie in movie_genres:
        if movieid == movie['movieid']:
            continue

        count = 0

        diff = coincidence - len(movie['genres'])

        if diff > coincidence/2 or diff < -coincidence/2:
            continue
        else:
            for genre in movie['genres']:
                if genre in genremovie:
                    count += 1

            if diff == 0 and coincidence - count == 0:
                if len(mostRelated) == 10:
                    continue
                moviedict = {"title": movie['movietitle'], "year": movie['year']}
                mostRelated.append(moviedict)
            
            elif coincidence - count <= coincidence/2:
                if len(related) == 10:
                    continue
                moviedict = {"title": movie['movietitle'], "year": movie['year']}
                related.append(moviedict)
    
    if coincidence == 1:
        related = None

    return mostRelated, related


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