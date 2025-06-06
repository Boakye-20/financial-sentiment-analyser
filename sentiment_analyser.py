#!/usr/bin/env python3
"""
Financial & SaaS News Sentiment Analyser
Tracks sentiment for stocks and SaaS companies
Author: Paul Kwarteng
Date: 07-06-25 2024
"""

import feedparser
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import seaborn as sns
import time
import json
import os
import warnings
warnings.filterwarnings('ignore')

class NewsSentimentAnalyser:
    def __init__(self):
        """Initialise the sentiment analyser with news sources"""
        self.vader = SentimentIntensityAnalyzer()
        
        # Financial news RSS feeds
        self.financial_feeds = {
            'Yahoo Finance': 'https://finance.yahoo.com/rss/',
            'Reuters Business': 'https://feeds.reuters.com/reuters/businessNews',
            'MarketWatch': 'http://feeds.marketwatch.com/marketwatch/topstories',
            'Financial Times': 'https://www.ft.com/?format=rss'
        }
        
        # SaaS/Tech news sources
        self.saas_feeds = {
            'TechCrunch': 'https://techcrunch.com/feed/',
            'The Verge': 'https://www.theverge.com/rss/index.xml',
            'Hacker News': 'https://hnrss.org/frontpage',
            'VentureBeat': 'https://feeds.venturebeat.com/VentureBeat'
        }
        
        # Combined tracking for both sectors - 20 entities total
        self.tracked_entities = {
            # Financial stocks (UK and US) - 10 stocks
            'stocks': [
                # US Tech Giants (4)
                'AAPL',   # Apple
                'MSFT',   # Microsoft
                'GOOGL',  # Alphabet/Google
                'NVDA',   # Nvidia
                
                # US Financial (3)
                'JPM',    # JPMorgan Chase
                'BAC',    # Bank of America
                'GS',     # Goldman Sachs
                
                # UK Stocks (3)
                'HSBA.L', # HSBC
                'BP.L',   # BP
                'AZN.L',  # AstraZeneca
            ],
            
            # Major SaaS companies - 10 companies
            'saas': [
                # Core SaaS (5)
                'CRM',    # Salesforce
                'SNOW',   # Snowflake
                'TEAM',   # Atlassian
                'ZM',     # Zoom
                'DDOG',   # Datadog
                
                # High-Growth Tech (5)
                'SHOP',   # Shopify
                'SQ',     # Block (Square)
                'PLTR',   # Palantir
                'COIN',   # Coinbase
                'SPOT',   # Spotify
            ],
            
            # Keywords for private SaaS
            'saas_keywords': ['SaaS', 'subscription', 'ARR', 'B2B software', 
                            'cloud software', 'enterprise software', 'recurring revenue']
        }
        
        # Colour scheme (British spelling)
        self.colours = {
            'positive': '#2ECC71',
            'negative': '#E74C3C',
            'neutral': '#95A5A6',
            'primary': '#3498DB',
            'secondary': '#9B59B6'
        }
        
        # Store results
        self.results = []
        
    def fetch_news(self, entity, entity_type='stock'):
        """Fetch news for a specific entity"""
        all_news = []
        
        # Choose appropriate feeds
        feeds = self.financial_feeds if entity_type == 'stock' else self.saas_feeds
        
        for source, url in feeds.items():
            try:
                print(f"  Fetching from {source}...")
                feed = feedparser.parse(url)
                
                for entry in feed.entries[:20]:  # Get latest 20 from each
                    # Check if entity is mentioned
                    title = entry.title.lower()
                    summary = entry.get('summary', '').lower()
                    
                    # For stocks, also check company names
                    entity_variants = [entity.lower()]
                    if entity_type == 'stock':
                        # Add company name variants
                        company_names = {
                            'AAPL': ['apple', 'iphone', 'tim cook'],
                            'MSFT': ['microsoft', 'windows', 'satya nadella'],
                            'GOOGL': ['google', 'alphabet', 'android'],
                            'NVDA': ['nvidia', 'jensen huang', 'gpu'],
                            'JPM': ['jpmorgan', 'jp morgan', 'jamie dimon'],
                            'BAC': ['bank of america', 'bofa'],
                            'GS': ['goldman sachs', 'goldman'],
                            'HSBA.L': ['hsbc', 'hongkong shanghai'],
                            'BP.L': ['british petroleum', 'bp'],
                            'AZN.L': ['astrazeneca', 'astra zeneca'],
                            'CRM': ['salesforce', 'marc benioff'],
                            'SNOW': ['snowflake'],
                            'TEAM': ['atlassian', 'jira', 'confluence'],
                            'ZM': ['zoom', 'zoom video'],
                            'DDOG': ['datadog'],
                            'SHOP': ['shopify'],
                            'SQ': ['square', 'block inc', 'jack dorsey'],
                            'PLTR': ['palantir'],
                            'COIN': ['coinbase'],
                            'SPOT': ['spotify']
                        }
                        if entity in company_names:
                            entity_variants.extend(company_names[entity])
                    
                    # Check all variants
                    if any(variant in title or variant in summary for variant in entity_variants):
                        all_news.append({
                            'title': entry.title,
                            'summary': entry.get('summary', ''),
                            'published': entry.get('published_parsed', ''),
                            'source': source,
                            'link': entry.link,
                            'entity': entity
                        })
            except Exception as e:
                print(f"  Error fetching from {source}: {e}")
                
        return all_news
    
    def analyse_sentiment(self, text):
        """Analyse sentiment using both TextBlob and VADER"""
        # Clean text
        text = text.strip()
        if not text:
            return self._neutral_sentiment()
            
        # VADER sentiment
        vader_scores = self.vader.polarity_scores(text)
        
        # TextBlob sentiment
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
        except:
            polarity = 0
            subjectivity = 0
        
        # Combine both approaches with weighted average
        combined_score = {
            'compound': vader_scores['compound'],
            'positive': vader_scores['pos'],
            'negative': vader_scores['neg'],
            'neutral': vader_scores['neu'],
            'polarity': polarity,
            'subjectivity': subjectivity,
            'overall': (vader_scores['compound'] * 0.6 + polarity * 0.4)  # Weight VADER more
        }
        
        return combined_score
    
    def _neutral_sentiment(self):
        """Return neutral sentiment scores"""
        return {
            'compound': 0,
            'positive': 0,
            'negative': 0,
            'neutral': 1,
            'polarity': 0,
            'subjectivity': 0,
            'overall': 0
        }
    
    def fetch_stock_data(self, symbol, days=30):
        """Fetch stock price data"""
        try:
            stock = yf.Ticker(symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            data = stock.history(start=start_date, end=end_date)
            if data.empty:
                return None
            return data
        except Exception as e:
            print(f"  Error fetching stock data for {symbol}: {e}")
            return None
    
    def analyse_entity(self, entity, entity_type='stock'):
        """Complete analysis for one entity"""
        print(f"\nAnalysing {entity_type}: {entity}")
        
        # Fetch news
        news = self.fetch_news(entity, entity_type)
        print(f"  Found {len(news)} news articles")
        
        # Analyse each article
        sentiments = []
        for article in news:
            sentiment = self.analyse_sentiment(
                article['title'] + ' ' + article['summary']
            )
            sentiment['timestamp'] = datetime.now()
            sentiment['article'] = article
            sentiments.append(sentiment)
        
        # Get price data if it's a stock
        price_data = None
        if entity_type == 'stock':
            price_data = self.fetch_stock_data(entity)
        
        # Calculate average sentiment
        avg_sentiment = np.mean([s['overall'] for s in sentiments]) if sentiments else 0
        
        return {
            'entity': entity,
            'type': entity_type,
            'sentiments': sentiments,
            'price_data': price_data,
            'avg_sentiment': avg_sentiment,
            'sentiment_label': self._get_sentiment_label(avg_sentiment)
        }
    
    def _get_sentiment_label(self, score):
        """Convert sentiment score to label"""
        if score >= 0.3:
            return 'Very Positive'
        elif score >= 0.1:
            return 'Positive'
        elif score <= -0.3:
            return 'Very Negative'
        elif score <= -0.1:
            return 'Negative'
        else:
            return 'Neutral'
    
    def create_dashboard(self, save_path=None):
        """Create comprehensive sentiment dashboard"""
        # Analyse all entities
        print("\n" + "="*60)
        print("Starting comprehensive analysis...")
        print("="*60)
        
        # Analyse stocks
        stock_results = []
        for stock in self.tracked_entities['stocks']:
            result = self.analyse_entity(stock, 'stock')
            stock_results.append(result)
            time.sleep(1)  # Be polite to APIs
        
        # Analyse SaaS companies
        saas_results = []
        for saas in self.tracked_entities['saas']:
            result = self.analyse_entity(saas, 'saas')
            saas_results.append(result)
            time.sleep(1)
        
        # Create visualisation
        plt.style.use('seaborn-v0_8-darkgrid')
        fig = plt.figure(figsize=(20, 24))
        gs = gridspec.GridSpec(5, 2, height_ratios=[1, 1, 1, 1, 1.5], 
                              hspace=0.35, wspace=0.3)
        
        # Define colour scheme
        colors = sns.color_palette("coolwarm", 10)
        
        # Panel 1: Overall Market Sentiment
        ax1 = fig.add_subplot(gs[0, :])
        self._plot_market_sentiment(ax1, stock_results + saas_results, colors)
        
        # Panel 2: Stock Sentiment Heatmap
        ax2 = fig.add_subplot(gs[1, 0])
        self._plot_sentiment_heatmap(ax2, stock_results, "Stock Sentiment Scores", colors)
        
        # Panel 3: SaaS Sentiment Heatmap  
        ax3 = fig.add_subplot(gs[1, 1])
        self._plot_sentiment_heatmap(ax3, saas_results, "SaaS Company Sentiment Scores", colors)
        
        # Panel 4: Top Movers - Sentiment
        ax4 = fig.add_subplot(gs[2, 0])
        self._plot_top_movers(ax4, stock_results + saas_results, colors)
        
        # Panel 5: Sentiment vs Price (for top stock)
        ax5 = fig.add_subplot(gs[2, 1])
        best_stock = max(stock_results, key=lambda x: len(x['sentiments'])) if stock_results else None
        if best_stock and best_stock['price_data'] is not None:
            self._plot_sentiment_vs_price(ax5, best_stock, colors)
        
        # Panel 6: News Volume by Source
        ax6 = fig.add_subplot(gs[3, 0])
        self._plot_news_volume(ax6, stock_results + saas_results, colors)
        
        # Panel 7: Sentiment Distribution
        ax7 = fig.add_subplot(gs[3, 1])
        self._plot_sentiment_distribution(ax7, stock_results + saas_results, colors)
        
        # Panel 8: Key Insights Table
        ax8 = fig.add_subplot(gs[4, :])
        self._create_insights_table(ax8, stock_results, saas_results)
        
        # Main title
        fig.suptitle('Financial & SaaS News Sentiment Analysis Dashboard', 
                    fontsize=24, fontweight='bold', y=0.98)
        
        # Add timestamp
        timestamp_text = f'Generated: {datetime.now().strftime("%d %B %Y at %H:%M GMT")}'
        fig.text(0.99, 0.01, timestamp_text, ha='right', fontsize=10, style='italic')
        
        # Save
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
            print(f"\n✓ Dashboard saved to: {save_path}")
        
        plt.show()
        
        # Save data for future use
        self._save_results(stock_results, saas_results)
        
        return stock_results, saas_results
    
    def _plot_market_sentiment(self, ax, results, colors):
        """Plot overall market sentiment gauge"""
        # Calculate averages
        if not results:
            return
            
        avg_sentiment = np.mean([r['avg_sentiment'] for r in results if r['sentiments']])
        
        # Create gauge visualisation
        categories = ['Very Negative', 'Negative', 'Neutral', 'Positive', 'Very Positive']
        values = [0] * 5
        
        # Determine which category
        if avg_sentiment <= -0.3:
            values[0] = 1
        elif avg_sentiment <= -0.1:
            values[1] = 1
        elif avg_sentiment <= 0.1:
            values[2] = 1
        elif avg_sentiment <= 0.3:
            values[3] = 1
        else:
            values[4] = 1
        
        # Create horizontal bar
        y_pos = [0]
        left = 0
        colours = ['#E74C3C', '#EC7063', '#95A5A6', '#82E0AA', '#2ECC71']
        
        for i, (cat, val, colour) in enumerate(zip(categories, values, colours)):
            width = 0.2
            alpha = 1.0 if val > 0 else 0.3
            ax.barh(y_pos, width, left=left, color=colour, alpha=alpha, edgecolor='black')
            ax.text(left + width/2, 0, cat, ha='center', va='center', fontsize=10, 
                   weight='bold' if val > 0 else 'normal')
            left += width
        
        ax.set_xlim(0, 1)
        ax.set_ylim(-0.5, 0.5)
        ax.set_yticks([])
        ax.set_xticks([])
        ax.set_title(f'Overall Market Sentiment (Score: {avg_sentiment:.3f})', 
                    fontweight='bold', fontsize=16)
        
        # Remove spines
        for spine in ax.spines.values():
            spine.set_visible(False)
    
    def _plot_sentiment_heatmap(self, ax, results, title, colors):
        """Create sentiment heatmap"""
        if not results or not any(r['sentiments'] for r in results):
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center')
            ax.set_title(title)
            return
            
        # Filter results with data
        valid_results = [r for r in results if r['sentiments']]
        if not valid_results:
            return
            
        entities = [r['entity'] for r in valid_results]
        sentiments = [r['avg_sentiment'] for r in valid_results]
        
        # Sort by sentiment
        sorted_idx = np.argsort(sentiments)[::-1]
        
        y_pos = np.arange(len(entities))
        bars = ax.barh(y_pos, [sentiments[i] for i in sorted_idx])
        
        # Colour bars based on sentiment
        for bar, sentiment in zip(bars, [sentiments[i] for i in sorted_idx]):
            if sentiment > 0.1:
                bar.set_color(self.colours['positive'])
            elif sentiment < -0.1:
                bar.set_color(self.colours['negative'])
            else:
                bar.set_color(self.colours['neutral'])
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels([entities[i] for i in sorted_idx])
        ax.set_xlabel('Average Sentiment Score')
        ax.set_title(title, fontweight='bold', fontsize=14)
        ax.axvline(0, color='black', linewidth=1, linestyle='--', alpha=0.5)
        ax.set_xlim(-1, 1)
        
        # Add value labels
        for i, (bar, idx) in enumerate(zip(bars, sorted_idx)):
            width = bar.get_width()
            label_x = width + 0.02 if width > 0 else width - 0.02
            ax.text(label_x, bar.get_y() + bar.get_height()/2, 
                   f'{sentiments[idx]:.3f}', ha='left' if width > 0 else 'right', 
                   va='center', fontsize=9)
    
    def _plot_top_movers(self, ax, results, colors):
        """Plot biggest sentiment changes"""
        # Get results with sentiments
        valid_results = [r for r in results if r['sentiments']]
        if not valid_results:
            return
            
        # Sort by absolute sentiment
        sorted_results = sorted(valid_results, key=lambda x: abs(x['avg_sentiment']), reverse=True)[:10]
        
        if not sorted_results:
            return
            
        entities = [r['entity'] for r in sorted_results]
        sentiments = [r['avg_sentiment'] for r in sorted_results]
        
        bars = ax.bar(range(len(entities)), sentiments)
        
        # Colour based on positive/negative
        for bar, sentiment in zip(bars, sentiments):
            if sentiment > 0.1:
                bar.set_color(self.colours['positive'])
            elif sentiment < -0.1:
                bar.set_color(self.colours['negative'])
            else:
                bar.set_color(self.colours['neutral'])
        
        ax.set_xticks(range(len(entities)))
        ax.set_xticklabels(entities, rotation=45, ha='right')
        ax.set_ylabel('Sentiment Score')
        ax.set_title('Top Sentiment Movers', fontweight='bold', fontsize=14)
        ax.axhline(0, color='black', linewidth=1, alpha=0.5)
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_ylim(-1, 1)
    
    def _plot_sentiment_vs_price(self, ax, result, colors):
        """Plot sentiment against price movement"""
        if result['price_data'] is None or len(result['sentiments']) == 0:
            ax.text(0.5, 0.5, 'No price data available', ha='center', va='center')
            return
            
        # Calculate daily returns
        prices = result['price_data']['Close']
        returns = prices.pct_change().fillna(0) * 100  # Convert to percentage
        
        # Plot on two axes
        ax2 = ax.twinx()
        
        # Plot price
        line1 = ax.plot(prices.index, prices.values, label='Price', 
                       color=self.colours['primary'], linewidth=2.5)
        ax.set_ylabel('Price (£ / $)', color=self.colours['primary'], fontsize=12)
        ax.tick_params(axis='y', labelcolor=self.colours['primary'])
        ax.grid(True, alpha=0.3)
        
        # Plot returns as bars
        pos_returns = [r if r > 0 else 0 for r in returns]
        neg_returns = [r if r < 0 else 0 for r in returns]
        
        bars1 = ax2.bar(returns.index, pos_returns, alpha=0.5, 
                        color=self.colours['positive'], label='Positive Returns')
        bars2 = ax2.bar(returns.index, neg_returns, alpha=0.5, 
                        color=self.colours['negative'], label='Negative Returns')
        
        ax2.set_ylabel('Daily Returns (%)', color='black', fontsize=12)
        ax2.axhline(0, color='black', linewidth=0.5, alpha=0.5)
        
        # Add sentiment indicator
        sentiment_colour = (self.colours['positive'] if result['avg_sentiment'] > 0 
                          else self.colours['negative'])
        ax.text(0.02, 0.98, f"Avg Sentiment: {result['avg_sentiment']:.3f}", 
               transform=ax.transAxes, fontsize=11, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor=sentiment_colour, alpha=0.3))
        
        ax.set_title(f"{result['entity']} - Price Movement & Returns", fontweight='bold', fontsize=14)
        ax.tick_params(axis='x', rotation=45)
        
        # Format x-axis dates
        ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d %b'))
    
    def _plot_news_volume(self, ax, results, colors):
        """Plot news volume by source"""
        source_counts = {}
        for result in results:
            for sentiment in result['sentiments']:
                source = sentiment['article']['source']
                source_counts[source] = source_counts.get(source, 0) + 1
        
        if source_counts:
            # Sort by count
            sorted_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)
            sources = [s[0] for s in sorted_sources]
            counts = [s[1] for s in sorted_sources]
            
            # Create pie chart
            colours = plt.cm.Set3(np.linspace(0, 1, len(sources)))
            wedges, texts, autotexts = ax.pie(counts, labels=sources, autopct='%1.1f%%', 
                                              startangle=90, colors=colours)
            
            # Improve text
            for text in texts:
                text.set_fontsize(10)
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(10)
            
            ax.set_title('News Distribution by Source', fontweight='bold', fontsize=14)
    
    def _plot_sentiment_distribution(self, ax, results, colors):
        """Plot sentiment score distribution"""
        all_sentiments = []
        for result in results:
            all_sentiments.extend([s['overall'] for s in result['sentiments']])
        
        if all_sentiments:
            # Create histogram
            n, bins, patches = ax.hist(all_sentiments, bins=30, alpha=0.7, edgecolor='black')
            
            # Colour bins by sentiment
            for i, patch in enumerate(patches):
                bin_center = (bins[i] + bins[i+1]) / 2
                if bin_center > 0.1:
                    patch.set_facecolor(self.colours['positive'])
                elif bin_center < -0.1:
                    patch.set_facecolor(self.colours['negative'])
                else:
                    patch.set_facecolor(self.colours['neutral'])
            
            # Add statistics
            mean_sentiment = np.mean(all_sentiments)
            median_sentiment = np.median(all_sentiments)
            
            ax.axvline(mean_sentiment, color='red', linestyle='--', linewidth=2,
                      label=f'Mean: {mean_sentiment:.3f}')
            ax.axvline(median_sentiment, color='blue', linestyle='--', linewidth=2,
                      label=f'Median: {median_sentiment:.3f}')
            
            ax.set_xlabel('Sentiment Score')
            ax.set_ylabel('Frequency')
            ax.set_title('Sentiment Score Distribution', fontweight='bold', fontsize=14)
            ax.legend()
            ax.grid(True, alpha=0.3, axis='y')
            ax.set_xlim(-1, 1)
    
    def _create_insights_table(self, ax, stock_results, saas_results):
        """Create insights summary table"""
        ax.axis('off')
        
        # Calculate key metrics
        insights = []
        
        # Filter results with data
        valid_stocks = [r for r in stock_results if r['sentiments']]
        valid_saas = [r for r in saas_results if r['sentiments']]
        
        # Most positive stock
        if valid_stocks:
            most_positive_stock = max(valid_stocks, key=lambda x: x['avg_sentiment'])
            insights.append(['Most Positive Stock', 
                           f"{most_positive_stock['entity']} ({most_positive_stock['avg_sentiment']:.3f})"])
        
        # Most negative stock  
        if valid_stocks:
            most_negative_stock = min(valid_stocks, key=lambda x: x['avg_sentiment'])
            insights.append(['Most Negative Stock', 
                           f"{most_negative_stock['entity']} ({most_negative_stock['avg_sentiment']:.3f})"])
        
        # Most positive SaaS
        if valid_saas:
            most_positive_saas = max(valid_saas, key=lambda x: x['avg_sentiment'])
            insights.append(['Most Positive SaaS', 
                           f"{most_positive_saas['entity']} ({most_positive_saas['avg_sentiment']:.3f})"])
        
        # Market comparison
        if valid_stocks and valid_saas:
            stock_avg = np.mean([r['avg_sentiment'] for r in valid_stocks])
            saas_avg = np.mean([r['avg_sentiment'] for r in valid_saas])
            insights.append(['Sector Comparison', 
                           f"Stocks: {stock_avg:.3f} | SaaS: {saas_avg:.3f}"])
        
        # Total articles analysed
        total_articles = sum(len(r['sentiments']) for r in stock_results + saas_results)
        insights.append(['Total Articles Analysed', str(total_articles)])
        
        # News coverage
        most_covered = max(stock_results + saas_results, key=lambda x: len(x['sentiments']))
        insights.append(['Most News Coverage', 
                        f"{most_covered['entity']} ({len(most_covered['sentiments'])} articles)"])
        
        # Create table
        if insights:
            table = ax.table(cellText=insights,
                            colLabels=['Metric', 'Value'],
                            cellLoc='left',
                            loc='center',
                            colWidths=[0.4, 0.6])
            
            table.auto_set_font_size(False)
            table.set_fontsize(12)
            table.scale(1.2, 2)
            
            # Style header
            for i in range(2):
                table[(0, i)].set_facecolor('#34495E')
                table[(0, i)].set_text_props(weight='bold', color='white')
            
            # Alternate row colours
            for i in range(1, len(insights) + 1):
                if i % 2 == 0:
                    for j in range(2):
                        table[(i, j)].set_facecolor('#ECF0F1')
        
        ax.set_title('Key Insights & Metrics Summary', fontweight='bold', fontsize=16, pad=20)
    
    def _save_results(self, stock_results, saas_results):
        """Save results to JSON for future analysis"""
        output = {
            'analysis_date': datetime.now().isoformat(),
            'summary': {
                'total_stocks_analysed': len(stock_results),
                'total_saas_analysed': len(saas_results),
                'total_articles': sum(len(r['sentiments']) for r in stock_results + saas_results)
            },
            'stock_results': [
                {
                    'entity': r['entity'],
                    'avg_sentiment': r['avg_sentiment'],
                    'sentiment_label': r['sentiment_label'],
                    'num_articles': len(r['sentiments']),
                    'sources': list(set(s['article']['source'] for s in r['sentiments']))
                } for r in stock_results
            ],
            'saas_results': [
                {
                    'entity': r['entity'],
                    'avg_sentiment': r['avg_sentiment'],
                    'sentiment_label': r['sentiment_label'],
                    'num_articles': len(r['sentiments']),
                    'sources': list(set(s['article']['source'] for s in r['sentiments']))
                } for r in saas_results
            ]
        }
        
        # Save to file
        filename = f'sentiment_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n✓ Results saved to: {filename}")

def main():
    """Run the sentiment analyser"""
    print("\n" + "="*60)
    print("Financial & SaaS News Sentiment Analyser")
    print("="*60)
    print(f"Analysis Date: {datetime.now().strftime('%d %B %Y')}")
    print("="*60)
    
    # Create analyser instance
    analyser = NewsSentimentAnalyser()
    
    # Generate timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_path = f"sentiment_dashboard_{timestamp}.png"
    
    # Create dashboard
    try:
        stock_results, saas_results = analyser.create_dashboard(save_path)
        
        print("\n" + "="*60)
        print("✓ Analysis complete!")
        print("="*60)
        
        # Print summary
        print("\nQuick Summary:")
        print("-" * 40)
        
        # Best performers
        all_results = [r for r in stock_results + saas_results if r['sentiments']]
        if all_results:
            best = max(all_results, key=lambda x: x['avg_sentiment'])
            worst = min(all_results, key=lambda x: x['avg_sentiment'])
            
            print(f"Most Positive: {best['entity']} ({best['avg_sentiment']:.3f})")
            print(f"Most Negative: {worst['entity']} ({worst['avg_sentiment']:.3f})")
            
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        print("Please check your internet connection and try again.")

if __name__ == "__main__":
    main()