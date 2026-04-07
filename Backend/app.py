import joblib
import pandas as pd
import rapidfuzz as rf
import Packages.autoencoder
from flask_cors import CORS
from flask import Flask, request, jsonify
from youtubesearchpython import VideosSearch
from collections import defaultdict

app = Flask(__name__)
CORS(app)

model = joblib.load("Models/autoencoder.pkl")
model_kn = joblib.load("Models/knn.pkl")
scaler = joblib.load("Models/scaler.pkl")
embeddings = joblib.load("Models/embeddings.pkl")
df = pd.read_csv("Models/cleaned_dataset.csv")

# Prebuilt dictionary for song lookup
# Create mapping: song name → list of indices  
name_to_index = defaultdict(list)
for idx, name in enumerate(df["TRACK_NAME"]):
    name_to_index[name.upper()].append(idx)


#Video Search
def get_song_video(song_name, artists = None):
    try:
        search_query = f"{song_name} {(artists or "").replace(';', ' ')}"
        result = VideosSearch(search_query, limit = 1).result()["result"]
        if not result:
            return None, None
        video = result[0]
        return video["thumbnails"][0]["url"], video["link"]
    except Exception as e:
        print(f"[YouTube Fetch Error]: {e}")
        return None, None
#Video Search Updated With Try-Catch

# Optimized Song Index Finding
def get_song_index(song_name):
    result = name_to_index.get(song_name.upper())
    if not result:
        return None
    return result[0]

#Song Suggestion
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
    k = request.args.get("k", default = 8, type = int)

    print(f"Request received for \"{song_name}\" \'{k}\'")

    if not song_name:
        return jsonify({ "error": "Song is needed" })

    song, suggestions = get_song_suggestion(song_name, k)

    if song is None:
        return jsonify({ "error": "Unable to find songs" })
    
    song = song.to_dict()
    suggestions = suggestions.to_dict(orient = "records")
    
    song["THUMBNAIL"], song["VIDEO_LINK"] = get_song_video(song["TRACK_NAME"], song["ARTISTS"])

    for suggested_song in suggestions:
        suggested_song["THUMBNAIL"], suggested_song["VIDEO_LINK"] = get_song_video(suggested_song["TRACK_NAME"], suggested_song["ARTISTS"])

    return jsonify({
        "song": song,
        "suggestions": suggestions
    })

# Only for testing, will be removed when deploying
app.run(host = "0.0.0.0", port = 5000)