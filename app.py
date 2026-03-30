from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Fibonacci API
@app.route('/api/fibonacci')
def fibonacci():
    n = int(request.args.get('n'))
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return jsonify({"result": a})

# Tonelli (simple placeholder)
@app.route('/api/verify', methods=['POST'])
def verify():
    data = request.json
    n = data.get('n')
    p = data.get('p')
    return jsonify({
        "message": "Verification logic here",
        "n": n,
        "p": p
    })

if __name__ == '__main__':
    app.run(debug=True)