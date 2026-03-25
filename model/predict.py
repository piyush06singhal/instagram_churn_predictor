import pandas as pd
import numpy as np
import joblib
import json

class ChurnPredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.feature_names = None
        self.load_model()
    
    def load_model(self):
        """Load trained model and preprocessing objects"""
        try:
            self.model = joblib.load('model/best_model.pkl')
            self.scaler = joblib.load('model/scaler.pkl')
            self.label_encoder = joblib.load('model/label_encoder.pkl')
            
            with open('model/feature_names.json', 'r') as f:
                self.feature_names = json.load(f)
            
            print("Model loaded successfully!")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise
    
    def preprocess_input(self, data):
        """Preprocess input data for prediction"""
        df = pd.DataFrame([data]) if isinstance(data, dict) else pd.DataFrame(data)
        
        # Calculate engagement rate if not provided
        if 'engagement_rate' not in df.columns:
            df['engagement_rate'] = (df['likes'] + df['comments'] + df['shares'] + df['saves']) / df['followers_count']
        
        # Encode post_type
        if 'post_type' in df.columns:
            df['post_type_encoded'] = self.label_encoder.transform(df['post_type'])
        
        # Select and order features
        X = df[self.feature_names]
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        return X_scaled
    
    def predict(self, data):
        """Make churn prediction"""
        X = self.preprocess_input(data)
        
        # Get prediction and probability
        prediction = self.model.predict(X)[0]
        probability = self.model.predict_proba(X)[0]
        
        churn_probability = probability[1]
        
        # Determine risk category
        if churn_probability < 0.33:
            risk_category = "Low"
        elif churn_probability < 0.67:
            risk_category = "Medium"
        else:
            risk_category = "High"
        
        return {
            'churn_prediction': int(prediction),
            'churn_probability': float(churn_probability),
            'no_churn_probability': float(probability[0]),
            'risk_category': risk_category
        }
    
    def get_feature_importance(self):
        """Get feature importance"""
        try:
            importance_df = pd.read_csv('model/feature_importance.csv')
            return importance_df.to_dict('records')
        except:
            return None

if __name__ == "__main__":
    # Test prediction
    predictor = ChurnPredictor()
    
    sample_data = {
        'followers_count': 50000,
        'likes': 2000,
        'comments': 150,
        'shares': 50,
        'saves': 300,
        'reach': 25000,
        'impressions': 40000,
        'posting_gap_days': 3,
        'follower_change': 500,
        'competitor_avg_engagement': 0.08,
        'post_type': 'reel'
    }
    
    result = predictor.predict(sample_data)
    print("\nPrediction Result:")
    print(f"Churn Probability: {result['churn_probability']:.2%}")
    print(f"Risk Category: {result['risk_category']}")
