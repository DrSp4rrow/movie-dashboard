document.getElementById('fetch-tmdb').addEventListener('click', () => {
    const movieName = document.getElementById('movie-name').value;

    fetch(`/api/fetch_tmdb?query=${movieName}`)
        .then(response => response.json())
        .then(data => {
            const resultsContainer = document.getElementById('search-results');
            const resultList = document.getElementById('result-list');
            resultList.innerHTML = ''; // Limpiar resultados previos

            if (data.results.length > 0) {
                resultsContainer.style.display = 'block';

                data.results.forEach(movie => {
                    const listItem = document.createElement('li');
                    listItem.textContent = `${movie.title} (${movie.release_date.split('-')[0]})`;
                    listItem.addEventListener('click', () => {
                        // Autorrellenar campos al seleccionar una película
                        document.getElementById('movie-name').value = movie.title;
                        document.getElementById('poster-url').value = `https://image.tmdb.org/t/p/w500${movie.poster_path}`;
                        document.getElementById('poster-preview').src = `https://image.tmdb.org/t/p/w500${movie.poster_path}`;
                        document.getElementById('poster-preview').style.display = 'block';
                        document.getElementById('year').value = movie.release_date.split('-')[0];
                        document.getElementById('rating').value = parseFloat(movie.vote_average).toFixed(1); // Redondear Ratio
                        document.getElementById('synopsis').value = movie.overview;
                        document.getElementById('genres').value = movie.genre_names.join(', '); // Mostrar nombres de géneros

                        resultsContainer.style.display = 'none'; // Ocultar resultados
                    });
                    resultList.appendChild(listItem);
                });
            } else {
                alert('No se encontraron películas.');
            }
        });
});

document.getElementById('movie-form').addEventListener('submit', event => {
    event.preventDefault();
    const movieData = {
        name: document.getElementById('movie-name').value,
        poster_url: document.getElementById('poster-url').value,
        year: parseInt(document.getElementById('year').value),
        rating: parseFloat(document.getElementById('rating').value),
        synopsis: document.getElementById('synopsis').value,
        genres: document.getElementById('genres').value.split(','),
        play_url: document.getElementById('play-url').value,
    };
    fetch('/api/add_movie', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(movieData),
    })
        .then(response => response.json())
        .then(data => alert(data.message));
});
