# 💳 Wallet Credit Scoring System

## 📌 Overview

I built this machine learning system to analyze wallet transactions on Aave V2 and assign credit scores (0–1000) based on transaction behavior. Higher scores indicate trustworthy wallets, while lower scores flag potentially risky behavior.

---

## 🛠 How It Works

### 1. Data Loading

- Takes raw JSON transaction data (like the sample provided)
- Normalizes nested JSON structure using `pd.json_normalize()`
- Renames columns to match expected format:
  - `userWallet` → `user`
  - `action` → `type`
  - `actionData.amount` → `amount`

### 2. Feature Engineering

The system extracts key features from transaction data:

#### 📊 Transaction Patterns

- `tx_count`: Total transactions  
- `tx_freq`: Average time between transactions  
- `tx_burstiness`: Measures irregular timing patterns  

#### 💰 Financial Behavior

- `deposit_ratio`: % of deposits vs other actions  
- `borrow_ratio`: % of borrows  
- `liquidations`: Count of liquidation events  

#### 💵 Amount Analysis

- `avg_amount`: Mean transaction size  
- `amount_std`: Amount volatility  
- `total_volume`: Sum of all transactions  

### 3. Credit Scoring

- Uses **Isolation Forest** algorithm to detect anomalous behavior
- Scores range from 0 to 1000:
  - **800–1000**: Regular, human-like patterns
  - **400–800**: Somewhat irregular
  - **0–400**: Likely bots or exploit behavior

---

## 🚀 How to Run It

Follow these steps to use the scoring system:

1. **Install requirements**:
   ```bash
   pip install -r requirements.txt
Run the scoring:

bash
Copy
Edit
python Model.py user-wallet-transactions.json
Check output in /output/ folder:
If not automatically created, run:

bash
Copy
Edit
mkdir output
Output files:
wallet_scores.csv: Wallet address and scores

score_distribution.png: Visualization of score distribution

analysis.md: Summary report

📂 Sample JSON Structure
The input transaction file should contain entries like:

json
Copy
Edit
{
  "userWallet": "0x000...",
  "timestamp": 1629178166,
  "action": "deposit",
  "actionData": {
    "amount": "2000000000",
    "type": "Deposit"
  }
}
🔍 Key Technical Details
Algorithm Choice
Isolation Forest is ideal for:

High-dimensional transaction data

Anomaly detection

No need for labeled training data

Score Interpretation
These are relative scores (not absolute probabilities)

Lower scores = more deviation from normal behavior

Use thresholds to segment users by risk

🛠 Troubleshooting
"No such file" error
Make sure the output directory exists:

bash
Copy
Edit
mkdir output
Git push errors
If you're getting branch errors:

bash
Copy
Edit
git branch -m master main
git push -u origin main
📈 Sample Output


Mean score: 682.42

Score Range	Interpretation	Wallets
800–1000	Responsible users	187
400–800	Moderate risk	2419
0–400	High risk	891

🤝 Contributing
Feel free to:

Report issues

Suggest improvements

Fork and adapt for your needs

javascript
Copy
Edit
