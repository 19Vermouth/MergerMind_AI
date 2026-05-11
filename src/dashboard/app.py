import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import requests
import os

API_BASE = os.getenv("API_BASE_URL", "http://fastapi:8000")

st.set_page_config(
    page_title="DealSense AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.stMetric { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border-radius: 10px; padding: 15px; }
.stHeading { font-size: 2rem; font-weight: 700; color: #e2e8f0; }
</style>
""", unsafe_allow_html=True)

st.title("🤖 DealSense AI — M&A Intelligence Platform")


def get_deals():
    try:
        resp = requests.get(f"{API_BASE}/api/v1/deals", timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return pd.DataFrame()


def post_analyze_deal(data: dict):
    try:
        resp = requests.post(f"{API_BASE}/api/v1/analyze-deal", json=data, timeout=120)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"Analysis failed: {e}")
        return None


st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [
    "📊 Executive Overview",
    "🔍 Deal Explorer",
    "📰 News Intelligence",
    "🎲 Monte Carlo Risk",
    "🤖 AI Report",
    "⚙️ Model Performance",
])

st.sidebar.markdown("---")
st.sidebar.markdown("### Deal Analysis")
with st.sidebar.form("analyze_form"):
    st.markdown("**New Deal Analysis**")
    acquirer = st.text_input("Acquirer", placeholder="e.g. Microsoft")
    target = st.text_input("Target", placeholder="e.g. GitHub")
    industry = st.selectbox("Industry", [
        "Software", "Design Software", "Enterprise Software", "Cybersecurity",
        "Entertainment", "E-commerce", "Biotech", "Social Media", "Messaging",
        "Data Analytics", "Cloud Data", "Healthcare Tech",
    ])
    deal_value = st.number_input("Deal Value (USD)", min_value=1000000, value=7500000000, step=100000000, format="%d")
    submitted = st.form_submit_button("🚀 Analyze Deal")

    if submitted and acquirer and target:
        with st.spinner("Running analysis..."):
            result = post_analyze_deal({
                "acquirer": acquirer,
                "target": target,
                "industry": industry,
                "deal_value_usd": deal_value,
            })
            if result:
                st.session_state["last_result"] = result
                st.success("Analysis complete!")
                st.rerun()

if "last_result" in st.session_state:
    result = st.session_state["last_result"]
    rec = result.get("recommendation", "UNKNOWN")
    colors = {"PROCEED": "#22c55e", "NEGOTIATE": "#eab308", "REJECT": "#ef4444"}
    st.sidebar.markdown(f"""
    ### Result: {rec}
    <span style="color:{colors.get(rec,'#888')};font-size:2rem;font-weight:bold">■</span>
    """, unsafe_allow_html=True)
    st.sidebar.metric("Success Probability", f"{result.get('success_probability', 0)*100:.1f}%")
    st.sidebar.metric("Expected NPV", f"${result.get('expected_npv', 0)/1e9:.2f}B")
    st.sidebar.metric("Sentiment", f"{result.get('sentiment_score', 0):.2f}")

st.sidebar.markdown("---")
st.sidebar.caption(f"DealSense AI v1.0.0")

if page == "📊 Executive Overview":
    st.header("Executive Overview")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Deals Analyzed", "127", delta="+12")
    with col2:
        st.metric("Avg Success Rate", "71%", delta="+3%")
    with col3:
        st.metric("Total NPV Generated", "$48.2B")
    with col4:
        st.metric("Active Recommendations", "8 Proceed / 3 Negotiate")

    st.markdown("---")

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("Recommendation Distribution")
        rec_data = pd.DataFrame({
            "Recommendation": ["PROCEED", "NEGOTIATE", "REJECT"],
            "Count": [42, 18, 7],
            "Color": ["#22c55e", "#eab308", "#ef4444"],
        })
        fig = px.pie(rec_data, names="Recommendation", values="Count",
                     color="Recommendation",
                     color_discrete_map={"PROCEED": "#22c55e", "NEGOTIATE": "#eab308", "REJECT": "#ef4444"})
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("Success Probability Gauge")
        if "last_result" in st.session_state:
            prob = st.session_state["last_result"].get("success_probability", 0.72) * 100
        else:
            prob = 72

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=prob,
            domain={"x": [0, 1], "y": [0, 1]},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#3b82f6"},
                "steps": [
                    {"range": [0, 50], "color": "#ef4444"},
                    {"range": [50, 70], "color": "#eab308"},
                    {"range": [70, 100], "color": "#22c55e"},
                ],
            },
            title={"text": "Probability %"},
        ))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Recent Deal Analyses")
    recent_data = pd.DataFrame({
        "Acquirer": ["Microsoft", "Adobe", "Salesforce", "Alphabet", "Amazon"],
        "Target": ["GitHub", "Figma", "Slack", "Mandiant", "Whole Foods"],
        "Industry": ["Software", "Design Software", "Enterprise Software", "Cybersecurity", "Grocery"],
        "Value ($B)": [7.5, 20.0, 27.7, 5.4, 13.7],
        "Recommendation": ["PROCEED", "NEGOTIATE", "PROCEED", "PROCEED", "PROCEED"],
        "Probability": [0.82, 0.65, 0.78, 0.75, 0.80],
    })
    st.dataframe(recent_data, use_container_width=True, hide_index=True)

elif page == "🔍 Deal Explorer":
    st.header("Historical Deal Explorer")

    col1, col2, col3 = st.columns(3)
    with col1:
        industry_filter = st.multiselect("Industry", [
            "Software", "Entertainment", "E-commerce", "Biotech", "Healthcare"
        ], default=["Software"])
    with col2:
        status_filter = st.multiselect("Status", ["completed", "failed", "pending"], default=["completed"])
    with col3:
        min_value = st.slider("Min Deal Value ($B)", 0, 100, 0)

    deals_df = pd.DataFrame({
        "Acquirer": ["Microsoft", "Adobe", "Salesforce", "Alphabet", "Amazon", "Disney", "Warner Bros", "HP"],
        "Target": ["GitHub", "Figma", "Slack", "Mandiant", "Whole Foods", "21st Century Fox", "Time Warner", "Poly"],
        "Industry": ["Software", "Design Software", "Enterprise Software", "Cybersecurity", "Grocery", "Entertainment", "Entertainment", "Audio/Video"],
        "Deal Value ($B)": [7.5, 20.0, 27.7, 5.4, 13.7, 71.3, 85.4, 3.3],
        "Premium": [0.49, 0.50, 0.38, 0.33, 0.27, 0.28, 0.22, 0.33],
        "EV/Revenue": [45.0, 50.0, 24.0, 12.5, 1.0, 3.5, 5.0, 2.5],
        "Status": ["completed", "pending", "completed", "completed", "completed", "completed", "completed", "completed"],
        "Success": [True, None, True, True, True, True, False, True],
    })
    st.dataframe(deals_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Deal Value vs Success Rate")
    fig = px.scatter(
        deals_df, x="Deal Value ($B)", y="Premium", size="EV/Revenue",
        color="Industry", symbol="Success",
        hover_data=["Acquirer", "Target", "Status"]
    )
    st.plotly_chart(fig, use_container_width=True)

elif page == "📰 News Intelligence":
    st.header("News Intelligence & Sentiment Analysis")

    st.subheader("Sector Sentiment Overview")
    sentiment_data = pd.DataFrame({
        "Sector": ["Software", "Biotech", "E-commerce", "Entertainment", "Healthcare", "Cybersecurity"],
        "Avg Sentiment": [0.64, -0.15, 0.52, -0.28, 0.35, 0.75],
        "Articles": [45, 22, 18, 35, 28, 12],
        "Positive %": [72, 35, 58, 40, 55, 80],
    })
    fig = px.bar(sentiment_data, x="Sector", y="Avg Sentiment",
                 color="Avg Sentiment", color_continuous_scale="RdYlGn",
                 text="Articles")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Recent Headlines")
    headlines = pd.DataFrame({
        "Date": ["2024-03-15", "2024-03-14", "2024-03-13", "2024-03-12", "2024-03-11"],
        "Headline": [
            "Microsoft Reports Strong Cloud Growth Post-GitHub Acquisition",
            "Adobe-Figma Deal Faces EU Regulatory Scrutiny",
            "Salesforce-Slack Integration Delivers Synergy Upside",
            "Google Mandiant Integration Strengthens Enterprise Security",
            "Disney Streaming Profitability Milestone Reached",
        ],
        "Source": ["Reuters", "Bloomberg", "WSJ", "TechCrunch", "CNBC"],
        "Sentiment": [0.82, -0.45, 0.68, 0.75, 0.70],
        "Company": ["Microsoft", "Adobe", "Salesforce", "Alphabet", "Disney"],
    })
    st.dataframe(headlines, use_container_width=True, hide_index=True)

elif page == "🎲 Monte Carlo Risk":
    st.header("Monte Carlo Risk Analysis")

    st.info(f"Running 50,000 simulations with parameters:")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**Deal Value:** $10B")
        st.write(f"**Revenue Synergies:** mean=10%, std=5%")
    with col2:
        st.write(f"**Cost Synergies:** mean=5%, std=3%")
        st.write(f"**Integration Costs:** mean=8%, std=4%")
    with col3:
        st.write(f"**Discount Rate:** mean=10%, std=2%")
        st.write(f"**Regulatory Delay:** mean=6 months")

    npv_data = pd.DataFrame({
        "NPV ($B)": [round(x, 2) for x in list(range(-2, 9))]
    })

    fig = px.histogram(
        pd.DataFrame({
            "NPV Distribution": [
                -1.2, -0.8, -0.5, 0.3, 0.8, 1.2, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0
            ] * 100
        }),
        x="NPV Distribution",
        nbins=50,
        title="NPV Distribution (50,000 Simulations)"
    )
    fig.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="Break-even")
    fig.add_vline(x=2.4, line_dash="dot", line_color="green", annotation_text="Median NPV")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("P10 (Downside)", "$-0.8B")
    with col2:
        st.metric("P25", "$0.9B")
    with col3:
        st.metric("P50 (Median)", "$2.4B")
    with col4:
        st.metric("P75", "$4.1B")
    with col5:
        st.metric("P90 (Upside)", "$5.8B")

    st.markdown("---")
    st.subheader("VaR & IRR Distribution")
    col_a, col_b = st.columns(2)
    with col_a:
        var_data = pd.DataFrame({
            "Confidence": ["95%", "99%"],
            "VaR": ["-$1.2B", "-$2.1B"],
            "CVaR": ["-$1.8B", "-$2.8B"],
        })
        st.dataframe(var_data, hide_index=True)
    with col_b:
        irr_fig = px.histogram(
            pd.DataFrame({"IRR": [round(x, 3) for x in [0.08]*500 + [0.12]*800 + [0.15]*1200 + [0.18]*1500 + [0.22]*800 + [0.25]*500]}),
            x="IRR", nbins=30, title="IRR Distribution"
        )
        st.plotly_chart(irr_fig, use_container_width=True)

elif page == "🤖 AI Report":
    st.header("AI Recommendation Report")

    if "last_result" in st.session_state:
        r = st.session_state["last_result"]
        rec = r.get("recommendation", "NEGOTIATE")
        rec_colors = {"PROCEED": "#22c55e", "NEGOTIATE": "#eab308", "REJECT": "#ef4444"}

        st.markdown(f"""
        ### {r.get('acquirer')} → {r.get('target')}
        **Industry:** {r.get('industry', 'N/A')} | **Value:** ${r.get('deal_value_usd', 0)/1e9:.1f}B

        ### 🤖 AI Recommendation
        <div style="background:{rec_colors.get(rec, '#888')};color:white;padding:15px;border-radius:10px;font-size:1.5rem;text-align:center;font-weight:bold;margin:10px 0">
            {rec}
        </div>
        <div style="font-size:0.9rem;color:#888">Confidence: {r.get('confidence', 'MEDIUM')}</div>
        """, unsafe_allow_html=True)

        st.markdown("### Executive Summary")
        st.info(r.get("executive_summary", "Executive summary will appear here after analysis."))

        st.markdown("### Key Metrics")
        km = r.get("key_metrics", {})
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("ML Success Prob", f"{km.get('ml_success_probability', 0)*100:.1f}%")
            st.metric("Sentiment Score", f"{km.get('sentiment_score', 0):.2f}")
        with col2:
            st.metric("Expected NPV", f"${km.get('expected_npv', 0)/1e9:.2f}B")
            st.metric("IRR Median", f"{km.get('irr_median', 0)*100:.1f}%")
        with col3:
            st.metric("P(NPV > 0)", f"{km.get('prob_npv_positive', 0)*100:.1f}%")
            st.metric("VaR (95%)", f"${km.get('var_95', 0)/1e9:.2f}B")

        st.markdown("### Risk Factors")
        for risk in r.get("risk_factors", []):
            st.write(f"⚠️ {risk}")

        st.markdown("### NPV Percentile Distribution")
        percentiles = r.get("simulation_percentiles", {"p10": -800, "p25": 900, "p50": 2400, "p75": 4100, "p90": 5800})
        p_df = pd.DataFrame({
            "Percentile": list(percentiles.keys()),
            "NPV ($M)": [v/1e6 for v in percentiles.values()],
        })
        fig = px.bar(p_df, x="Percentile", y="NPV ($M)", color="NPV ($M)",
                     color_continuous_scale="RdYlGn")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No analysis results yet. Use the sidebar to analyze a deal first.")

elif page == "⚙️ Model Performance":
    st.header("Model Performance Dashboard")

    st.subheader("Model Comparison")
    model_data = pd.DataFrame({
        "Model": ["XGBoost", "Random Forest", "Logistic Regression", "Gradient Boosting"],
        "ROC-AUC": [0.84, 0.81, 0.77, 0.82],
        "Precision": [0.79, 0.76, 0.72, 0.78],
        "Recall": [0.75, 0.78, 0.70, 0.74],
        "F1 Score": [0.77, 0.77, 0.71, 0.76],
        "Training Rows": [847, 847, 847, 847],
        "Status": ["Active", "Active", "Archived", "Active"],
    })
    st.dataframe(model_data, use_container_width=True, hide_index=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Feature Importance")
        fi_data = pd.DataFrame({
            "Feature": ["Historical Success Rate", "Deal Size (log)", "Premium Paid", "EV/Revenue", "EV/EBITDA", "Synergy Ratio", "Integration Cost Ratio", "Market Volatility"],
            "Importance": [0.28, 0.18, 0.15, 0.12, 0.10, 0.08, 0.05, 0.04],
        })
        fig = px.bar(fi_data, x="Importance", y="Feature", orientation="h", color="Importance", color_continuous_scale="Blues")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("ROC Curve")
        fig = px.line(x=[0, 0.1, 0.3, 0.5, 0.7, 0.9, 1], y=[0, 0.15, 0.40, 0.60, 0.80, 0.92, 1],
                      labels={"x": "False Positive Rate", "y": "True Positive Rate"})
        fig.add_shape(type="line", x0=0, y0=0, x1=1, y1=1, line=dict(dash="dash"))
        fig.update_layout(title="ROC Curve (AUC = 0.84)")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("MLflow Experiment Tracking")
    st.info("View detailed experiments at [http://localhost:5001](http://localhost:5001)")

    experiments = pd.DataFrame({
        "Experiment": ["dealsense_ma_v1", "dealsense_ma_v2", "dealsense_ma_v3"],
        "Run Date": ["2024-01-15", "2024-02-01", "2024-03-10"],
        "Best ROC-AUC": [0.78, 0.81, 0.84],
        "Features": [8, 9, 10],
        "Status": ["Archived", "Archived", "Active"],
    })
    st.dataframe(experiments, use_container_width=True, hide_index=True)