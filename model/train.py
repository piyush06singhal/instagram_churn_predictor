import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import joblib
import json

class ChurnModelTrainer:
    def __init__(self, data_path='data/instagram_data.csv'):
        self.data_path = data_path
        self.models = {}
        self.best_model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_names = None
        
    def load_and_preprocess_data(self):
        """Load and preprocess the dataset"""
        print("Loading data...")
        df = pd.read_csv(self.data_path)
        
        # Handle missing values
        df = df.fillna(df.median(numeric_only=True))
        
        # Encode categorical variables
        df['post_type_encoded'] = self.label_encoder.fit_transform(df['post_type'])
        
        # Select features
        feature_cols = ['followers_count', 'likes', 'comments', 'shares', 'saves', 
                       'reach', 'impressions', 'engagement_rate', 'posting_gap_days',
                       'follower_change', 'competitor_avg_engagement', 'post_type_encoded']
        
        X = df[feature_cols]
        y = df['churn_label']
        
        self.feature_names = feature_cols
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        print(f"Training samples: {len(X_train)}, Test samples: {len(X_test)}")
        print(f"Churn rate in training: {y_train.mean():.2%}")
        
        return X_train_scaled, X_test_scaled, y_train, y_test
    
    def train_models(self, X_train, X_test, y_train, y_test):
        """Train multiple models and evaluate"""
        print("\n" + "="*50)
        print("Training Models...")
        print("="*50)
        
        # Define models
        models_config = {
            'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
            'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10),
            'XGBoost': XGBClassifier(n_estimators=100, random_state=42, max_depth=6, learning_rate=0.1)
        }
        
        results = {}
        
        for name, model in models_config.items():
            print(f"\nTraining {name}...")
            model.fit(X_train, y_train)
            
            # Predictions
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1]
            
            # Metrics
            metrics = {
                'accuracy': accuracy_score(y_test, y_pred),
                'precision': precision_score(y_test, y_pred),
                'recall': recall_score(y_test, y_pred),
                'f1_score': f1_score(y_test, y_pred),
                'roc_auc': roc_auc_score(y_test, y_pred_proba)
            }
            
            results[name] = metrics
            self.models[name] = model
            
            print(f"{name} Results:")
            for metric, value in metrics.items():
                print(f"  {metric}: {value:.4f}")
        
        return results
    
    def select_best_model(self, results):
        """Select best model based on F1 score"""
        best_model_name = max(results, key=lambda x: results[x]['f1_score'])
        self.best_model = self.models[best_model_name]
        
        print(f"\n{'='*50}")
        print(f"Best Model: {best_model_name}")
        print(f"F1 Score: {results[best_model_name]['f1_score']:.4f}")
        print(f"{'='*50}")
        
        return best_model_name, self.best_model
    
    def get_feature_importance(self, model_name):
        """Get feature importance from the best model"""
        model = self.models[model_name]
        
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
        elif hasattr(model, 'coef_'):
            importances = np.abs(model.coef_[0])
        else:
            return None
        
        feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importances
        }).sort_values('importance', ascending=False)
        
        return feature_importance
    
    def save_model(self, model_name):
        """Save the best model and preprocessing objects"""
        print("\nSaving model and preprocessing objects...")
        
        joblib.dump(self.best_model, 'model/best_model.pkl')
        joblib.dump(self.scaler, 'model/scaler.pkl')
        joblib.dump(self.label_encoder, 'model/label_encoder.pkl')
        
        # Save feature names
        with open('model/feature_names.json', 'w') as f:
            json.dump(self.feature_names, f)
        
        # Save feature importance
        feature_importance = self.get_feature_importance(model_name)
        if feature_importance is not None:
            feature_importance.to_csv('model/feature_importance.csv', index=False)
        
        print("Model saved successfully!")
    
    def run_training_pipeline(self):
        """Run the complete training pipeline"""
        # Load and preprocess
        X_train, X_test, y_train, y_test = self.load_and_preprocess_data()
        
        # Train models
        results = self.train_models(X_train, X_test, y_train, y_test)
        
        # Select best model
        best_model_name, _ = self.select_best_model(results)
        
        # Save model
        self.save_model(best_model_name)
        
        # Display feature importance
        feature_importance = self.get_feature_importance(best_model_name)
        if feature_importance is not None:
            print("\nTop 5 Most Important Features:")
            print(feature_importance.head())
        
        return results

if __name__ == "__main__":
    trainer = ChurnModelTrainer()
    results = trainer.run_training_pipeline()
