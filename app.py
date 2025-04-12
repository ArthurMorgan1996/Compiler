from flask import Flask, request, jsonify
import subprocess
import tempfile
import os

app = Flask(__name__)

@app.route('/run', methods=['POST'])
def run_code():
    data = request.get_json()
    code = data.get('code')

    # Temporary file for code
    with tempfile.NamedTemporaryFile(delete=False, suffix='.py') as temp:
        temp.write(code.encode('utf-8'))
        temp.flush()
        temp.close()

        try:
            result = subprocess.run(
                ['python', temp.name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10
            )
            output = result.stdout.decode('utf-8') + result.stderr.decode('utf-8')
        except subprocess.TimeoutExpired:
            output = "Error: Code execution timed out."
        finally:
            os.unlink(temp.name)

    return jsonify({'output': output})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
