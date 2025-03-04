from flask import Blueprint, request, jsonify 
import numpy as np
import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import pickle
import fasttext
from sklearn.decomposition import LatentDirichletAllocation
from bs4 import BeautifulSoup
preprocess_bp=Blueprint('preprocess',__name__)
# Load the trained model
with open(r"C:\Users\kunal\ProjectMinor\SVCModelnew.pkl", 'rb') as file:
    model = pickle.load(file)
with open(r"C:\Users\kunal\ProjectMinor\scalernew.pkl", 'rb') as file:
    scaler = pickle.load(file)

import re

def clean_text(text):
    # 1️⃣ Remove HTML tags (like <div>, <p>, etc.)
    text = BeautifulSoup(text, "html.parser").get_text()
    # 2️⃣ Remove URLs (http, https, www)
    text = re.sub(r'http[s]?://\S+', '', text)  # Removes links starting with http/https
    text = re.sub(r'www\.\S+', '', text)        # Removes links starting with www
    # 3️⃣ Remove usernames (@username)
    text = re.sub(r'@\w+', '', text)  # Removes @mentions
    # 4️⃣ Remove special characters (optional)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # 5️⃣ Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text.lower()  # Convert to lowercase for uniformity


# Function to load stopwords from a file
def load_stopwords(file_path):
    """Reads stopwords from a TXT file and returns a set."""
    with open(file_path, "r", encoding="utf-8") as f:
        stopwords = set(line.strip().lower() for line in f if line.strip())  # Lowercased stopwords
    return stopwords

# Hinglish Stemming Function
def hinglish_stem(word):
    """Applies stemming for English words while removing common Hinglish suffixes."""
    hindi_suffixes = ['na', 'ta', 'ti', 'te', 'ega', 'egi', 'enge', 'ka', 'ki', 'ke', 'log', 'wala', 'wali', 'wale', 'kar', 'se', 'mein', 'on']
    porter = PorterStemmer()

    # Remove common Hinglish suffixes
    for suffix in hindi_suffixes:
        if word.endswith(suffix):
            return word[:-len(suffix)]

    return porter.stem(word).strip()  # Apply Porter Stemmer for English words
stopwords = load_stopwords(r"C:\Users\kunal\ProjectMinor\stop_hinglish_union.txt")
# Main Text Processing Function (Optimized)
def removestopwords(cleaned_text):
    """Removes stopwords (preloaded set) and applies English stemming."""
    words = cleaned_text.split()  # Tokenize (No need to reprocess text)
    stemmed_words = [word for word in words if word not in stopwords]
    
    return ' '.join(stemmed_words)  # Join words with a single space

# Function to compute sentence embeddings
def get_average_embedding(sentence, model):
    words = sentence.split()
    word_vectors = [model.get_word_vector(word) for word in words if word.strip()]
    if not word_vectors:
        return np.zeros(model.get_dimension())  # Return zero vector for empty sentences
    return np.mean(word_vectors, axis=0)

def get_top_words(model, feature_names, n_top_words=10):
    topics_list = []  # List to store topics

    for topic_idx, topic in enumerate(model.components_):
        top_words = [feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]]
        topics_list.append(top_words)  # Store words as a list

    return topics_list  # Return the list of topics

model_en = fasttext.load_model(r"C:\Users\kunal\ProjectMinor\cc.en.300.bin")


import requests

@preprocess_bp.route('/preprocess/test',methods=['GET'])
def test():
    return "I am working"

@preprocess_bp.route('/preprocess',methods=['POST'])
def process():
    comments = request.json.get("comments", []) 
    
    cleanComments = [clean_text(text) for text in comments]
    nostopwordComments = [removestopwords(sentence) for sentence in cleanComments]
    stemmedComments = [" ".join([hinglish_stem(word) for word in sentence.split()]) for sentence in nostopwordComments]
    summary_data=requests.post('http://127.0.0.1:5000/api/summarize',json={"comments": cleanComments})

    if summary_data.status_code == 200:
        summarize_response = summary_data.json()
        summarize = summarize_response.get('summarize', "Summary not available")
        print(summarize) 
    else:
        summarize = "Unable to generate summary"

    # Assuming X is a list of sentences
    sentence_embeddings = [get_average_embedding(sentence, model_en) for sentence in stemmedComments]
    # Convert to a NumPy array with proper shape
    X_data_df = pd.DataFrame(sentence_embeddings)
    X_scale = scaler.transform(X_data_df)
    predictions=model.predict(X_scale)
    # Total number of predictions
    total = len(predictions)

    # Count positive (1) and negative (0) predictions
    positive_count = np.sum(predictions)  # Since 1s represent positive
    negative_count = total - positive_count

    # Calculate percentages
    positive_percentage = (positive_count / total) * 100
    negative_percentage = (negative_count / total) * 100
    tfidf_vectorizer = TfidfVectorizer(max_features=3000)  # Adjust features as needed
    X_tfidf = tfidf_vectorizer.fit_transform(nostopwordComments)
    num_topics =5
    lda = LatentDirichletAllocation(n_components=num_topics, random_state=42)
    X_topics = lda.fit_transform(X_tfidf)
    topic_distribution = np.mean(X_topics, axis=0)

    # Convert to percentage
    topic_percentage = np.round(topic_distribution * 100,2)
    LDA_result=get_top_words(lda, tfidf_vectorizer.get_feature_names_out())
    

    return jsonify({
    'positive': positive_percentage,
    'negative': negative_percentage,
    'lda_result': LDA_result,
    'topic_dist': topic_percentage.tolist(),  # Convert ndarray to list
    'summarize':summarize})


