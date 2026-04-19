import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent / "src"))
from dataguard.config import config

st.set_page_config(
    page_title="DataGuard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&family=DM+Mono:wght@300;400;500&display=swap');

/* ── Fonts everywhere ── */
html, body, [class*="css"], .stApp {
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] > div {
    padding-top: 1.5rem;
}
section[data-testid="stSidebar"] .stRadio label {
    font-family: 'DM Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    padding: 5px 0;
}
section[data-testid="stSidebar"] .stRadio > div {
    gap: 2px;
}

/* ── Main padding ── */
.main .block-container {
    padding: 2rem 2.5rem 3rem;
    max-width: 1380px;
}

/* ── Page header ── */
.pg-header {
    margin-bottom: 2rem;
    padding-bottom: 1.2rem;
    border-bottom: 1px solid rgba(128,128,128,0.2);
}
.pg-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    opacity: 0.4;
    margin-bottom: 0.4rem;
}
.pg-header h1 {
    font-family: 'DM Sans', sans-serif;
    font-size: 1.9rem;
    font-weight: 300;
    letter-spacing: -0.03em;
    margin: 0 0 0.2rem;
    line-height: 1.1;
}
.pg-header h1 strong { font-weight: 600; }
.pg-runtag {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    opacity: 0.45;
    letter-spacing: 0.04em;
    margin-top: 0.5rem;
}
.pg-runtag::before {
    content: '';
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #22c55e;
    opacity: 1;
}

/* ── KPI row: 4 cells separated by dividers ── */
.kpi-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    border: 1px solid rgba(128,128,128,0.18);
    border-radius: 14px;
    overflow: hidden;
    margin-bottom: 2.5rem;
}
.kpi-cell {
    padding: 1.4rem 1.6rem;
    border-right: 1px solid rgba(128,128,128,0.18);
    transition: background 0.15s;
}
.kpi-cell:last-child { border-right: none; }
.kpi-cell:hover { background: rgba(128,128,128,0.04); }

