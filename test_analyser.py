"""
Test script for the Financial & SaaS Sentiment Analyser
Run this to test individual components
"""

from sentiment_analyzer import NewsSentimentAnalyser
from datetime import datetime
import json

def test_sentiment_analysis():
    """Test the sentiment analysis functionality"""
    print("\n" + "="*60)
    print("Testing Sentiment Analysis")
    print("="*60)
    
    analyser = NewsSentimentAnalyser()
    
    # Test sentences
    test_texts = [
        ("Apple reports record-breaking quarterly earnings, exceeding all analyst expectations", "Positive"),
        ("Microsoft faces major security breach, millions of users affected", "Negative"),
        ("Google announces normal quarterly results in line with expectations", "Neutral"),
        ("SaaS company Salesforce sees massive growth in enterprise adoption", "Positive"),
        ("Tech stocks plummet as recession fears grow", "Negative")
    ]
    
    for text, expected in test_texts:
        sentiment = analyser.analyse_sentiment(text)
        print(f"\nText: {text[:50]}...")
        print(f"Expected: {expected}")
        print(f"Score: {sentiment['overall']:.3f}")
        print(f"Label: {analyser._get_sentiment_label(sentiment['overall'])}")
        print("-" * 40)

def test_single_entity():
    """Test analysis for a single entity"""
    print("\n" + "="*60)
    print("Testing Single Entity Analysis")
    print("="*60)
    
    analyser = NewsSentimentAnalyser()
    
    # Test with Apple
    print("\nAnalysing AAPL (Apple)...")
    result = analyser.analyse_entity('AAPL', 'stock')
    
    print(f"\nResults for {result['entity']}:")
    print(f"- Articles found: {len(result['sentiments'])}")
    print(f"- Average sentiment: {result['avg_sentiment']:.3f}")
    print(f"- Sentiment label: {result['sentiment_label']}")
    
    if result['sentiments']:
        print("\nTop 3 articles:")
        for i, sentiment in enumerate(result['sentiments'][:3]):
            article = sentiment['article']
            print(f"\n{i+1}. {article['title']}")
            print(f"   Source: {article['source']}")
            print(f"   Sentiment: {sentiment['overall']:.3f}")

def test_quick_analysis():
    """Run a quick analysis on fewer entities"""
    print("\n" + "="*60)
    print("Running Quick Analysis (3 stocks, 2 SaaS)")
    print("="*60)
    
    analyser = NewsSentimentAnalyser()
    
    # Override with fewer entities for testing
    analyser.tracked_entities['stocks'] = ['AAPL', 'MSFT', 'HSBA.L']
    analyser.tracked_entities['saas'] = ['CRM', 'SNOW']
    
    # Create mini dashboard
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_path = f"test_dashboard_{timestamp}.png"
    
    try:
        analyser.create_dashboard(save_path)
        print(f"\n✓ Test dashboard created: {save_path}")
    except Exception as e:
        print(f"\n❌ Error creating dashboard: {e}")

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("Financial & SaaS Sentiment Analyser - Test Suite")
    print("="*60)
    
    # Choose which test to run
    print("\nSelect test to run:")
    print("1. Test sentiment analysis")
    print("2. Test single entity analysis")
    print("3. Quick analysis (mini dashboard)")
    print("4. Run all tests")
    
    choice = input("\nEnter choice (1-4): ")
    
    if choice == '1':
        test_sentiment_analysis()
    elif choice == '2':
        test_single_entity()
    elif choice == '3':
        test_quick_analysis()
    elif choice == '4':
        test_sentiment_analysis()
        test_single_entity()
        test_quick_analysis()
    else:
        print("Invalid choice. Please run again.")

if __name__ == "__main__":
    main()