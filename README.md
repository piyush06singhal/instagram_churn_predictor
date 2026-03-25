# 📊 AI-Powered Instagram Performance & Churn Prediction Platform

A complete end-to-end machine learning platform that helps Instagram creators predict follower churn, analyze engagement trends, and receive AI-powered recommendations to improve their performance.

## 🎯 Features

- **Churn Prediction**: ML-powered prediction of follower loss risk
- **Trend Analysis**: Visualize engagement metrics over time
- **Competitor Comparison**: Compare your performance with industry averages
- **AI Recommendations**: Get personalized, actionable suggestions
- **User Authentication**: Secure signup and login system
- **Data Upload**: Support for CSV file uploads
- **Interactive Dashboard**: Beautiful visualizations with Plotly
- **REST API**: Complete backend API for all operations

## 🏗️ Architecture

```
├── app.py                      # Streamlit frontend application
├── backend/
│   └── api.py                  # Flask REST API server
├── model/
│   ├── train.py                # ML model training pipeline
│   ├── predict.py              # Prediction module
│   ├── best_model.pkl          # Trained model (generated)
│   ├── scaler.pkl              # Feature scaler (generated)
│   └── feature_importance.csv  # Feature rankings (generated)
├── data/
│   ├── generate_dataset.py     # Dataset generation script
│   └── instagram_data.csv      # Training data (generated)
├── database/
│   ├── db_manager.py           # Database operations
│   └── instagram_churn.db      # SQLite database (generated)
├── utils/
│   └── recommendations.py      # Recommendation engine
└── requirements.txt            # Python dependencies
```

## 📊 Dataset Features

The platform uses the following features for prediction:

- `followers_count`: Total number of followers
- `likes`: Number of likes on posts
- `comments`: Number of comments
- `shares`: Number of shares
- `saves`: Number of saves
- `reach`: Post reach
- `impressions`: Post impressions
- `engagement_rate`: Calculated as (likes + comments + shares + saves) / followers
- `posting_gap_days`: Days between posts
- `follower_change`: Net follower gain/loss
- `competitor_avg_engagement`: Average engagement rate of competitors
- `post_type`: Type of content (reel/image/story)

**Target Variable**: `churn_label` (1 = churn risk, 0 = no churn)

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone or download the project**

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Generate dataset**

```bash
python data/generate_dataset.py
```

4. **Train the ML models**

```bash
python model/train.py
```

This will:

- Train Logistic Regression, Random Forest, and XGBoost models
- Evaluate and compare all models
- Select the best model based on F1 score
- Save the model and preprocessing objects

5. **Run the Streamlit application**

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### Optional: Run the Flask API (for external integrations)

```bash
python backend/api.py
```

API will be available at `http://localhost:5000`

## 📱 Using the Platform

### 1. Sign Up / Login

- Create a new account or login with existing credentials
- Your data is securely stored with hashed passwords

### 2. Predict Churn

- Navigate to "Predict Churn" page
- Enter your Instagram engagement metrics
- Get instant churn prediction with risk category
- View personalized recommendations

### 3. Upload Data

- Upload CSV files with historical engagement data
- Bulk import multiple records at once
- Track your performance over time

### 4. Analyze Trends

- View engagement rate trends
- Analyze follower change patterns
- Compare performance by post type
- Identify best-performing content

### 5. Get Recommendations

- Receive AI-powered suggestions
- Prioritized action items
- Content strategy advice
- Posting frequency optimization

## 🤖 Machine Learning Models

The platform trains and evaluates three models:

1. **Logistic Regression**: Fast, interpretable baseline
2. **Random Forest**: Ensemble method with feature importance
3. **XGBoost**: Gradient boosting for high accuracy

### Model Evaluation Metrics

- Accuracy
- Precision
- Recall
- F1 Score
- ROC-AUC

The best model is automatically selected based on F1 score.

## 🔌 API Endpoints

