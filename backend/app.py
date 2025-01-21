from flask import Flask, request, jsonify, render_template, redirect, url_for
import psycopg2  # Cambiar sqlite3 por psycopg2
import requests

app = Flask(__name__)

# Configuración de la base de datos PostgreSQL
DB_HOST = 'dpg-cu7dvstsvqrc739830ng-a'  # Cambia con tu host de PostgreSQL en Render
DB_PORT = '5432'  # Puerto predeterminado de PostgreSQL
DB_NAME = 'database_y7oe'  # Nombre de tu base de datos
DB_USER = 'sp4rrow'  # Usuario de tu base de datos
DB_PASSWORD = 'liCiVC4i8RwDWQGv6eXH1sMO8765tUVX'  # Contraseña de tu base de datos

# Función para conectar a la base de datos PostgreSQL
def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            poster_url TEXT,
            year INTEGER,
            rating REAL,
            synopsis TEXT,
            genres TEXT,
            play_url TEXT
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

init_db()

# Rutas para las páginas web
@app.route('/', methods=['GET'])
def home():
    search_query = request.args.get('search', '').strip()  # Obtener parámetro de búsqueda
    conn = get_db_connection()
    cursor = conn.cursor()

    if search_query:
        # Buscar películas que coincidan parcialmente con el nombre
        cursor.execute("SELECT * FROM movies WHERE LOWER(name) LIKE %s", ('%' + search_query.lower() + '%',))
    else:
        # Obtener todas las películas
        cursor.execute("SELECT * FROM movies")

    movies = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('home.html', movies=movies, search_query=search_query)  # Página principal independiente

@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM movies')
    movies = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('dashboard.html', movies=movies)

@app.route('/upload')
def upload_movie():
    return render_template('upload.html')

# API para guardar una película
@app.route('/api/add_movie', methods=['POST'])
def add_movie():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO movies (name, poster_url, year, rating, synopsis, genres, play_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    ''', (data['name'], data['poster_url'], data['year'], data['rating'], 
          data['synopsis'], ','.join(data['genres']), data['play_url']))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Movie added successfully'}), 201

import json

# Agregar al inicio del archivo, después de las importaciones
GENRES = {}

def fetch_genres():
    global GENRES
    tmdb_api_key = "92074445c64b2a5c5f1c980784a79ebc"
    url = f'https://api.themoviedb.org/3/genre/movie/list?api_key={tmdb_api_key}&language=es-MX'
    response = requests.get(url)
    if response.status_code == 200:
        genre_list = response.json().get('genres', [])
        GENRES = {genre['id']: genre['name'] for genre in genre_list}

# Llamar a esta función cuando la aplicación se inicie
fetch_genres()


# API para obtener datos desde TMDB
@app.route('/api/fetch_tmdb', methods=['GET'])
def fetch_tmdb():
    query = request.args.get('query')
    tmdb_api_key = "92074445c64b2a5c5f1c980784a79ebc"
    url = f'https://api.themoviedb.org/3/search/movie?api_key={tmdb_api_key}&language=es-MX&query={query}'
    response = requests.get(url)
    if response.status_code == 200:
        movies = response.json().get('results', [])
        # Mapear géneros
        for movie in movies:
            movie['genre_names'] = [GENRES.get(genre_id, "Desconocido") for genre_id in movie.get('genre_ids', [])]
        return jsonify({'results': movies})
    return jsonify({'results': []}), 404

# Añadimos un filtro para convertir el ratio en estrellas.
@app.template_filter('star_rating')
def star_rating(ratio):
    full_stars = int(ratio)
    half_star = (ratio - full_stars) >= 0.5
    return "⭐" * full_stars + ("✨" if half_star else "")


# API para eliminar una película
@app.route('/api/delete_movie/<int:id>', methods=['DELETE'])
def delete_movie(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM movies WHERE id = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Movie deleted successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)
