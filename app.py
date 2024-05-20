import streamlit as st
import numpy as np
import pandas as pd
from functools import lru_cache
import requests


st.set_page_config(
    page_title="Vishal's movie recommendation",
    page_icon=":rocket:",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def load_docs():
    parts=[]
    for i in range(6):
        parts.append(np.load(f'./array_data_{i}.npy'))
    return np.vstack(parts)

docs = load_docs()

new_movies = pd.read_csv('./cleaned_csv_3.csv')

st.title("Movie Recommendation System")
movie_name = st.selectbox("Find your next favorite movie!",new_movies["title"].values)

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

if st.button('recommend') and len(movie_name)!=0 :
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
