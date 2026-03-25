from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.predict import ChurnPredictor
from database.db_manager import DatabaseManager
from utils.recommendations import RecommendationEngine
import pandas as pd

app = Flask(__name__)
CORS(app)

# Initialize components
predictor = ChurnPredictor()
db = DatabaseManager()
rec_engine = RecommendationEngine()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'API is running'})

@app.route('/api/signup', methods=['POST'])
def signup():
    """User signup endpoint"""
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not all([username, email, password]):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    result = db.create_user(username, email, password)
    
    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 400

@app.route('/api/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not all([username, password]):
        return jsonify({'success': False, 'message': 'Missing credentials'}), 400
    
    result = db.authenticate_user(username, password)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 401

@app.route('/api/predict', methods=['POST'])
def predict_churn():
    """Churn prediction endpoint"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['followers_count', 'likes', 'comments', 'shares', 'saves',
                          'reach', 'impressions', 'posting_gap_days', 'follower_change',
                          'competitor_avg_engagement', 'post_type']
        
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'success': False,
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Make prediction
        prediction_result = predictor.predict(data)
        
        # Save to database if user_id provided
        user_id = data.get('user_id')
        if user_id:
            db.save_engagement_data(user_id, data)
            db.save_prediction(
                user_id,
                prediction_result['churn_probability'],
                prediction_result['risk_category']
            )
        
        # Generate recommendations
        recommendations = rec_engine.generate_recommendations(data, prediction_result)
        
        return jsonify({
            'success': True,
            'prediction': prediction_result,
            'recommendations': recommendations
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Prediction error: {str(e)}'
        }), 500

@app.route('/api/upload', methods=['POST'])
def upload_csv():
    """CSV upload endpoint"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        
        file = request.files['file']
        user_id = request.form.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'message': 'User ID required'}), 400
        
        # Read CSV
        df = pd.read_csv(file)
        
        # Validate columns
        required_cols = ['followers_count', 'likes', 'comments', 'shares', 'saves',
                        'reach', 'impressions', 'posting_gap_days', 'follower_change',
                        'competitor_avg_engagement', 'post_type']
        
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            return jsonify({
                'success': False,
                'message': f'Missing columns: {", ".join(missing_cols)}'
            }), 400
        
        # Save each row
        saved_count = 0
        for _, row in df.iterrows():
            result = db.save_engagement_data(user_id, row.to_dict())
            if result['success']:
                saved_count += 1
        
        return jsonify({
            'success': True,
            'message': f'Successfully uploaded {saved_count} records'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Upload error: {str(e)}'
        }), 500

@app.route('/api/trends/<int:user_id>', methods=['GET'])
def get_trends(user_id):
    """Get user engagement trends"""
    try:
        df = db.get_user_engagement_history(user_id)
        
        if df.empty:
            return jsonify({
                'success': False,
                'message': 'No data found for user'
            }), 404
        
        # Calculate trends
        trends = {
            'engagement_over_time': df[['created_at', 'engagement_rate']].to_dict('records'),
            'follower_change_over_time': df[['created_at', 'follower_change']].to_dict('records'),
            'post_type_performance': df.groupby('post_type')['engagement_rate'].mean().to_dict(),
            'average_engagement': float(df['engagement_rate'].mean()),
            'total_posts': len(df)
        }
        
        return jsonify({
            'success': True,
            'trends': trends
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Trends error: {str(e)}'
        }), 500

@app.route('/api/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    """Get recommendations for user"""
    try:
        # Get latest engagement data
        df = db.get_user_engagement_history(user_id)
        
        if df.empty:
            return jsonify({
                'success': False,
                'message': 'No data found for user'
            }), 404
        
        latest_data = df.iloc[0].to_dict()
        
        # Get latest prediction
        pred_df = db.get_user_predictions(user_id)
        if not pred_df.empty:
            latest_pred = pred_df.iloc[0]
            prediction_result = {
                'churn_probability': latest_pred['churn_probability'],
                'risk_category': latest_pred['risk_category']
            }
        else:
            # Make new prediction
            prediction_result = predictor.predict(latest_data)
        
        # Generate recommendations
        recommendations = rec_engine.generate_recommendations(latest_data, prediction_result)
        
        return jsonify({
            'success': True,
            'recommendations': recommendations
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Recommendations error: {str(e)}'
        }), 500

@app.route('/api/feature-importance', methods=['GET'])
def get_feature_importance():
    """Get feature importance from model"""
    try:
        importance = predictor.get_feature_importance()
        
        if importance:
            return jsonify({
                'success': True,
                'feature_importance': importance
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Feature importance not available'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("Starting Flask API server...")
    print("API will be available at http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
