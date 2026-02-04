from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import requests
import simi

app = Flask(__name__)
CORS(app)  #this lets the thing to talk to other apis and stuff

DATA_PATH = "problems.json"
INDEX = None

def load_stuff():
    global INDEX
    try:
        f = open(DATA_PATH, "r", encoding="utf-8") #utf 8 is the way the file will be interpreted in
        data = json.load(f) #loads the file as a json
        f.close()
        
        INDEX = simi.build_index(data)  #the whole logic for the indexing for the problems
        print("data loaded good")
    except:
        print("shi didnt work")

@app.route("/recommend", methods=["POST"])
def get_recs():
    global INDEX
    if INDEX == None:
        return jsonify({"error": "server not ready (no data)"}), 503 #this is when  the site isnt ready 

    req = request.json #the data we get from the site
    if req == None:
        req = {}

    my_tags = req.get("tags") #the tags we get from the site
    if my_tags == None:
        my_tags = []
        
    recent = req.get("recent") #the recent problems we get from the site
    if recent == None:
        recent = []

    q = ""
    for t in my_tags:
        q = q + t + " "
    
    for r in recent:
        q = q + r + " "
    
    #this is string we make from the stuff we got from the site (leetcode logic goes crazy ngl)
    print("query is: " + q) 

    feats = simi.extract_query_features(INDEX["items"], q)#this
    res = simi.score(INDEX, feats, top=50)#what simi will generate

    final_ans = []
    
    for x in res:
        itm = x["item"]
        
        slug = itm.get("titleSlug")
        if slug == None:
            slug = itm["title"].lower().replace(" ", "-")
            
        obj = {
            "title": itm["title"],
            "titleSlug": slug,
            "difficulty": itm["difficulty"],
            "topics": itm["tags"],
            "score": x["score"],
            "reason": "Matches your interest in " + str(feats["tags"][:2])
        } #format for the front end
        final_ans.append(obj)

    return jsonify({"recommendations": final_ans})#jsonify makes the responce list into a json file

@app.route("/profile", methods=["POST"])
def profile_func():
    try:
        u = request.json.get("username")
        
        q = 'query getUserProfile($username: String!) { matchedUser(username: $username) { submitStats { acSubmissionNum { difficulty count } } } }'
        
        v = {"username": u}
        
        r = requests.post("https://leetcode.com/graphql", json={"query": q, "variables": v}, headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}, timeout=5)
        
        resp_json = r.json()
        
        if "data" in resp_json:
            d = resp_json["data"]
            if d["matchedUser"]:
                stats = d["matchedUser"]["submitStats"]["acSubmissionNum"]
                return jsonify(stats)
                
        return jsonify({"error": "User not found"}), 404
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/friend", methods=["POST"])
def friend_stuff():
    u = request.json.get("username")
    
    q = """
    query getUserRecent($username: String!) {
        matchedUser(username: $username) {
            submitStats {
                acSubmissionNum {
                    difficulty
                    count
                }
            }
        }
        recentSubmissionList(username: $username, limit: 10) {
            title
            timestamp
        }
    }
    """
    
    try:
        r = requests.post("https://leetcode.com/graphql", json={"query": q, "variables": {"username": u}}, headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}, timeout=5)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    load_stuff()
    print("starting server on 5000")
    app.run(port=5000, debug=True)
