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