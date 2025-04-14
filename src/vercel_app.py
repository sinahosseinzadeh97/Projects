from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({
        "status": "success",
        "message": "Loan Prediction System API",
        "version": "1.0.0"
    })

@app.route('/test')
def test():
    return jsonify({
        "status": "success",
        "message": "API is working"
    })

if __name__ == '__main__':
    app.run() 