import requests

API_URL = "https://api-inference.huggingface.co/models/ai-forever/T5-large-spell"
HEADERS = {"Authorization": "Bearer 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"}  # Replace with your Hugging Face API key

def correct_spelling_2d(matrix):
    corrected_matrix = []
    
    for row in matrix:

        sentence = " ".join(row)  # Convert row to a sentence
        payload = {
            "inputs": f"{sentence}",
            "parameters": {
                "max_length": 100,
                "do_sample": False,  # Ensure deterministic output
                "repetition_penalty": 1.5  # Reduce word repetition
            }
        }
        
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        
        if response.status_code == 200:
            corrected_text = response.json()[0]["generated_text"]
            corrected_words = list(dict.fromkeys(corrected_text.split()))  # Remove duplicates
            corrected_matrix.append(corrected_words)
        else:
            corrected_matrix.append(row)  # Keep original row if API fails
    
    return corrected_matrix
# Example input (2D list of words)
input_matrix = [
    ["helo", "wrld"],
    ["ths", "is", "a", "tst","someting"]
]

corrected_output = correct_spelling_2d(input_matrix)
print(corrected_output)