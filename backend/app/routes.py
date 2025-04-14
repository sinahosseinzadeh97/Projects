from flask import Blueprint, jsonify, request
from ..models.predictor import LoanPredictor

main = Blueprint('main', __name__)
predictor = LoanPredictor()

@main.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        prediction = predictor.predict(data)
        return jsonify({
            'status': 'success',
            'prediction': prediction
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@main.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'API is running'
    }) 