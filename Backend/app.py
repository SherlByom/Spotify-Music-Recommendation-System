import joblib
import pandas as pd
import rapidfuzz as rf
import Packages.autoencoder
from flask import Flask, request, jsonify

app = Flask(__name__)

model = joblib.load("Models/autoencoder.pkl")
model_kn = joblib.load("Models/knn.pkl")
scaler = joblib.load("Models/scaler.pkl")
embeddings = joblib.load("Models/embeddings.pkl")
df = pd.read_csv("Models/cleaned_dataset.csv")

model_kn.fit(embeddings)

def get_song_suggestion(song_name_input, k = 5):
    song_tuple = rf.process.extract(song_name_input, df["TRACK_NAME"])[0]
    index = song_tuple[2] if song_tuple[1] > 65.0 else None

    if (index == None):
        return None, None, None

    distances, indices = model_kn.kneighbors([embeddings[index]], n_neighbors = k + 1)

    return song_tuple[0], df.iloc[indices[0][1:]][["TRACK_NAME", "TRACK_GENRE"]], distances

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
    "My heart will go on"
]

for song in test_songs:
    song_name, suggestions, distances = get_song_suggestion(song)
    print(f"\n\n---- {song_name} -----")
    print(suggestions)
    print(distances)