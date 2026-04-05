import joblib
import pandas as pd
import rapidfuzz as rf
import Packages.autoencoder
from flask_cors import CORS
from flask import Flask, request, jsonify

app = Flask(__name__)
CORS(app)

model = joblib.load("Models/autoencoder.pkl")
model_kn = joblib.load("Models/knn.pkl")
scaler = joblib.load("Models/scaler.pkl")
embeddings = joblib.load("Models/embeddings.pkl")
df = pd.read_csv("Models/cleaned_dataset.csv")

def get_song_index(song_name):
    result = df[df["TRACK_NAME"].str.upper() == song_name.upper()]

    if len(result) == 0:
        return None

    return result.index[0]

def get_song_suggestion(song_name_input, k = 5):
    index = get_song_index(song_name_input)
    fuzzy_threshold = 75
    
    if index == None:
        song_tuples = rf.process.extract(song_name_input.upper(), df["TRACK_NAME"].str.upper(), scorer = rf.fuzz.token_sort_ratio, limit = 10)

        for song_tuple in song_tuples:
            index = song_tuple[2] if (len(song_tuple[0]) > len(song_name_input) * 0.6) and (song_tuple[1] > fuzzy_threshold) else None
            if index:
                break

    if index == None:
        return None, None

    distances, indices = model_kn.kneighbors([embeddings[index]], n_neighbors = k + 1)

    return df.iloc[index], df.iloc[indices[0][1:]]

@app.route("/suggest", methods = ["GET"])
def suggestion_api():
    song_name = request.args.get("song")
    k = request.args.get("k", default = 5, type = int)

    if not song_name:
        return jsonify({ "error": "Song is needed" })

    song, suggestions = get_song_suggestion(song_name, k)

    if song is None:
        return jsonify({ "error": "Unable to find songs" })

    return jsonify({
        "song": song.to_dict(),
        "suggestions": suggestions.to_dict(orient = "records")
    })

# Only for testing, will be removed when deploying
app.run(host = "0.0.0.0", port = 5000)