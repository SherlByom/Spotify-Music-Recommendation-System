import joblib
import pandas as pd
import rapidfuzz as rf
import Packages.autoencoder
from flask_cors import CORS
from collections import defaultdict
from flask import Flask, request, jsonify
from youtubesearchpython import VideosSearch

app = Flask(__name__)
CORS(app)

model = joblib.load("Models/autoencoder.pkl")
model_kn = joblib.load("Models/knn.pkl")
scaler = joblib.load("Models/scaler.pkl")
embeddings = joblib.load("Models/embeddings.pkl")
df = pd.read_csv("Models/cleaned_dataset.csv")

# Prebuilt dictionary for song lookup
name_to_index = defaultdict(list)
for idx, name in enumerate(df["TRACK_NAME"]):
    name_to_index[name.upper()].append(idx)

#Song Suggestion
df["TRACK_NAME_UPPER"] = df["TRACK_NAME"].str.upper()

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

# Optimized Song Index Finding
def get_song_index(song_name):
    result = name_to_index.get(song_name.upper())
    if not result:
        return None
    return result[0]

def index_to_suggestion(index, k):
    if index >= len(df) or index < 0:
        return None, None

    distances, indices = model_kn.kneighbors([embeddings[index]], n_neighbors = k + 1)
    return df.iloc[index], df.iloc[indices[0][1:]]

def get_song_suggestion(song_name_input, k = 8):
    index = get_song_index(song_name_input)
    fuzzy_threshold = 75
    
    if index is None:
        song_tuples = rf.process.extract(song_name_input.upper(), df["TRACK_NAME_UPPER"], scorer = rf.fuzz.token_sort_ratio, limit = 10)
        for song_tuple in song_tuples:
            index = song_tuple[2] if (len(song_tuple[0]) > len(song_name_input) * 0.6) and (song_tuple[1] > fuzzy_threshold) else None
            if index is not None:
                break
            
    if index is None:
        return None, None

    return index_to_suggestion(index, k)
    
def get_dropdown_names(query = ""):
    if query == "":
        return []
    
    fuzzy_threshold = 75
    tuple_list = []

    song_tuples = rf.process.extract(query.upper(), df["TRACK_NAME_UPPER"], scorer = rf.fuzz.token_sort_ratio, limit = 10)
    for song_tuple in song_tuples:
        if (len(song_tuple[0]) > len(query) * 0.6) and (song_tuple[1] > fuzzy_threshold):
            tuple_list.append(song_tuple)

    if len(tuple_list) == 0:
        return None
    
    return tuple_list

@app.route("/suggestname", methods = ["GET"])
def suggestion_name_api():
    song_name = request.args.get("song")
    k = request.args.get("k", default = 8, type = int)

    print(f"Request received for name = \"{song_name}\", k = \'{k}\'")

    if not song_name:
        return jsonify({ "error": "Song is needed" }), 400

    try:
        song, suggestions = get_song_suggestion(song_name, k)
    except Exception as e:
        print(f"Error in Suggestion")

    if song is None:
        return jsonify({ "error": "Unable to find songs" }), 404
    
    song = song.to_dict()
    suggestions = suggestions.to_dict(orient = "records")
    
    for suggested_song in suggestions:
        try:
            suggested_song["THUMBNAIL"], suggested_song["VIDEO_LINK"] = get_song_video(
                suggested_song["TRACK_NAME"], 
                suggested_song["ARTISTS"]
            )
        except Exception as e:
            print(f"Error fetching video: {e}")
            suggested_song["THUMBNAIL"] = None
            suggested_song["VIDEO_LINK"] = None

    return jsonify({
        "song": song,
        "suggestions": suggestions
    }), 200

@app.route("/suggestindex", methods = ["GET"])
def suggestion_index_api():
    index = request.args.get("i", type = int)
    k = request.args.get("k", default = 8, type = int)

    print(f"Request received for index = \"{index}\", k = \'{k}\'")

    if index < 0:
        return jsonify({ "error": "Valid index needed" }), 400

    try:
        song, suggestions = index_to_suggestion(index, k)
    except Exception as e:
        print(f"Error in Suggestion")

    if song is None:
        return jsonify({ "error": "Unable to find songs" }), 404
    
    song = song.to_dict()
    suggestions = suggestions.to_dict(orient = "records")
    
    for suggested_song in suggestions:
        try:
            suggested_song["THUMBNAIL"], suggested_song["VIDEO_LINK"] = get_song_video(
                suggested_song["TRACK_NAME"], 
                suggested_song["ARTISTS"]
            )
        except Exception as e:
            print(f"Error fetching video: {e}")
            suggested_song["THUMBNAIL"] = None
            suggested_song["VIDEO_LINK"] = None

    return jsonify({
        "song": song,
        "suggestions": suggestions
    }), 200

@app.route("/dropdownquery", methods = ["GET"])
def dropdown_api():
    query = request.args.get("q")
    print(f"Dropdown suggestion for {query}")
    tuples = get_dropdown_names(query)

    return jsonify({ "songs": tuples })

# Only for testing, will be removed when deploying
app.run(host = "0.0.0.0", port = 5000)