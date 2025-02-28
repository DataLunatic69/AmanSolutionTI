from flask import Flask, request, jsonify
from routers import ModelRouter
from logger import log_usage, log_error
import time

app = Flask(__name__)
model_router = ModelRouter()

@app.route('/generate', methods=['POST'])
def generate():
    try:
        prompt = request.json.get('prompt')
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        start_time = time.time()
        response = model_router.invoke(prompt)
        end_time = time.time()
        
        tokens_used = len(response.split())  
        time_taken = end_time - start_time

        log_usage(model_router.providers[0].name, tokens_used, success=True, time_taken=time_taken)
        return jsonify({"response": response, "tokens_used": tokens_used})
    except Exception as e:
        log_error(str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

