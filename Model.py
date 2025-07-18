import json
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import sys
import os

def load_data(file_path):
    """Load and normalize transaction data from JSON file"""
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    df = pd.json_normalize(data)
    
    df = df.rename(columns={
        'userWallet': 'user',
        'action': 'type',
        'actionData.amount': 'amount',
        'actionData.type': 'action_type'
    })
    
    required_cols = ['user', 'timestamp', 'type', 'amount']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    
    return df

def safe_float_convert(x):
    """Safely convert string amounts to float"""
    try:
        return float(x)
    except (ValueError, TypeError):
        return 0.0

def engineer_features(df):
    """Create features from raw transaction data"""
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    
    df['amount'] = df['amount'].apply(safe_float_convert)
    
    user_features = df.groupby('user').agg({
        'timestamp': [
            ('tx_count', 'count'),
            ('tx_freq', lambda x: x.diff().mean().total_seconds() if len(x) > 1 else 0),
            ('tx_burstiness', lambda x: np.std([y.total_seconds() for y in x.diff().dropna()]) if len(x) > 1 else 0)
        ],
        'type': [
            ('deposit_ratio', lambda x: (x == 'deposit').mean()),
            ('borrow_ratio', lambda x: (x == 'borrow').mean()),
            ('liquidations', lambda x: (x == 'liquidationcall').sum())
        ],
        'amount': [
            ('avg_amount', 'mean'),
            ('amount_std', 'std'),
            ('total_volume', 'sum')
        ]
    })
    
    user_features.columns = ['_'.join(col).strip() for col in user_features.columns.values]
    
    user_features.replace([np.inf, -np.inf], np.nan, inplace=True)
    user_features.fillna(0, inplace=True)
    
    return user_features

def calculate_credit_scores(features):
    """Calculate credit scores using isolation forest"""
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features)
    
    clf = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
    clf.fit(X_scaled)
    
    anomaly_scores = clf.decision_function(X_scaled)
    
    min_score, max_score = anomaly_scores.min(), anomaly_scores.max()
    credit_scores = 1000 * (anomaly_scores - min_score) / (max_score - min_score)
    
    return pd.Series(credit_scores, index=features.index)

def analyze_scores(scores):
    """Generate analysis and visualizations"""
    os.makedirs('output', exist_ok=True)
    
    plt.figure(figsize=(10, 6))
    bins = range(0, 1100, 100)
    plt.hist(scores, bins=bins, edgecolor='black')
    plt.title('Wallet Credit Score Distribution')
    plt.xlabel('Credit Score')
    plt.ylabel('Number of Wallets')
    plt.savefig('output/score_distribution.png')
    plt.close()
    
    analysis = {
        'mean_score': scores.mean(),
        'median_score': scores.median(),
        'score_std': scores.std(),
        'score_ranges': pd.cut(scores, bins=bins).value_counts().sort_index().to_dict()
    }
    
    return analysis

def main(input_file):
    print(f"Processing file: {input_file}")
    
    try:
        df = load_data(input_file)
        print(f"Loaded {len(df)} transactions")
        
        features = engineer_features(df)
        print(f"Generated features for {len(features)} wallets")
        
        scores = calculate_credit_scores(features)
        print("Credit scores calculated")
        
        scores.to_csv('output/wallet_scores.csv')
        print("Saved wallet_scores.csv")
        
        analysis = analyze_scores(scores)
        with open('output/analysis.md', 'w') as f:
            f.write(f"## Credit Score Analysis\n\n")
            f.write(f"**Statistics:**\n")
            f.write(f"- Mean score: {analysis['mean_score']:.2f}\n")
            f.write(f"- Median score: {analysis['median_score']:.2f}\n")
            f.write(f"- Standard deviation: {analysis['score_std']:.2f}\n\n")
            f.write(f"**Score Distribution:**\n")
            for rng, cnt in analysis['score_ranges'].items():
                f.write(f"- {rng}: {cnt} wallets\n")
            
            f.write("\n## Behavior Analysis\n")
            f.write("- **High scores (800-1000):** Regular, responsible usage patterns\n")
            f.write("- **Medium scores (400-800):** Somewhat irregular but not clearly risky\n")
            f.write("- **Low scores (0-400):** Highly irregular patterns, possible bots or exploit attempts\n")
        
        print("Analysis complete. Results saved in 'output' directory")
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_json_file>")
        sys.exit(1)
    
    main(sys.argv[1])