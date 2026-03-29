import joblib
import pandas as pd
import torch.nn as nn
from flask import Flask, request, jsonify
from Models.autoencoder import AutoEncoder

app = Flask(__name__)

model = joblib.load("Models/autoencoder.pkl")
model_kn = joblib.load("Models/knn.pkl")
scaler = joblib.load("Models/scaler.pkl")
embeddings = joblib.load("Models/embeddings.pkl")
df = pd.read_csv("Models/cleaned_dataset.csv")

def get_song_index(song_name):
    result = df[df["TRACK_NAME"].str.upper() == song_name.upper()]
    return result

print(get_song_index("Comedy"))