.kpi-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    opacity: 0.45;
    margin-bottom: 0.55rem;
}
.kpi-val {
    font-family: 'DM Sans', sans-serif;
    font-size: 2.3rem;
    font-weight: 300;
    letter-spacing: -0.04em;
    line-height: 1;
}
.kpi-val.c-green { color: #16a34a; }
.kpi-val.c-red   { color: #dc2626; }
.kpi-val.c-amber { color: #d97706; }
.kpi-val.c-blue  { color: #2563eb; }
.kpi-hint {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    opacity: 0.3;
    margin-top: 0.35rem;
}

/* ── Section label ── */
.sec-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.13em;
    text-transform: uppercase;
    opacity: 0.38;
    margin: 1.8rem 0 0.9rem;
    display: flex;
    align-items: center;
    gap: 10px;
}
.sec-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(128,128,128,0.18);
}

/* ── Row card (issues / history) ── */
.row-card {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.8rem 1.1rem;
    border: 1px solid rgba(128,128,128,0.15);
    border-radius: 10px;
    margin-bottom: 5px;
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    transition: border-color 0.15s, background 0.15s;
}
.row-card:hover {
    border-color: rgba(128,128,128,0.3);
    background: rgba(128,128,128,0.04);
}
.row-card.active {
    border-left: 3px solid #2563eb;
}

/* ── Severity pill ── */
.pill {
    display: inline-block;
    padding: 2px 9px 3px;
    border-radius: 5px;
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    font-weight: 500;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    flex-shrink: 0;
}
.pill-HIGH   { background: rgba(220,38,38,0.12);  color: #dc2626; }
.pill-MEDIUM { background: rgba(217,119,6,0.12);  color: #d97706; }
.pill-LOW    { background: rgba(22,163,74,0.12);   color: #16a34a; }

/* ── Mini stat strip ── */
.stat-strip {
    display: flex;
    gap: 1px;
    border: 1px solid rgba(128,128,128,0.18);
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 1.8rem;
}
.stat-cell {
    flex: 1;
    padding: 1rem 1.2rem;
}
.stat-cell:hover { background: rgba(128,128,128,0.04); }

/* ── Sidebar info box ── */
.info-box {
    padding: 0.9rem 1rem;
    border: 1px solid rgba(128,128,128,0.18);
    border-radius: 10px;
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    line-height: 2;
    margin-top: 0.6rem;
    opacity: 0.85;
}
.info-box .lk { opacity: 0.5; }
.info-box .lv-green { color: #16a34a; }

/* ── Streamlit widget overrides ── */
.stSelectbox > div > div {
    border-radius: 8px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 12px !important;
}
.stTextInput > div > div > input {
    border-radius: 8px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 12px !important;
}
.stButton > button {
    border-radius: 8px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 0.05em;
    font-weight: 500;
    padding: 0.45rem 1.2rem;
}
.stDownloadButton > button {
    border-radius: 8px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 0.04em;
    width: 100%;
}
div[data-testid="stFileUploader"] {
    border-radius: 10px !important;
}
.stDataFrame { border-radius: 10px; }
hr { opacity: 0.15 !important; }
</style>
""", unsafe_allow_html=True)

# ── Plotly: neutral theme that works on both light & dark ─────────────────────
def make_layout(title=""):
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Mono, monospace", size=11),
        title=dict(text=title, font=dict(family="DM Sans, sans-serif", size=14, weight=300)),
        xaxis=dict(gridcolor="rgba(128,128,128,0.15)", linecolor="rgba(128,128,128,0.15)",
                   tickfont=dict(size=10)),
        yaxis=dict(gridcolor="rgba(128,128,128,0.15)", linecolor="rgba(128,128,128,0.15)",
                   tickfont=dict(size=10)),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
        margin=dict(l=10, r=10, t=44, b=10),
        colorway=["#2563eb", "#16a34a", "#d97706", "#dc2626", "#7c3aed"],
    )

SEV_COLOR = {"HIGH": "#dc2626", "MEDIUM": "#d97706", "LOW": "#16a34a"}

# ── DB ────────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_conn():
    return sqlite3.connect(config.db_path, check_same_thread=False)

def q(sql, params=None):
    return pd.read_sql(sql, get_conn(), params=params)

def get_runs():         return q("SELECT * FROM quality_runs ORDER BY timestamp DESC")
def get_issues(rid):    return q("SELECT * FROM quality_issues WHERE run_id=?", [int(rid)])
def get_anomalies(rid): return q("SELECT * FROM anomaly_flags WHERE run_id=?", [int(rid)])

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:0.5rem 0 1.2rem;'>
        <div style='font-family:DM Mono,monospace;font-size:9px;letter-spacing:0.15em;
                    text-transform:uppercase;opacity:0.35;margin-bottom:5px;'>System</div>
        <div style='font-family:DM Sans,sans-serif;font-size:1.3rem;font-weight:300;
                    letter-spacing:-0.02em;'>
            Data<strong style='font-weight:600;'>Guard</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    page = st.radio(
        "Navigate",
        ["Upload & Run", "Overview", "Quality Issues", "Anomaly Explorer", "Run History"],
        label_visibility="collapsed",
    )
    st.divider()

    runs_df = get_runs()
    if runs_df.empty and page != "Upload & Run":
        st.caption("No runs yet — use Upload & Run.")
        st.stop()
    elif runs_df.empty:
        run_row = {"run_id":0,"total_rows":0,"pass_rate":0,"issues_found":0,"anomalies_found":0}
        selected_run, run_id = "—", 0
    else:
        selected_run = st.selectbox("Run", runs_df["run_name"], label_visibility="collapsed")
        run_row = runs_df[runs_df["run_name"] == selected_run].iloc[0]
        run_id  = run_row["run_id"]

    st.markdown(f"""
    <div class="info-box">
        <span class="lk">run_id&nbsp;&nbsp;</span>{run_id}<br>
        <span class="lk">rows&nbsp;&nbsp;&nbsp;&nbsp;</span>{int(run_row.get('total_rows',0)):,}<br>
        <span class="lk">pass&nbsp;&nbsp;&nbsp;&nbsp;</span>
        <span class="lv-green">{run_row.get('pass_rate',0):.1f}%</span>
    </div>
    """, unsafe_allow_html=True)

    if not runs_df.empty:
        st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
        ci = get_issues(run_id)
        ca = get_anomalies(run_id)
        if not ci.empty:
            st.download_button("↓ Export Issues CSV", ci.to_csv(index=False).encode(),
                               f"issues_{selected_run}.csv", "text/csv", use_container_width=True)
        if not ca.empty:
            st.download_button("↓ Export Anomalies CSV", ca.to_csv(index=False).encode(),
                               f"anomalies_{selected_run}.csv", "text/csv", use_container_width=True)

# ── helpers ───────────────────────────────────────────────────────────────────
def header(eyebrow, title_html, run=None):
    run_tag = f'<div class="pg-runtag">{run}</div>' if run else ""
    st.markdown(f"""
    <div class="pg-header">
        <div class="pg-eyebrow">{eyebrow}</div>
        <h1>{title_html}</h1>
        {run_tag}
    </div>""", unsafe_allow_html=True)

def sec(label):
    st.markdown(f'<div class="sec-label">{label}</div>', unsafe_allow_html=True)

def empty_state(msg):
    st.markdown(f"""
    <div style='padding:3.5rem;text-align:center;font-family:DM Mono,monospace;
                font-size:11px;letter-spacing:0.1em;opacity:0.4;'>
        ✓ &nbsp;{msg}
    </div>""", unsafe_allow_html=True)

# ── UPLOAD & RUN ──────────────────────────────────────────────────────────────
if page == "Upload & Run":
    header("DataGuard — New Analysis", "<strong>Upload</strong> & Run")
    uploaded = st.file_uploader("CSV file", type=["csv"])
    run_name = st.text_input("Run name", value="scan_run_1")
    if st.button("▶  Start Pipeline"):
        if uploaded and run_name:
            from src.dataguard.pipeline import run_pipeline
            config.input_dir.mkdir(parents=True, exist_ok=True)
            sp = config.input_dir / uploaded.name
            sp.write_bytes(uploaded.getbuffer())
            with st.spinner("Running pipeline…"):
                r = run_pipeline(
                    input_file=str(sp), run_name=run_name,
                    schema={"order_id":"int64","customer_id":"int64",
                            "unit_price":"float64","quantity":"int64"},
                    rules={"unit_price":(0.01,1000.0),"quantity":(1,100)},
                )
            if r:
                st.success(f"Complete — {r['issues']} issues · {r['anomalies']} anomalies")
        else:
            st.warning("Please upload a file and enter a run name.")
    st.stop()

# ── OVERVIEW ──────────────────────────────────────────────────────────────────
elif page == "Overview":
    header("DataGuard — Dashboard", "Data<strong>Guard</strong>", selected_run)

    total  = int(run_row["total_rows"])
    rate   = float(run_row["pass_rate"])
    issues = int(run_row["issues_found"])
    anom   = int(run_row["anomalies_found"])

    rc = "c-green" if rate>=90  else "c-amber" if rate>=70  else "c-red"
    ic = "c-red"   if issues>10 else "c-amber" if issues>0  else "c-green"
    ac = "c-red"   if anom>20   else "c-amber" if anom>0    else "c-green"

    st.markdown(f"""
    <div class="kpi-row">
        <div class="kpi-cell">
            <div class="kpi-label">Total Rows</div>
            <div class="kpi-val c-blue">{total:,}</div>
            <div class="kpi-hint">records ingested</div>
        </div>
        <div class="kpi-cell">
            <div class="kpi-label">Pass Rate</div>
            <div class="kpi-val {rc}">{rate:.1f}<span style="font-size:1.1rem;opacity:0.6;">%</span></div>
            <div class="kpi-hint">validation success</div>
        </div>
        <div class="kpi-cell">
            <div class="kpi-label">Issues</div>
            <div class="kpi-val {ic}">{issues}</div>
            <div class="kpi-hint">quality violations</div>
        </div>
        <div class="kpi-cell">
            <div class="kpi-label">Anomalies</div>
            <div class="kpi-val {ac}">{anom}</div>
            <div class="kpi-hint">flagged records</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    idf = get_issues(run_id)
    if not idf.empty:
        sec("Issues by check")
        c1, c2 = st.columns([3, 2])
        with c1:
            fig = go.Figure(go.Bar(
                x=idf["check_name"], y=idf["issue_count"],
                marker=dict(color=idf["severity"].map(SEV_COLOR),
                            line=dict(width=0), opacity=0.85),
                text=idf["issue_count"], textposition="outside",
                textfont=dict(family="DM Mono", size=10),
            ))
            fig.update_layout(**make_layout("Check results"), bargap=0.38)
            fig.update_xaxes(tickangle=-15)
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            sc = idf["severity"].value_counts().reset_index()
            sc.columns = ["severity","count"]
            fig2 = go.Figure(go.Pie(
                labels=sc["severity"], values=sc["count"], hole=0.68,
                marker=dict(colors=[SEV_COLOR.get(s,"#888") for s in sc["severity"]],
                            line=dict(color="rgba(0,0,0,0)", width=3)),
                textfont=dict(family="DM Mono", size=10),
            ))
            fig2.update_layout(
                **make_layout("Severity mix"),
                annotations=[dict(
                    text=f"<b>{int(idf['issue_count'].sum())}</b>",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(family="DM Sans", size=26),
                )],
            )
            st.plotly_chart(fig2, use_container_width=True)
    else:
        empty_state("no issues for this run")

# ── QUALITY ISSUES ────────────────────────────────────────────────────────────
elif page == "Quality Issues":
    header("DataGuard — Validation", "Quality <strong>Issues</strong>", selected_run)

    idf = get_issues(run_id)
    if idf.empty:
        empty_state("no issues detected — data quality perfect")
    else:
        high = len(idf[idf["severity"]=="HIGH"])
        med  = len(idf[idf["severity"]=="MEDIUM"])
        low  = len(idf[idf["severity"]=="LOW"])

        st.markdown(f"""
        <div class="stat-strip">
            <div class="stat-cell">
                <div class="kpi-label">High</div>
                <div class="kpi-val c-red" style="font-size:1.9rem;">{high}</div>
            </div>
            <div class="stat-cell" style="border-left:1px solid rgba(128,128,128,0.18);">
                <div class="kpi-label">Medium</div>
                <div class="kpi-val c-amber" style="font-size:1.9rem;">{med}</div>
            </div>
            <div class="stat-cell" style="border-left:1px solid rgba(128,128,128,0.18);">
                <div class="kpi-label">Low</div>
                <div class="kpi-val c-green" style="font-size:1.9rem;">{low}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        sec("All issues")
        for _, row in idf.iterrows():
            sev = row.get("severity","LOW")
            st.markdown(f"""
            <div class="row-card">
                <span class="pill pill-{sev}">{sev}</span>
                <span style='flex:2;font-size:12px;'>{row.get('check_name','—')}</span>
                <span style='opacity:0.4;'>{row.get('column_name','—')}</span>
                <span style='font-weight:500;margin-left:auto;'>
                    {int(row.get('issue_count',0))} rows
                </span>
            </div>
            """, unsafe_allow_html=True)

# ── ANOMALY EXPLORER ──────────────────────────────────────────────────────────
elif page == "Anomaly Explorer":
    header("DataGuard — ML Detection", "Anomaly <strong>Explorer</strong>", selected_run)

    adf = get_anomalies(run_id)
    if adf.empty:
        empty_state("no anomalies detected")
    else:
        cols = ["All"] + sorted(adf["column_name"].unique().tolist())
        sel  = st.selectbox("Filter by column", cols, label_visibility="visible")
        flt  = adf if sel=="All" else adf[adf["column_name"]==sel]

        fig = go.Figure()
        for sev, color in SEV_COLOR.items():
            sub = flt[flt["severity"]==sev]
            if sub.empty: continue
            fig.add_trace(go.Scatter(
                x=sub["row_index"], y=sub["anomaly_score"],
                mode="markers", name=sev,
                marker=dict(color=color, size=7, opacity=0.8,
                            line=dict(color="rgba(0,0,0,0.2)", width=1)),
                hovertemplate=f"<b>{sev}</b><br>Row %{{x}}<br>Score %{{y:.3f}}<extra></extra>",
            ))
        fig.add_hline(y=0, line_dash="dot", line_color="rgba(128,128,128,0.3)")
        fig.update_layout(**make_layout(f"Anomaly scores — {sel}"),
                          xaxis_title="Row index", yaxis_title="Score")
        st.plotly_chart(fig, use_container_width=True)

        sec(f"Flagged records ({len(flt)})")
        st.dataframe(flt, use_container_width=True, height=300)

# ── RUN HISTORY ───────────────────────────────────────────────────────────────
elif page == "Run History":
    header("DataGuard — Audit", "Run <strong>History</strong>")

    hist = get_runs()
    fig  = go.Figure()
    fig.add_trace(go.Scatter(
        x=hist["timestamp"], y=hist["issues_found"],
        mode="lines+markers", name="Issues",
        line=dict(color="#dc2626", width=1.5),
        marker=dict(size=5, color="#dc2626"),
        fill="tozeroy", fillcolor="rgba(220,38,38,0.06)",
    ))
    fig.add_trace(go.Scatter(
        x=hist["timestamp"], y=hist["anomalies_found"],
        mode="lines+markers", name="Anomalies",
        line=dict(color="#2563eb", width=1.5),
        marker=dict(size=5, color="#2563eb"),
        fill="tozeroy", fillcolor="rgba(37,99,235,0.06)",
    ))
    fig.add_trace(go.Scatter(
        x=hist["timestamp"], y=hist["pass_rate"],
        mode="lines+markers", name="Pass %",
        line=dict(color="#16a34a", width=1.5, dash="dot"),
        marker=dict(size=5, color="#16a34a"),
        yaxis="y2",
    ))
    fig.update_layout(
        **make_layout("Quality over time"),
        hovermode="x unified",
        yaxis2=dict(overlaying="y", side="right",
                    gridcolor="rgba(128,128,128,0.1)",
                    tickfont=dict(size=10)),
    )
    st.plotly_chart(fig, use_container_width=True)

    sec("All runs")
    for _, row in hist.iterrows():
        rate   = row["pass_rate"]
        rc     = "#16a34a" if rate>=90 else "#d97706" if rate>=70 else "#dc2626"
        active = "active" if row["run_name"] == selected_run else ""
        st.markdown(f"""
        <div class="row-card {active}">
            <span style='flex:2;font-size:12px;font-weight:500;'>{row['run_name']}</span>
            <span style='opacity:0.4;font-size:10px;'>{row['timestamp'][:16]}</span>
            <span style='opacity:0.6;'>{int(row['total_rows']):,} rows</span>
            <span style='color:{rc};font-weight:500;margin-left:auto;'>{rate:.1f}%</span>
            <span style='color:#dc2626;opacity:0.85;'>{int(row['issues_found'])} issues</span>
            <span style='color:#2563eb;opacity:0.85;'>{int(row['anomalies_found'])} anom.</span>
        </div>
        """, unsafe_allow_html=True)