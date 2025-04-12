from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import tempfile
import os
import uuid
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Rate limiting dictionary
rate_limits = {}

@app.route('/')
def home():
    return "Python Compiler API is running!"

@app.route('/run', methods=['POST'])
def run_code():
    # Basic rate limiting
    client_ip = request.remote_addr
    current_time = time.time()
    
    if client_ip in rate_limits:
        last_request_time = rate_limits[client_ip]
        if current_time - last_request_time < 1:  # 1 second cooldown
            return jsonify({'output': 'Error: Too many requests. Please wait a moment before trying again.'}), 429
    
    rate_limits[client_ip] = current_time
    
    # Get code from request
    data = request.get_json()
    if not data or 'code' not in data:
        return jsonify({'output': 'Error: No code provided'}), 400
    
    code = data.get('code')
    
    # Generate a unique filename to prevent collisions
    unique_id = str(uuid.uuid4())
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=f'_{unique_id}.py') as temp:
        temp.write(code.encode('utf-8'))
        temp.flush()
        temp_name = temp.name
        
    try:
        # Run the code with resource limits
        result = subprocess.run(
            ['python', temp_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,  # 5 second timeout
            env=dict(os.environ, PYTHONIOENCODING='utf-8')
        )
        
        # Combine stdout and stderr
        output = result.stdout.decode('utf-8')
        error = result.stderr.decode('utf-8')
        
        if error:
            output = f"Error:\n{error}\n\nOutput (if any):\n{output}"
            
    except subprocess.TimeoutExpired:
        output = "Error: Code execution timed out (5 second limit)."
    except Exception as e:
        output = f"Error: {str(e)}"
    finally:
        # Clean up the temporary file
        try:
            os.unlink(temp_name)
        except:
            pass
            
    return jsonify({'output': output})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
