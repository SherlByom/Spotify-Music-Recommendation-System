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

model_kn.fit(embeddings)

def get_song_suggestion(song_name_input, k = 5):
    song_tuple = rf.process.extract(song_name_input, df["TRACK_NAME"])[0]
    index = song_tuple[2] if song_tuple[1] > 65.0 else None

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