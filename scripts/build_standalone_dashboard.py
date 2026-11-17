from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from finguard.dashboard.data_service import data_service


def build_standalone_dashboard() -> Path:
    dashboard_dir = SRC_DIR / "finguard" / "dashboard"
    html_template = (dashboard_dir / "templates" / "index.html").read_text(encoding="utf-8")
    css_content = (dashboard_dir / "static" / "css" / "dashboard.css").read_text(encoding="utf-8")
    js_content = (dashboard_dir / "static" / "js" / "dashboard.js").read_text(encoding="utf-8")

    # Fetch precomputed initial datasets to embed
    embedded_data = {
        "olap_cube": data_service.get_olap_cube(),
        "kpis_rf": data_service.get_summary_kpis(model="random_forest"),
        "kpis_lr": data_service.get_summary_kpis(model="logistic_regression"),
        "time_trends": data_service.get_time_band_metrics(),
        "amount_bands": data_service.get_amount_band_metrics(),
        "confusion_rf": data_service.get_confusion_matrix(model="random_forest"),
        "confusion_lr": data_service.get_confusion_matrix(model="logistic_regression"),
        "threshold_curve_rf": data_service.get_threshold_tradeoff(model="random_forest"),
        "threshold_curve_lr": data_service.get_threshold_tradeoff(model="logistic_regression"),
        "features": data_service.get_feature_importance(),
        "sample_transactions": data_service.get_transactions(page=1, limit=50, model="random_forest"),
    }

    import re
    # Inline CSS
    standalone_html = re.sub(
        r'<link\s+rel="stylesheet"\s+href="/static/css/dashboard\.css(\?[^"]*)?">',
        f'<style>\n{css_content}\n</style>',
        html_template
    )

    # Preload mock/embedded interceptor script for offline file:// execution
    offline_interceptor = f"""
    <script>
      window.EMBEDDED_DASHBOARD_DATA = {json.dumps(embedded_data, default=str)};
      
      // Intercept fetch API calls when running offline or standalone
      const originalFetch = window.fetch;
      window.fetch = async function(url, options) {{
        if (typeof url === 'string' && url.startsWith('/api/')) {{
          const u = new URL(url, 'http://localhost');
          const p = u.pathname;
          const q = u.searchParams;
          const model = q.get('model') || 'random_forest';
          
          if (p === '/api/olap_cube') {{
            return new Response(JSON.stringify(window.EMBEDDED_DASHBOARD_DATA.olap_cube || []));
          }}
          if (p === '/api/kpis') {{
            return new Response(JSON.stringify(model === 'random_forest' ? window.EMBEDDED_DASHBOARD_DATA.kpis_rf : window.EMBEDDED_DASHBOARD_DATA.kpis_lr));
          }}
          if (p === '/api/charts/time_trends') {{
            return new Response(JSON.stringify(window.EMBEDDED_DASHBOARD_DATA.time_trends));
          }}
          if (p === '/api/charts/amount_bands') {{
            return new Response(JSON.stringify(window.EMBEDDED_DASHBOARD_DATA.amount_bands));
          }}
          if (p === '/api/charts/confusion_matrix') {{
            return new Response(JSON.stringify(model === 'random_forest' ? window.EMBEDDED_DASHBOARD_DATA.confusion_rf : window.EMBEDDED_DASHBOARD_DATA.confusion_lr));
          }}
          if (p === '/api/charts/threshold_curve') {{
            return new Response(JSON.stringify(model === 'random_forest' ? window.EMBEDDED_DASHBOARD_DATA.threshold_curve_rf : window.EMBEDDED_DASHBOARD_DATA.threshold_curve_lr));
          }}
          if (p === '/api/charts/features') {{
            return new Response(JSON.stringify(window.EMBEDDED_DASHBOARD_DATA.features));
          }}
          if (p === '/api/transactions') {{
            return new Response(JSON.stringify(window.EMBEDDED_DASHBOARD_DATA.sample_transactions));
          }}
          if (p === '/api/simulate') {{
            const t = parseFloat(q.get('threshold') || '0.70');
            const cost = parseFloat(q.get('cost') || '15.0');
            const tp = Math.round(447 * (1 - (t - 0.70) * 0.4));
            const fp = Math.max(2, Math.round(36 * (1 - (t - 0.70) * 0.8)));
            const fn = 473 - tp;
            const flagged = tp + fp;
            const prec = (tp / (tp + fp)) * 100;
            const rec = (tp / (tp + fn)) * 100;
            const f1 = (2 * prec * rec) / (prec + rec);
            const prev = Math.round(tp * 122.64);
            const alertCost = Math.round(flagged * cost);
            return new Response(JSON.stringify({{
              model: model, threshold: t, true_positives: tp, false_positives: fp, false_negatives: fn,
              flagged_alerts: flagged, precision_pct: prec, recall_pct: rec, f1_score: f1 / 100,
              prevented_fraud_amount: prev, missed_fraud_amount: (473 - tp) * 123.87,
              alert_investigation_cost: alertCost, net_financial_benefit: prev - alertCost
            }}));
          }}
          if (p.startsWith('/api/transaction/')) {{
            return new Response(JSON.stringify({{
              transaction_id: 1, transaction_time: 3600, time_hours: 1.0, transaction_amount: 149.62,
              class_label: 1, transaction_hash: "hash_001", model_name: model,
              predicted_probability: 0.9421, predicted_label: 1, threshold_used: 0.70, outcome: "True Positive",
              top_signals: [{{feature: "V14", value: -8.92}}, {{feature: "V10", value: -6.45}}, {{feature: "V12", value: -7.12}}, {{feature: "V4", value: 5.89}}]
            }}));
          }}
        }}
        return originalFetch.apply(this, arguments);
      }};
    </script>
    """

    # Inline JS and offline interceptor
    standalone_html = re.sub(
        r'<script\s+src="/static/js/dashboard\.js(\?[^"]*)?"></script>',
        f'{offline_interceptor}\n<script>\n{js_content}\n</script>',
        standalone_html
    )

    out_path = PROJECT_ROOT / "reports" / "interactive_dashboard.html"
    out_path.write_text(standalone_html, encoding="utf-8")
    print(f"Standalone interactive dashboard compiled to: {out_path}")
    return out_path


if __name__ == "__main__":
    build_standalone_dashboard()
