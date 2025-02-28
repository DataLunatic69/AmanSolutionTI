from flask import Flask, request, jsonify, render_template
import logging
from logger import setup_logging
from routers import ModelRouter

# Initialize logging
setup_logging()

# Create Flask app
app = Flask(__name__)

# Initialize the model router
model_router = ModelRouter()

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({'error': 'No prompt provided'}), 400

        response, provider_info = model_router.invoke(data['prompt'])

        # Format the response with activity logs
        return jsonify({
            'response': response,
            'provider': provider_info['name'],
            'model': provider_info['model'],
            'activity_log': provider_info['activity_log']
        })

    except Exception as e:
        logging.error(f"Error generating response: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)