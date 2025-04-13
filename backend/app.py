from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DEFAULT_API_KEY = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Test endpoint
@app.route('/test', methods=['GET'])
def test_route():
    return jsonify({"status": "API is working!"})

# Helper function to classify query (not a route)
def classify_query_helper(query, api_key=None):
    if not query:
        return {"error": "No query provided"}, 400
    
    # Use provided API key or fall back to default
    openai.api_key = api_key

    try:
        response = openai.chat.completions.create(
            model="ft:gpt-4o-mini-2024-07-18:personal:router:B9Yzb1mV",
            messages=[
                {"role": "system", "content": "You are an AI trained to classify queries into categories and difficulty levels."},
                {"role": "user", "content": query}
            ]
        )

        classification_result = response.choices[0].message.content.strip()
        print(f"Raw classification result: {classification_result}")
        
        # Parse the pipe-separated format: "Category: Maths | Difficulty Level: Low"
        parts = classification_result.split('|')
        
        # Extract category from first part
        category_part = parts[0].strip() if len(parts) > 0 else ""
        category_match = re.search(r"(?i)category\s*:\s*([a-zA-Z0-9 ]+)", category_part)
        category = category_match.group(1).strip() if category_match else "unknown"
        
        # Extract difficulty from second part
        difficulty_part = parts[1].strip() if len(parts) > 1 else ""
        difficulty_match = re.search(r"(?i)difficulty\s*level\s*:\s*([a-zA-Z0-9 ]+)", difficulty_part)
        difficulty = difficulty_match.group(1).strip().lower() if difficulty_match else "unknown"
        
        # Map "Low" to "easy", "Medium" to "medium", "High" to "hard"
        difficulty_mapping = {
            "low": "easy",
            "medium": "medium",
            "high": "hard"
        }
        
        difficulty = difficulty_mapping.get(difficulty.lower(), "unknown")
        
        print(f"Parsed category: {category}, difficulty: {difficulty}")
        
        return {"category": category, "difficulty": difficulty}
    
    except Exception as e:
        print(f"Error in classification: {str(e)}")
        return {"error": str(e)}, 500

# # Classify query endpoint
# @app.route('/classify', methods=['POST'])
# def classify_query():
#     try:
#         data = request.json
#         query = data.get("query", "")
#         api_key = data.get("api_key", None)
        
#         result = classify_query_helper(query, api_key)
        
#         if isinstance(result, tuple):
#             return jsonify(result[0]), result[1]
            
#         return jsonify(result)
    
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# Function to get recommended model based on difficulty
def get_recommended_model(difficulty):
    models = {
        "easy": "gpt-3.5-turbo",
        "medium": "gpt-4o-mini",
        "hard": "o3-mini"
    }
    return models.get(difficulty.lower(), "unknown")

# Router endpoint
@app.route('/api/router', methods=['POST'])
def router():
    try:
        data = request.json
        question = data.get('question', '')
        api_key = data.get('api_key', None)
        
        if not question:
            return jsonify({"error": "No question provided"}), 400
        
        # Use the helper function
        result = classify_query_helper(question, api_key)
        
        if isinstance(result, tuple):
            return jsonify(result[0]), result[1]
        
        classify_data = result
        difficulty = classify_data.get("difficulty", "unknown")
        category = classify_data.get("category", "unknown")
        recommended_model = get_recommended_model(difficulty)
        
        return jsonify({
            "category": category,
            "difficulty": difficulty,
            "recommended_model": recommended_model
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Answer endpoint
@app.route('/api/answer', methods=['POST'])
def get_answer():
    try:
        data = request.json
        question = data.get('question', '')
        model = data.get('model', 'gpt-3.5-turbo')
        api_key = data.get('api_key', None)
        print(f"Attempting to use model: {model}")
        
        if not question:
            return jsonify({"error": "No question provided"}), 400
        
        # Create OpenAI client with the appropriate API key
        client = openai.OpenAI(api_key=api_key or DEFAULT_API_KEY)
        
        # Define messages for the API call
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question}
        ]
        
        # Create arguments dictionary based on the model
        args = {
            "model": model,
            "messages": messages
        }
        
        # Add temperature parameter only for models that support it
        if model != "o3-mini":
            args["temperature"] = 0.7
        
        response = client.chat.completions.create(**args)
        
        answer = response.choices[0].message.content
        
        return jsonify({"answer": answer})
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Server starting on http://localhost:5000...")
    app.run(debug=True, port=5000)