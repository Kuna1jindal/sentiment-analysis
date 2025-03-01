import random
from transformers import pipeline, AutoTokenizer
from flask import Blueprint, request, jsonify

# Load pre-trained summarization model and its tokenizer
model_name = "facebook/bart-large-cnn"
summarizer = pipeline("summarization", model=model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Create a Blueprint for summarization
summarize_bp = Blueprint('summarize', __name__)

@summarize_bp.route('/summarize/test', methods=['GET'])
def test():
    return 'I am running...'

def select_random_comments(comments, max_tokens=900, min_tokens=3):
    """Randomly select comments until we reach the max token limit (using tokenizer count)."""
    selected_comments = []
    current_tokens = 0
    
    random.shuffle(comments)  # Shuffle the comments randomly

    for comment in comments:
        tokens = len(tokenizer.tokenize(comment))  # More accurate token count
        if tokens < min_tokens:
            continue
        if current_tokens + tokens > max_tokens:  # Stop when exceeding limit
            break
        selected_comments.append(comment)
        current_tokens += tokens
    
    return " ".join(selected_comments)  # Return selected comments as a single string

@summarize_bp.route('/summarize', methods=['POST'])
def summarize_comments():
    comments = request.json.get("comments", [])

    if not comments or not isinstance(comments, list):
        return jsonify({"error": "Invalid input. 'comments' should be a non-empty list."}), 400
    
    summaries = []
    for _ in range(3):  # Create 3 different summaries
        selected_text = select_random_comments(comments)  # Pick random comments within token limit
        try:
            summary_output = summarizer(selected_text, max_length=250, min_length=15, do_sample=False)
            summaries.append(summary_output[0]['summary_text'])
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    return jsonify({
        "summarize":summaries
    })
