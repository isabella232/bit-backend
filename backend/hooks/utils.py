from backend import repo
from backend.config import API
from backend.general_utils import create_image_obj
from backend.models import Activity, Card, Hint, Module, Topic, Track
from backend.tracks.utils import create_tracks_dict
import ast
import os
import requests


# Function to call the Card's Create/Update route
def call_card_routes(card_data, folder_path):
    cards = get_github_urls(folder_path)

    for card_name, raw_data in card_data.items():
        card_data[card_name]["github_raw_data"] = cards[card_name]["raw_url"]
        card_data[card_name]["gems"] = int(card_data[card_name]["gems"])
        card_data[card_name]["order"] = int(card_data[card_name]["order"])
        card_data[card_name]["filename"] = cards[card_name]["filename"]
        name_length = len(card_name) - 2

        if name_length < 0:
            card = Card.query.filter_by(github_raw_data=cards[card_name]["raw_url"]).first()

            if card:
                requests.put(API + "/cards", json=card_data[card_name])
            else:
                requests.post(API + "/cards", json=card_data[card_name])
        else:
            call_hint_routes(name_length, cards, card_name, card_data)

    return


# Function to call the Hint Create/Update route
def call_hint_routes(name_length, cards, card_name, card_data):
    hint = Hint.query.filter_by(github_raw_data=cards[card_name]["raw_url"]).first()
    parent_name = card_name[:name_length]
    card_data[card_name]["parent"] = cards[parent_name]["raw_url"]

    if name_length == 1:
        card_data[card_name]["is_card_hint"] = True
    else:
        card_data[card_name]["is_card_hint"] = False

    if hint:
        requests.put(API + "/hints", json=card_data[card_name])
    else:
        requests.post(API + "/hints", json=card_data[card_name])

    return


# Function to call the Topic's Create/Update route
def call_topic_routes(topic_data):
    for key, data in topic_data.items():
        topic = Topic.query.filter_by(github_id=data["github_id"]).first()

        if topic:
            requests.put(API + "/topics", json=data)
        else:
            requests.post(API + "/topics", json=data)

    return


# Function to call the Track's Create/Update route
def call_track_routes(track_data, tracks):
    for key, data in track_data.items():
        track = Track.query.filter_by(github_id=data["github_id"]).first()

        if track:
            requests.put(API + "/tracks", json=data)
            track = Track.query.filter_by(github_id=data["github_id"]).first()
            tracks.pop(track.github_id)
        else:
            requests.post(API + "/tracks", json=data)

    return tracks


# Function to call a topic's delete route
def delete_topic_route():
    topics = Topic.query.all()

    # Deletes Topics if they are not associated with a track
    for topic in topics:
        if not topic.tracks:
            data = {
                "github_id": topic.github_id
            }
            requests.delete(API + "/topics", json=data)

    return


# Function to call the track's delete route
def delete_track_route(tracks):
    # Deletes Tracks
    for track in tracks.values():
        requests.delete(API + "/tracks", json=track)

    return


# Function to edit the tests.json file
def edit_test_json(files):
    topic_data = {}
    test_file = files["tests.json"].raw_url
    response = requests.get(test_file)
    data = response.text
    track_data = ast.literal_eval(data)

    for key, val in track_data.items():
        for topic in val["topics"]:
            topic_data[topic["name"]] = topic

    parse_tracks(track_data, topic_data)

    return


# Function to get files from all the commits
def get_files(commits):
    files = {}
    removed_files = []

    for commit in commits:
        change = repo.get_commit(sha=commit["id"])
        removed_files += commit["removed"]

        for file in change.files:
            files[file.filename] = file

    return files, removed_files


# Function to get the raw url of each card
def get_github_urls(folder_path):
    contents = repo.get_contents(path=folder_path)
    cards = {}

    for content in contents:
        if "README.md" not in content.path and "images" not in content.path:
            card_name = content.path.split("/")[2]
            card_name = card_name.split(".")[0]
            cards[card_name] = {
                "raw_url": content.download_url,
                "filename": content.path
            }

    return cards


# Function to parse a markdown file to JSON data
def md_to_json(raw_url):
    response = requests.get(raw_url)
    data = response.text
    f = open("parse.md", "a")
    f.write(data)
    f.close()

    cmd = "md_to_json parse.md"
    output = os.popen(cmd).read()
    result = ast.literal_eval(output)
    os.remove("parse.md")

    return result


# Function to take data from a README.md to Create/Update a module
def parse_activity(file):
    raw_url = file.raw_url
    data = md_to_json(raw_url)
    data["image"] = create_image_obj(data["image"], data["image_folder"], "activities")
    activity = Activity.query.filter_by(github_id=data["github_id"]).first()
    call_card_routes(data["cards"], data["folder_path"])

    if activity:
        requests.put(API + "/activities", json=data)
    else:
        requests.post(API + "/activities", json=data)

    return


# Function to take data from a README.md to Create/Update a module
def parse_module(file):
    raw_url = file.raw_url
    data = md_to_json(raw_url)
    data = update_module_data(data)
    module = Module.query.filter_by(github_id=data["github_id"]).first()

    if module:
        requests.put(API + "/modules", json=data)
    else:
        requests.post(API + "/modules", json=data)

    return


# Function to take the data from tests.json and update it
def parse_tracks(track_data, topic_data):
    tracks = create_tracks_dict()
    call_topic_routes(topic_data)
    tracks = call_track_routes(track_data, tracks)
    delete_topic_route()
    delete_track_route(tracks)

    return


# Function to type cast module fields and update image field
def update_module_data(data):
    data["image"] = create_image_obj(data["image"], data["image_folder"], "modules")

    if "github_id" in data:
        data["github_id"] = int(data["github_id"])

    if "gems_needed" in data:
        data["gems_needed"] = int(data["gems_needed"])

    return data
