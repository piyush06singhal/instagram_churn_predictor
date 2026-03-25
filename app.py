import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
import sys
import os

# Add paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from model.predict import ChurnPredictor
from database.db_manager import DatabaseManager
from utils.recommendations import RecommendationEngine

# Page config
st.set_page_config(
    page_title="Instagram Churn Prediction Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize components
@st.cache_resource
def load_predictor():
    return ChurnPredictor()

@st.cache_resource
def load_db():
    return DatabaseManager()

@st.cache_resource
def load_rec_engine():
    return RecommendationEngine()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #E1306C;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .risk-high {
        color: #ff4b4b;
        font-weight: bold;
    }
    .risk-medium {
        color: #ffa500;
        font-weight: bold;
    }
    .risk-low {
        color: #00cc00;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None

def login_page():
    """Login/Signup page"""
    st.markdown('<div class="main-header">📊 Instagram Churn Prediction Platform</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.subheader("Login to Your Account")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", type="primary"):
            if username and password:
                db = load_db()
                result = db.authenticate_user(username, password)
                
                if result['success']:
                    st.session_state.logged_in = True
                    st.session_state.user_id = result['user_id']
                    st.session_state.username = result['username']
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error(result['message'])
            else:
                st.warning("Please enter both username and password")
    
    with tab2:
        st.subheader("Create New Account")
        new_username = st.text_input("Username", key="signup_username")
        new_email = st.text_input("Email", key="signup_email")
        new_password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
        
        if st.button("Sign Up", type="primary"):
            if new_username and new_email and new_password:
                if new_password != confirm_password:
                    st.error("Passwords do not match!")
                else:
                    db = load_db()
                    result = db.create_user(new_username, new_email, new_password)
                    
                    if result['success']:
                        st.success("Account created successfully! Please login.")
                    else:
                        st.error(result['message'])
            else:
                st.warning("Please fill in all fields")

def create_gauge_chart(value, title):
    """Create a gauge chart for churn probability"""
    if value < 0.33:
        color = "green"
    elif value < 0.67:
        color = "orange"
    else:
        color = "red"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value * 100,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 24}},
        number={'suffix': "%"},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 33], 'color': 'lightgreen'},
                {'range': [33, 67], 'color': 'lightyellow'},
                {'range': [67, 100], 'color': 'lightcoral'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(height=300)
    return fig

def dashboard_page():
    """Main dashboard page"""
    st.markdown(f'<div class="main-header">Welcome, {st.session_state.username}! 👋</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.title("Navigation")
        page = st.radio(
            "Go to",
            ["Dashboard", "Predict Churn", "Upload Data", "Trends Analysis", "Recommendations"]
        )
        
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.username = None
            st.rerun()
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Predict Churn":
        show_prediction_page()
    elif page == "Upload Data":
        show_upload_page()
    elif page == "Trends Analysis":
        show_trends_page()
    elif page == "Recommendations":
        show_recommendations_page()

def show_dashboard():
    """Show main dashboard overview"""
    st.header("📊 Dashboard Overview")
    
    db = load_db()
    
    # Get user data
    engagement_df = db.get_user_engagement_history(st.session_state.user_id)
    predictions_df = db.get_user_predictions(st.session_state.user_id)
    
    if engagement_df.empty:
        st.info("👋 Welcome! Start by predicting churn or uploading your engagement data.")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Posts Tracked", len(engagement_df))
    
    with col2:
        avg_engagement = engagement_df['engagement_rate'].mean()
        st.metric("Avg Engagement Rate", f"{avg_engagement:.2%}")
    
    with col3:
        total_followers = engagement_df.iloc[0]['followers_count']
        st.metric("Current Followers", f"{total_followers:,}")
    
    with col4:
        if not predictions_df.empty:
            latest_risk = predictions_df.iloc[0]['risk_category']
            st.metric("Churn Risk", latest_risk)
        else:
            st.metric("Churn Risk", "N/A")
    
    # Latest prediction
    if not predictions_df.empty:
        st.subheader("Latest Churn Prediction")
        latest_pred = predictions_df.iloc[0]
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            fig = create_gauge_chart(latest_pred['churn_probability'], "Churn Risk")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            risk_class = f"risk-{latest_pred['risk_category'].lower()}"
            st.markdown(f"### Risk Category: <span class='{risk_class}'>{latest_pred['risk_category']}</span>", unsafe_allow_html=True)
            st.write(f"**Prediction Date:** {latest_pred['prediction_date']}")
            st.write(f"**Churn Probability:** {latest_pred['churn_probability']:.2%}")
            
            if latest_pred['risk_category'] == 'High':
                st.error("⚠️ High risk of losing followers! Check recommendations for action items.")
            elif latest_pred['risk_category'] == 'Medium':
                st.warning("⚡ Moderate risk. Some improvements needed.")
            else:
                st.success("✅ Low risk. Keep up the good work!")
    
    # Engagement trend
    st.subheader("Engagement Rate Over Time")
    if len(engagement_df) > 1:
        fig = px.line(
            engagement_df,
            x='created_at',
            y='engagement_rate',
            title='Engagement Rate Trend'
        )
        fig.update_layout(xaxis_title="Date", yaxis_title="Engagement Rate")
        st.plotly_chart(fig, use_container_width=True)

def show_prediction_page():
    """Show churn prediction page"""
    st.header("🔮 Predict Churn Risk")
    
    st.write("Enter your Instagram engagement metrics to get a churn prediction:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        followers_count = st.number_input("Followers Count", min_value=0, value=50000, step=1000)
        likes = st.number_input("Likes", min_value=0, value=2000, step=100)
        comments = st.number_input("Comments", min_value=0, value=150, step=10)
        shares = st.number_input("Shares", min_value=0, value=50, step=5)
        saves = st.number_input("Saves", min_value=0, value=300, step=10)
        reach = st.number_input("Reach", min_value=0, value=25000, step=1000)
    
    with col2:
        impressions = st.number_input("Impressions", min_value=0, value=40000, step=1000)
        posting_gap_days = st.number_input("Posting Gap (days)", min_value=1, max_value=30, value=3)
        follower_change = st.number_input("Follower Change", value=500, step=50)
        competitor_avg_engagement = st.number_input("Competitor Avg Engagement", min_value=0.0, max_value=1.0, value=0.08, step=0.01, format="%.3f")
        post_type = st.selectbox("Post Type", ["reel", "image", "story"])
    
    if st.button("Predict Churn Risk", type="primary"):
        data = {
            'user_id': st.session_state.user_id,
            'followers_count': followers_count,
            'likes': likes,
            'comments': comments,
            'shares': shares,
            'saves': saves,
            'reach': reach,
            'impressions': impressions,
            'posting_gap_days': posting_gap_days,
            'follower_change': follower_change,
            'competitor_avg_engagement': competitor_avg_engagement,
            'post_type': post_type
        }
        
        # Calculate engagement rate
        data['engagement_rate'] = (likes + comments + shares + saves) / followers_count
        
        with st.spinner("Analyzing your data..."):
            predictor = load_predictor()
            rec_engine = load_rec_engine()
            db = load_db()
            
            # Make prediction
            result = predictor.predict(data)
            
            # Save to database
            db.save_engagement_data(st.session_state.user_id, data)
            db.save_prediction(
                st.session_state.user_id,
                result['churn_probability'],
                result['risk_category']
            )
            
            # Generate recommendations
            recommendations = rec_engine.generate_recommendations(data, result)
        
        st.success("Prediction complete!")
        
        # Display results
        col1, col2 = st.columns([1, 2])
        
        with col1:
            fig = create_gauge_chart(result['churn_probability'], "Churn Risk")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            risk_class = f"risk-{result['risk_category'].lower()}"
            st.markdown(f"### Risk Category: <span class='{risk_class}'>{result['risk_category']}</span>", unsafe_allow_html=True)
            st.write(f"**Churn Probability:** {result['churn_probability']:.2%}")
            st.write(f"**No Churn Probability:** {result['no_churn_probability']:.2%}")
            st.write(f"**Engagement Rate:** {data['engagement_rate']:.2%}")
        
        # Show top recommendations
        st.subheader("Top Recommendations")
        for i, rec in enumerate(recommendations[:3], 1):
            with st.expander(f"{i}. [{rec['priority']}] {rec['category']}"):
                st.write(rec['recommendation'])
                st.write("**Action Items:**")
                for action in rec['action_items']:
                    st.write(f"- {action}")

def show_upload_page():
    """Show CSV upload page"""
    st.header("📤 Upload Engagement Data")
    
    st.write("Upload a CSV file with your Instagram engagement data.")
    
    st.info("""
    **Required columns:**
    - followers_count
    - likes
    - comments
    - shares
    - saves
    - reach
    - impressions
    - posting_gap_days
    - follower_change
    - competitor_avg_engagement
    - post_type
    """)
    
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.write("Preview of uploaded data:")
            st.dataframe(df.head())
            
            if st.button("Process and Save Data", type="primary"):
                db = load_db()
                saved_count = 0
                
                progress_bar = st.progress(0)
                
                for idx, row in df.iterrows():
                    # Calculate engagement rate if not present
                    if 'engagement_rate' not in row or pd.isna(row['engagement_rate']):
                        row['engagement_rate'] = (row['likes'] + row['comments'] + row['shares'] + row['saves']) / row['followers_count']
                    
                    result = db.save_engagement_data(st.session_state.user_id, row.to_dict())
                    if result['success']:
                        saved_count += 1
                    
                    progress_bar.progress((idx + 1) / len(df))
                
                st.success(f"Successfully saved {saved_count} out of {len(df)} records!")
        
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

def show_trends_page():
    """Show trends analysis page"""
    st.header("📈 Trends Analysis")
    
    db = load_db()
    engagement_df = db.get_user_engagement_history(st.session_state.user_id)
    
    if engagement_df.empty:
        st.info("No data available. Please add engagement data first.")
        return
    
    # Engagement rate over time
    st.subheader("Engagement Rate Over Time")
    fig = px.line(
        engagement_df,
        x='created_at',
        y='engagement_rate',
        title='Engagement Rate Trend',
        markers=True
    )
    fig.update_layout(xaxis_title="Date", yaxis_title="Engagement Rate")
    st.plotly_chart(fig, use_container_width=True)
    
    # Follower change over time
    st.subheader("Follower Change Over Time")
    fig = px.bar(
        engagement_df,
        x='created_at',
        y='follower_change',
        title='Follower Change Trend',
        color='follower_change',
        color_continuous_scale=['red', 'yellow', 'green']
    )
    fig.update_layout(xaxis_title="Date", yaxis_title="Follower Change")
    st.plotly_chart(fig, use_container_width=True)
    
    # Post type performance
    st.subheader("Performance by Post Type")
    post_type_perf = engagement_df.groupby('post_type')['engagement_rate'].mean().reset_index()
    fig = px.bar(
        post_type_perf,
        x='post_type',
        y='engagement_rate',
        title='Average Engagement Rate by Post Type',
        color='engagement_rate',
        color_continuous_scale='viridis'
    )
    fig.update_layout(xaxis_title="Post Type", yaxis_title="Avg Engagement Rate")
    st.plotly_chart(fig, use_container_width=True)
    
    # Statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Average Engagement", f"{engagement_df['engagement_rate'].mean():.2%}")
    
    with col2:
        st.metric("Total Posts", len(engagement_df))
    
    with col3:
        best_post_type = post_type_perf.loc[post_type_perf['engagement_rate'].idxmax(), 'post_type']
        st.metric("Best Post Type", best_post_type)

def show_recommendations_page():
    """Show recommendations page"""
    st.header("💡 AI-Powered Recommendations")
    
    db = load_db()
    engagement_df = db.get_user_engagement_history(st.session_state.user_id)
    predictions_df = db.get_user_predictions(st.session_state.user_id)
    
    if engagement_df.empty:
        st.info("No data available. Please add engagement data first.")
        return
    
    # Get latest data and prediction
    latest_data = engagement_df.iloc[0].to_dict()
    
    if not predictions_df.empty:
        latest_pred = predictions_df.iloc[0]
        prediction_result = {
            'churn_probability': latest_pred['churn_probability'],
            'risk_category': latest_pred['risk_category']
        }
    else:
        predictor = load_predictor()
        prediction_result = predictor.predict(latest_data)
    
    # Generate recommendations
    rec_engine = load_rec_engine()
    recommendations = rec_engine.generate_recommendations(latest_data, prediction_result)
    
    # Display recommendations
    for i, rec in enumerate(recommendations, 1):
        priority_color = {
            'High': '🔴',
            'Medium': '🟡',
            'Low': '🟢'
        }
        
        with st.expander(f"{priority_color[rec['priority']]} {i}. [{rec['priority']}] {rec['category']}", expanded=(i <= 3)):
            st.write(f"**{rec['recommendation']}**")
            st.write("\n**Action Items:**")
            for action in rec['action_items']:
                st.write(f"✓ {action}")
    
    # Feature importance
    st.subheader("📊 Feature Importance")
    st.write("Understanding which factors most influence your churn risk:")
    
    predictor = load_predictor()
    importance = predictor.get_feature_importance()
    
    if importance:
        importance_df = pd.DataFrame(importance)
        fig = px.bar(
            importance_df.head(10),
            x='importance',
            y='feature',
            orientation='h',
            title='Top 10 Most Important Features',
            color='importance',
            color_continuous_scale='viridis'
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

# Main app logic
def main():
    if not st.session_state.logged_in:
        login_page()
    else:
        dashboard_page()

if __name__ == "__main__":
    main()
