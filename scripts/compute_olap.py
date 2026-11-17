import json
import sys
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from finguard.database import connect_mysql

def main():
    conn = connect_mysql()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT 
            p.model_name,
            CASE
                WHEN t.transaction_time BETWEEN 0 AND 3599 THEN '0-1h'
                WHEN t.transaction_time BETWEEN 3600 AND 7199 THEN '1-2h'
                WHEN t.transaction_time BETWEEN 7200 AND 10799 THEN '2-3h'
                ELSE '3h+'
            END AS time_band,
            CASE
                WHEN t.transaction_amount < 10 THEN '0-10'
                WHEN t.transaction_amount < 50 THEN '10-50'
                WHEN t.transaction_amount < 100 THEN '50-100'
                WHEN t.transaction_amount < 250 THEN '100-250'
                WHEN t.transaction_amount < 500 THEN '250-500'
                WHEN t.transaction_amount < 1000 THEN '500-1000'
                ELSE '1000+'
            END AS amount_band,
            CASE 
                WHEN p.predicted_label = 1 AND t.class_label = 1 THEN 'True Positive'
                WHEN p.predicted_label = 1 AND t.class_label = 0 THEN 'False Positive'
                WHEN p.predicted_label = 0 AND t.class_label = 1 THEN 'False Negative'
                ELSE 'True Negative'
            END AS outcome,
            COUNT(*) AS tx_count,
            ROUND(SUM(t.transaction_amount), 2) AS total_amount,
            SUM(CASE WHEN t.class_label = 1 THEN 1 ELSE 0 END) AS fraud_count,
            ROUND(SUM(CASE WHEN t.class_label = 1 THEN t.transaction_amount ELSE 0 END), 2) AS fraud_amount,
            SUM(CASE WHEN p.predicted_label = 1 THEN 1 ELSE 0 END) AS flagged_count,
            ROUND(SUM(CASE WHEN p.predicted_label = 1 AND t.class_label = 1 THEN t.transaction_amount ELSE 0 END), 2) AS prevented_amount
        FROM transaction_predictions p
        JOIN transactions t ON t.transaction_id = p.transaction_id
        GROUP BY p.model_name, time_band, amount_band, outcome
    """)
    rows = cur.fetchall()
    print(f"Computed {len(rows)} OLAP cells.")
    total_tx = sum(r["tx_count"] for r in rows if r["model_name"] == "random_forest")
    print(f"Total transactions in random_forest: {total_tx}")
    
    # Save as JSON for caching
    out_file = Path(__file__).resolve().parent.parent / "reports" / "sql_exports" / "olap_cube.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w") as f:
        # Convert Decimals to float
        clean_rows = []
        for r in rows:
            clean_rows.append({
                "model_name": r["model_name"],
                "time_band": r["time_band"],
                "amount_band": r["amount_band"],
                "outcome": r["outcome"],
                "tx_count": int(r["tx_count"]),
                "total_amount": float(r["total_amount"] or 0),
                "fraud_count": int(r["fraud_count"] or 0),
                "fraud_amount": float(r["fraud_amount"] or 0),
                "flagged_count": int(r["flagged_count"] or 0),
                "prevented_amount": float(r["prevented_amount"] or 0)
            })
        json.dump(clean_rows, f, indent=2)
    print(f"Saved to {out_file}")
    conn.close()

if __name__ == "__main__":
    main()
