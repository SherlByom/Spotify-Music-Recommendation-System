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

def get_song(song_name_input, k = 5):
    index = get_song_index(song_name_input)

    if (index == None):
        return None, None

    distances, indices = model_kn.kneighbors([embeddings[index]], n_neighbors = k + 1)

    return df.iloc[indices[0]][["TRACK_NAME", "TRACK_GENRE"]], distances

x, y = get_song("Kun faya kun")
print(x)
print(y)