### Authentication

- `POST /api/signup` - Create new user account
- `POST /api/login` - Authenticate user

### Predictions

- `POST /api/predict` - Get churn prediction
- `GET /api/feature-importance` - Get feature importance rankings

### Data Management

- `POST /api/upload` - Upload CSV data
- `GET /api/trends/<user_id>` - Get engagement trends
- `GET /api/recommendations/<user_id>` - Get personalized recommendations

### Health Check

- `GET /api/health` - Check API status

## 📊 Sample API Request

```python
import requests

# Predict churn
data = {
    "followers_count": 50000,
    "likes": 2000,
    "comments": 150,
    "shares": 50,
    "saves": 300,
    "reach": 25000,
    "impressions": 40000,
    "posting_gap_days": 3,
    "follower_change": 500,
    "competitor_avg_engagement": 0.08,
    "post_type": "reel"
}

response = requests.post("http://localhost:5000/api/predict", json=data)
result = response.json()

print(f"Churn Probability: {result['prediction']['churn_probability']:.2%}")
print(f"Risk Category: {result['prediction']['risk_category']}")
```

## 🎨 Dashboard Features

### Overview Dashboard

- Key metrics at a glance
- Latest churn prediction with gauge chart
- Engagement rate trends
- Quick access to all features

### Prediction Page

- Interactive form for data entry
- Real-time prediction
- Visual risk indicator
- Top recommendations

### Trends Analysis

- Line charts for engagement over time
- Bar charts for follower changes
- Post type performance comparison
- Statistical summaries

### Recommendations

- Prioritized suggestions (High/Medium/Low)
- Actionable items for each recommendation
- Feature importance visualization
- Context-aware advice

## 🔒 Security Features

- Password hashing using SHA-256
- Session management
- SQL injection prevention
- Input validation
- Error handling without exposing internals

## 📈 Extending the Platform

### Add New Features

1. Edit `data/generate_dataset.py` to include new columns
2. Update `model/train.py` to include features in training
3. Modify `model/predict.py` to handle new features
4. Update frontend forms in `app.py`

### Add New Models

1. Import model in `model/train.py`
2. Add to `models_config` dictionary
3. Train and evaluate automatically

### Customize Recommendations

1. Edit `utils/recommendations.py`
2. Add new recommendation rules
3. Customize priority levels and action items

## 🐛 Troubleshooting

### Model not found error

```bash
# Ensure you've trained the model first
python model/train.py
```

### Database error

```bash
# Delete and reinitialize database
rm database/instagram_churn.db
python -c "from database.db_manager import DatabaseManager; DatabaseManager()"
```

### Import errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

## 📝 Project Structure Details

### Frontend (Streamlit)

- Clean, intuitive UI
- Responsive design
- Interactive visualizations
- Real-time updates

### Backend (Flask)

- RESTful API design
- CORS enabled
- Error handling
- JSON responses

### Machine Learning

- Scikit-learn pipeline
- Feature engineering
- Model comparison
- Automated selection

### Database (SQLite)

- User management
- Engagement history
- Prediction storage
- Query optimization

## 🎓 Educational Value

This project demonstrates:

- End-to-end ML pipeline development
- Full-stack application architecture
- Database design and management
- API development and integration
- Data visualization best practices
- Production-ready code structure

## 📄 License

This project is created for educational purposes.

## 👥 Contributing

This is a final-year engineering project template. Feel free to:

- Add new features
- Improve the UI/UX
- Optimize model performance
- Add more visualizations
- Implement additional ML algorithms

## 🙏 Acknowledgments

- Scikit-learn for ML algorithms
- Streamlit for the amazing frontend framework
- Flask for the lightweight backend
- Plotly for interactive visualizations
- XGBoost for gradient boosting implementation

---

**Built with ❤️ for Instagram Creators**

For questions or issues, please refer to the code comments or create an issue in the repository.
