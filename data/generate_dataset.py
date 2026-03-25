import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

def generate_instagram_dataset(n_samples=1000):
    """Generate synthetic Instagram engagement dataset"""
    
    data = {
        'user_id': range(1, n_samples + 1),
        'followers_count': np.random.randint(1000, 100000, n_samples),
        'likes': np.random.randint(50, 5000, n_samples),
        'comments': np.random.randint(5, 500, n_samples),
        'shares': np.random.randint(2, 200, n_samples),
        'saves': np.random.randint(10, 800, n_samples),
        'reach': np.random.randint(500, 50000, n_samples),
        'impressions': np.random.randint(1000, 80000, n_samples),
        'posting_gap_days': np.random.randint(1, 30, n_samples),
        'follower_change': np.random.randint(-500, 1000, n_samples),
        'competitor_avg_engagement': np.random.uniform(0.02, 0.15, n_samples),
        'post_type': np.random.choice(['reel', 'image', 'story'], n_samples)
    }
    
    df = pd.DataFrame(data)
    
    # Calculate engagement rate
    df['engagement_rate'] = (df['likes'] + df['comments'] + df['shares'] + df['saves']) / df['followers_count']
    
    # Generate churn label based on logic
    df['churn_label'] = 0
    
    # High churn risk conditions
    df.loc[(df['engagement_rate'] < 0.02) | 
           (df['follower_change'] < -100) | 
           (df['posting_gap_days'] > 15), 'churn_label'] = 1
    
    # Medium risk with some randomness
    medium_risk = (df['engagement_rate'] < 0.05) & (df['posting_gap_days'] > 7)
    df.loc[medium_risk & (np.random.rand(n_samples) > 0.5), 'churn_label'] = 1
    
    return df

if __name__ == "__main__":
    # Generate dataset
    df = generate_instagram_dataset(1000)
    
    # Save to CSV
    df.to_csv('data/instagram_data.csv', index=False)
    print(f"Dataset generated with {len(df)} samples")
    print(f"Churn distribution:\n{df['churn_label'].value_counts()}")
    print(f"\nFirst few rows:\n{df.head()}")
