from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import tempfile
import os
import uuid

app = Flask(__name__)
# Configure CORS more explicitly
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"]}})

@app.route('/')
def home():
    return "Python Compiler API is running!"

@app.route('/run', methods=['POST', 'OPTIONS'])
def run_code():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 200
        
    # Get code from request
    data = request.get_json()
    if not data or 'code' not in data:
        return jsonify({'output': 'Error: No code provided'}), 400
    
    code = data.get('code')
    
    # Create temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.py') as temp:
        temp.write(code.encode('utf-8'))
        temp_name = temp.name
        
    try:
        # Run the code
        result = subprocess.run(
            ['python', temp_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        
        output = result.stdout.decode('utf-8')
        error = result.stderr.decode('utf-8')
        
        if error:
            output = f"Error:\n{error}\n\nOutput (if any):\n{output}"
            
    except Exception as e:
        output = f"Error: {str(e)}"
    finally:
        # Clean up
        try:
            os.unlink(temp_name)
        except:
            pass
            
    return jsonify({'output': output})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
