from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/run', methods=['POST'])
def run():
    code = request.json['code']
    with open("temp.py", "w") as f:
        f.write(code)
    result = subprocess.run(["python3", "temp.py"], capture_output=True, text=True)
    return jsonify({"output": result.stdout})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
