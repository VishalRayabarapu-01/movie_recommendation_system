import streamlit as st
import numpy as np
import pandas as pd
from functools import lru_cache
import requests


if 'loading' not in st.session_state:
    st.session_state.loading = True

st.set_page_config(layout="wide")

if st.session_state.loading:
    st.title("Please wait until the app is ready")

@st.cache_resource
def load_docs():
    parts=[]
    for i in range(3):
        parts.append(np.load(f'./array_data_{i}.npy'))
    return np.vstack(parts)

docs = load_docs()

new_movies = pd.read_csv('./cleaned_csv_3.csv')

st.session_state.loading = False

st.title("Movie Recommendation System")
st.write("Find your next favorite movie!")

movie_name = st.text_input("Enter a movie name:")

@lru_cache(maxsize=128)
def get_top_15_indexes(name):
    num = new_movies[new_movies['normalised_text'] == name].index
    if num.size == 0:
        num = new_movies[new_movies['title'] == name].index
    if num.size != 0:
        sorted_indices_desc = docs[num].argsort()[0][::-1]
        return sorted_indices_desc
    else:
        return np.array([])

def fetch_movie_poster(imdb_id, retries=3, delay=2):
    url = f"https://api.themoviedb.org/3/find/{imdb_id}?external_source=imdb_id"
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyMTUxYTZjMDc3ZGQxZWQzMzBiZjYwMTYyODUzZjg0NSIsInN1YiI6IjY2M2UwNzQ3NTMyNzIzYWYzYTAyN2NiOCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.p5FOXZYvR7ug39CfZnPCSFJLlXClVBH_3PHcZNDRFGU"
    }
    for _ in range(retries):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return 'https://image.tmdb.org/t/p/original/' + response.json()['movie_results'][0]['poster_path']
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            return None
        except requests.exceptions.RequestException as e:
            return None
    return None

if movie_name:
    movie_indexes = get_top_15_indexes(movie_name)
    if movie_indexes.size != 0:
        num_per_row = 5
        num_rows = 4
        for i in range(num_rows):
            cols = st.columns(num_per_row)
            for j, col in enumerate(cols):
                index = i * num_per_row + j + 1 
                if index < len(movie_indexes):
                    movie_title = new_movies.iloc[movie_indexes[index]]['title']
                    imdb_id = new_movies.iloc[movie_indexes[index]]['imdb_id']
                    poster_url = fetch_movie_poster(imdb_id)
                    if poster_url:
                        col.image(poster_url, caption=movie_title, use_column_width=True)
                    else:
                        col.write(f"No poster available for {movie_title}")
    else:
        st.write("Enter the movie name correctly")
else:
    st.write("Please enter a movie name to get recommendations.")
