import pandas as pd

class RecommendationEngine:
    def __init__(self):
        self.recommendations = []
    
    def generate_recommendations(self, data, prediction_result):
        """Generate personalized recommendations based on data and prediction"""
        self.recommendations = []
        
        churn_prob = prediction_result['churn_probability']
        risk_category = prediction_result['risk_category']
        
        # Calculate engagement rate
        engagement_rate = data.get('engagement_rate', 0)
        competitor_avg = data.get('competitor_avg_engagement', 0.05)
        posting_gap = data.get('posting_gap_days', 0)
        follower_change = data.get('follower_change', 0)
        post_type = data.get('post_type', 'image')
        
        # High priority recommendations for high risk
        if risk_category == "High":
            self.recommendations.append({
                'priority': 'High',
                'category': 'Urgent Action Required',
                'recommendation': '⚠️ Your account is at HIGH risk of losing followers. Immediate action needed!',
                'action_items': [
                    'Review your content strategy immediately',
                    'Increase posting frequency',
                    'Engage more with your audience'
                ]
            })
        
        # Posting frequency recommendations
        if posting_gap > 7:
            self.recommendations.append({
                'priority': 'High',
                'category': 'Posting Frequency',
                'recommendation': f'You are posting every {posting_gap} days on average. This is too infrequent.',
                'action_items': [
                    'Aim to post at least 3-4 times per week',
                    'Create a content calendar',
                    'Batch create content to maintain consistency'
                ]
            })
        elif posting_gap > 3:
            self.recommendations.append({
                'priority': 'Medium',
                'category': 'Posting Frequency',
                'recommendation': f'Your posting frequency ({posting_gap} days) could be improved.',
                'action_items': [
                    'Try posting daily or every other day',
                    'Test different posting times'
                ]
            })
        
        # Engagement rate recommendations
        if engagement_rate < competitor_avg * 0.7:
            gap_percentage = ((competitor_avg - engagement_rate) / competitor_avg) * 100
            self.recommendations.append({
                'priority': 'High',
                'category': 'Engagement Rate',
                'recommendation': f'Your engagement rate ({engagement_rate:.2%}) is {gap_percentage:.1f}% below competitor average ({competitor_avg:.2%}).',
                'action_items': [
                    'Create more interactive content (polls, questions, quizzes)',
                    'Respond to comments within the first hour',
                    'Use trending audio and hashtags',
                    'Post when your audience is most active'
                ]
            })
        
        # Follower change recommendations
        if follower_change < 0:
            self.recommendations.append({
                'priority': 'High',
                'category': 'Follower Growth',
                'recommendation': f'You lost {abs(follower_change)} followers recently.',
                'action_items': [
                    'Analyze what content caused unfollows',
                    'Return to content that performed well',
                    'Avoid controversial or off-brand content',
                    'Engage with your community more'
                ]
            })
        elif follower_change < 100:
            self.recommendations.append({
                'priority': 'Medium',
                'category': 'Follower Growth',
                'recommendation': 'Your follower growth is slow. Let\'s accelerate it!',
                'action_items': [
                    'Collaborate with other creators',
                    'Use Instagram Reels to reach new audiences',
                    'Cross-promote on other platforms',
                    'Run a giveaway or contest'
                ]
            })
        
        # Content type recommendations
        if post_type == 'image':
            self.recommendations.append({
                'priority': 'Medium',
                'category': 'Content Strategy',
                'recommendation': 'Consider diversifying your content types.',
                'action_items': [
                    'Instagram Reels get 3x more reach than static posts',
                    'Try creating short-form video content',
                    'Mix Reels, Carousels, and Stories',
                    'Test different formats to see what resonates'
                ]
            })
        
        # Best practices
        if engagement_rate > 0:
            self.recommendations.append({
                'priority': 'Low',
                'category': 'Best Practices',
                'recommendation': 'General tips to maintain and improve performance.',
                'action_items': [
                    'Post during peak hours (typically 9-11 AM and 7-9 PM)',
                    'Use 5-10 relevant hashtags per post',
                    'Write compelling captions with clear CTAs',
                    'Analyze Instagram Insights weekly',
                    'Engage with your audience daily (respond to DMs and comments)'
                ]
            })
        
        # Positive reinforcement
        if risk_category == "Low":
            self.recommendations.append({
                'priority': 'Low',
                'category': 'Keep It Up!',
                'recommendation': '✅ Great job! Your account is performing well.',
                'action_items': [
                    'Continue your current strategy',
                    'Document what\'s working',
                    'Gradually experiment with new content types',
                    'Stay consistent with your posting schedule'
                ]
            })
        
        return self.recommendations
    
    def get_top_recommendations(self, n=5):
        """Get top N recommendations"""
        # Sort by priority
        priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
        sorted_recs = sorted(
            self.recommendations,
            key=lambda x: priority_order.get(x['priority'], 3)
        )
        return sorted_recs[:n]

if __name__ == "__main__":
    # Test recommendations
    engine = RecommendationEngine()
    
    sample_data = {
        'followers_count': 50000,
        'likes': 500,
        'comments': 20,
        'shares': 5,
        'saves': 30,
        'engagement_rate': 0.011,
        'posting_gap_days': 10,
        'follower_change': -50,
        'competitor_avg_engagement': 0.08,
        'post_type': 'image'
    }
    
    sample_prediction = {
        'churn_probability': 0.75,
        'risk_category': 'High'
    }
    
    recommendations = engine.generate_recommendations(sample_data, sample_prediction)
    
    print("Generated Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. [{rec['priority']}] {rec['category']}")
        print(f"   {rec['recommendation']}")
