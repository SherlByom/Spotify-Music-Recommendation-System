import joblib
import pandas as pd
from flask import Flask, request, jsonify
from Packages.autoencoder import AutoEncoder

app = Flask(__name__)

model = joblib.load("Models/autoencoder.pkl")
model_kn = joblib.load("Models/knn.pkl")
scaler = joblib.load("Models/scaler.pkl")
embeddings = joblib.load("Models/embeddings.pkl")
df = pd.read_csv("Models/cleaned_dataset.csv")

model_kn.fit(embeddings)

def get_song_index(song_name):
    result = df[df["TRACK_NAME"].str.upper() == song_name.upper()]

    if len(result) == 0:
        return None

    return result.index[0]

def get_song_suggestion(song_name_input, k = 5):
    index = get_song_index(song_name_input)

    if (index == None):
        return None, None

    distances, indices = model_kn.kneighbors([embeddings[index]], n_neighbors = k + 1)

    return df.iloc[indices[0]][["TRACK_NAME", "TRACK_GENRE"]], distances

test_songs = [
    # Your existing ones
    "Kun Faya Kun",
    "unravel",
    "Boba Tunnel",
    "Aniket Prantor",
    "Choo Lo",
    "Stairway to Heaven - Remaster",
    
    # Indian / Bollywood / similar
    "Tum Hi Ho",
    "Kesariya",
    "Raabta",
    "Agar Tum Saath Ho",
    
    # Anime / J-pop
    "Gurenge",
    "Silhouette",
    "Again",
    "Blue Bird",
    
    # Rock / Metal
    "Bohemian Rhapsody",
    "Smells Like Teen Spirit",
    "Enter Sandman",
    "Numb",
    
    # EDM / Electronic
    "Animals",
    "Titanium",
    "Closer",
    "Wake Me Up",
    
    # Chill / Acoustic
    "Let Her Go",
    "Perfect",
    "All of Me",
    "Photograph",
    
    # Random global mix
    "Despacito",
    "Shape of You",
    "Believer",
    "Someone You Loved"
]

for song in test_songs:
    songs, distances = get_song_suggestion(song)
    print(f"\n\n---- {song} -----")
    print(songs)
    print(distances)