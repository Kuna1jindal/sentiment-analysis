from flask import Flask, request, jsonify
from flask_cors import CORS
from googleapiclient.discovery import build
import os
import requests
from blueprints.preprocess import preprocess_bp 
from blueprints.summarize import summarize_bp
from dotenv import load_dotenv  # Import dotenv
# Load environment variables from .env file
load_dotenv()
# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests
app.register_blueprint(preprocess_bp, url_prefix='/api')  
app.register_blueprint(summarize_bp, url_prefix='/api')  

# Load YouTube Data API Key securely from environment variables
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Function to fetch comments from YouTube video
def fetch_youtube_comments(video_id):
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    
    comments = []
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=50  # Adjust as needed
    )
    
    response = request.execute()
    for item in response.get("items", []):
        comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        comments.append(comment)
    return comments

# Function to analyze sentiment
def analyze_sentiment(comments):
    url = 'http://127.0.0.1:5000/api/preprocess'
    response = requests.post(url, json={"comments": comments})  # Corrected JSON structure
    return response.json()  # Ensure this contains valid JSON

# API Route to Analyze YouTube Comments
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    url = data.get("url")
    
    if "youtube.com/watch?v=" not in url:
        return jsonify({"error": "Invalid YouTube URL"}), 400

    # Extract video ID from URL
    video_id = url.split("v=")[1].split("&")[0]

    try:
        comments = fetch_youtube_comments(video_id)
        if not comments:
            return jsonify({"error": "No comments found"}), 404
        print(comments[:5])
        sentiment_results = analyze_sentiment(comments)
        print(sentiment_results)
        return jsonify(sentiment_results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
