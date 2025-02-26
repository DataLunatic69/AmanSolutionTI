from flask import Flask, request, jsonify
from workflow import ModelSwitcher
import yaml
import os

# Load configuration file
with open("providers.yaml", "r") as file:
    config = yaml.safe_load(file)

app = Flask(__name__)
model_switcher = ModelSwitcher()

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Welcome to the Multi-LLM API! Use /generate to interact."})

@app.route("/generate", methods=["POST"])
def generate():
    """Handles text generation requests."""
    data = request.get_json()
    
    if not data or "prompt" not in data:
        return jsonify({"error": "Missing 'prompt' in request"}), 400
    
    response = model_switcher.invoke(data["prompt"])
    return jsonify(response)

@app.route("/logs", methods=["GET"])
def get_logs():
    """Return stored logs of previous requests."""
    logs_path = "logs/request_logs.json"
    if not os.path.exists(logs_path):
        return jsonify({"logs": []})

    with open(logs_path, "r") as log_file:
        logs = log_file.read()
    
    return jsonify({"logs": logs})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
