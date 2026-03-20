import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# ─── Page Config ──────────────────────────────────────────────────────────────

st.set_page_config(page_title="Hiring Funnel Dashboard", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

# ─── Design Tokens ────────────────────────────────────────────────────────────

C = {
    "blue": "#3B82F6",
    "blue_light": "#DBEAFE",
    "green": "#10B981",
    "green_light": "#D1FAE5",
    "red": "#EF4444",
    "red_light": "#FEE2E2",
    "amber": "#F59E0B",
    "amber_light": "#FEF3C7",
    "slate": "#475569",
    "slate_light": "#F1F5F9",
    "dark": "#0F172A",
    "funnel": ["#3B82F6", "#6366F1", "#8B5CF6", "#A855F7", "#EC4899"],
}

# ─── Global Styles ────────────────────────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .block-container { padding: 1.2rem 2rem 1rem 2rem; max-width: 1400px; }

    /* filter panel */
    .filter-bar {
        background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px;
        padding: 16px 20px; margin-bottom: 12px;
    }

    /* tabs — equidistant, full-width */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px; background: #F1F5F9; border-radius: 10px; padding: 4px;
        display: flex !important; justify-content: stretch;
    }
    .stTabs [data-baseweb="tab-list"] > button {
        flex: 1 1 0 !important; min-width: 0 !important;
        text-align: center; justify-content: center;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px; padding: 8px 12px; font-weight: 600; font-size: 0.85rem;
        color: #64748B; background: transparent; border: none;
        flex: 1 1 0 !important; justify-content: center;
    }
    .stTabs [aria-selected="true"] {
        background: #FFFFFF !important; color: #0F172A !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .stTabs [data-baseweb="tab-border"] { display: none; }
    .stTabs [data-baseweb="tab-highlight"] { display: none; }

    /* kpi strip */
    .kpi-strip { display: flex; gap: 14px; margin-bottom: 6px; }
    .kpi-card {
        flex: 1; background: #FFFFFF; border: 1px solid #E2E8F0;
        border-radius: 12px; padding: 16px 20px; text-align: center;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    }
    .kpi-label { font-size: 0.7rem; font-weight: 600; color: #94A3B8;
        text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 2px; }
    .kpi-value { font-size: 1.7rem; font-weight: 800; color: #0F172A; line-height: 1.2; }
    .kpi-sub { font-size: 0.7rem; color: #94A3B8; margin-top: 2px; }

    /* hero card */
    .hero-card {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        border-radius: 16px; padding: 36px 40px; text-align: center;
        margin-bottom: 20px;
    }
    .hero-emoji { font-size: 2.2rem; margin-bottom: 4px; }
    .hero-value { font-size: 3rem; font-weight: 800; color: #34D399; line-height: 1.1; }
    .hero-label { font-size: 1rem; color: #94A3B8; margin-top: 6px; font-weight: 500; }
    .hero-sub { font-size: 0.85rem; color: #64748B; margin-top: 10px; }

    /* insight bullets */
    .ins { padding: 12px 16px; border-radius: 10px; margin-bottom: 10px;
        font-size: 0.88rem; line-height: 1.5; }
    .ins-red { background: #FEF2F2; border-left: 4px solid #EF4444; color: #991B1B; }
    .ins-green { background: #F0FDF4; border-left: 4px solid #10B981; color: #065F46; }
    .ins-blue { background: #EFF6FF; border-left: 4px solid #3B82F6; color: #1E40AF; }

    /* section labels — high contrast */
    .sec-label {
        font-size: 1rem; font-weight: 800; color: #FFFFFF; margin-bottom: 14px;
        letter-spacing: -0.01em; padding-bottom: 6px;
        border-bottom: 2px solid #3B82F6; display: inline-block;
    }

    /* hide streamlit branding + sidebar */
    #MainMenu, footer, header { visibility: hidden; }
    [data-testid="collapsedControl"] { display: none; }
    [data-testid="stSidebar"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ─── Data Loading ─────────────────────────────────────────────────────────────

@st.cache_data
def load_data():
    df = pd.read_csv("hiring_funnel_mock_dataset.csv")
    for col in ["application_date", "screening_date", "interview_date", "offer_date", "hire_date"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    df["screened"] = df["screening_date"].notna()
    df["interviewed"] = df["interview_date"].notna()
    df["offered"] = df["offer_date"].notna()
    df["hired"] = df["hire_date"].notna()
    df["time_to_screen"] = (df["screening_date"] - df["application_date"]).dt.days
    df["time_to_interview"] = (df["interview_date"] - df["screening_date"]).dt.days
    df["time_to_offer"] = (df["offer_date"] - df["interview_date"]).dt.days
    df["time_to_hire_from_offer"] = (df["hire_date"] - df["offer_date"]).dt.days
    df["time_to_hire"] = (df["hire_date"] - df["application_date"]).dt.days
    return df

df_raw = load_data()

# ─── Inline Filter Toggle ─────────────────────────────────────────────────────

filter_on = st.toggle("🎯 Filters", value=True)

roles, recruiters, sources = [], [], []
min_d, max_d = df_raw["application_date"].min().date(), df_raw["application_date"].max().date()
date_range = (min_d, max_d)

if filter_on:
    with st.container():
        st.markdown("<div class='filter-bar'>", unsafe_allow_html=True)
        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1:
            roles = st.multiselect("Job Role", sorted(df_raw["job_role"].unique()), default=[])
        with fc2:
            recruiters = st.multiselect("Recruiter", sorted(df_raw["recruiter"].unique()), default=[])
        with fc3:
            sources = st.multiselect("Source", sorted(df_raw["source"].unique()), default=[])
        with fc4:
            date_range = st.date_input("Date Range", value=(min_d, max_d), min_value=min_d, max_value=max_d)
        st.markdown("</div>", unsafe_allow_html=True)

df = df_raw.copy()
if roles:
    df = df[df["job_role"].isin(roles)]
if recruiters:
    df = df[df["recruiter"].isin(recruiters)]
if sources:
    df = df[df["source"].isin(sources)]
if isinstance(date_range, tuple) and len(date_range) == 2:
    df = df[(df["application_date"].dt.date >= date_range[0]) & (df["application_date"].dt.date <= date_range[1])]

# ─── Metrics Engine ───────────────────────────────────────────────────────────

N = len(df)
n_screen = int(df["screened"].sum())
n_interview = int(df["interviewed"].sum())
n_offer = int(df["offered"].sum())
n_hire = int(df["hired"].sum())

cr_overall = n_hire / N * 100 if N else 0
cr_screen = n_screen / N * 100 if N else 0
cr_interview = n_interview / n_screen * 100 if n_screen else 0
cr_offer = n_offer / n_interview * 100 if n_interview else 0
cr_hire = n_hire / n_offer * 100 if n_offer else 0
offer_accept = cr_hire
avg_tth = df.loc[df["hired"], "time_to_hire"].mean() if n_hire else 0

drop_screen = N - n_screen
drop_interview = n_screen - n_interview
drop_offer = n_interview - n_offer
drop_hire = n_offer - n_hire

avg_t = {
    "App → Screen": df["time_to_screen"].mean(),
    "Screen → Interview": df["time_to_interview"].mean(),
    "Interview → Offer": df["time_to_offer"].mean(),
    "Offer → Hire": df["time_to_hire_from_offer"].mean(),
}
avg_t = {k: (v if pd.notna(v) else 0) for k, v in avg_t.items()}


def efficiency(cr_val, oar_val, tth_val):
    return (cr_val / 100 * oar_val / 100) / tth_val if tth_val and tth_val > 0 else 0


raw_eff_overall = efficiency(cr_overall, offer_accept, avg_tth)

stage_crs = {"Screening": cr_screen, "Interview": cr_interview, "Offer": cr_offer, "Hire": cr_hire}
worst_stage = min(stage_crs, key=stage_crs.get) if N else "N/A"
worst_cr = stage_crs.get(worst_stage, 0)
cr_list = [cr_screen, cr_interview, cr_offer, cr_hire]
idx_map = {"Screening": 0, "Interview": 1, "Offer": 2, "Hire": 3}


def simulate_improvement(pct=10):
    new_crs = list(cr_list)
    new_crs[idx_map[worst_stage]] = min(100, new_crs[idx_map[worst_stage]] + pct)
    cur = N
    for c in new_crs:
        cur = cur * c / 100
    return max(0, int(cur) - n_hire)


extra_hires = simulate_improvement(10)

# ─── Plotly Defaults ──────────────────────────────────────────────────────────

PLT = dict(
    margin=dict(l=20, r=20, t=52, b=16),
    font=dict(family="Inter, sans-serif", size=12, color="#334155"),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    hoverlabel=dict(bgcolor="#1E293B", font_color="#F8FAFC", font_size=12, bordercolor="rgba(0,0,0,0)"),
    hovermode="closest",
    bargap=0.25,
    uniformtext=dict(minsize=9, mode="show"),
)

def styled(fig, h=340, **kw):
    merged = {**PLT, **kw}
    fig.update_layout(**merged, height=h)
    fig.update_xaxes(gridcolor="#F1F5F9", zeroline=False,
                     title_font=dict(color="#1E293B", size=12),
                     tickfont=dict(color="#475569", size=11))
    fig.update_yaxes(gridcolor="#F1F5F9", zeroline=False,
                     title_font=dict(color="#1E293B", size=12),
                     tickfont=dict(color="#475569", size=11))
    if "title" in kw and isinstance(kw["title"], dict):
        pass
    elif "title" in kw:
        fig.update_layout(title_font=dict(color="#0F172A", size=14, family="Inter, sans-serif"))
    return fig

# ─── HEADER ───────────────────────────────────────────────────────────────────

st.markdown("## 📊 Hiring Funnel Dashboard")

# ─── KPI STRIP (always visible) ──────────────────────────────────────────────

kpi_html = "<div class='kpi-strip'>"
kpis = [
    ("Total Applicants", f"{N:,}", ""),
    ("Total Hires", f"{n_hire:,}", f"{cr_overall:.1f}% conversion"),
    ("Conversion Rate", f"{cr_overall:.1f}%", "end-to-end"),
    ("Avg Time to Hire", f"{avg_tth:.0f} days" if avg_tth else "—", "application → hire"),
    ("Offer Accept Rate", f"{offer_accept:.1f}%", f"{n_offer} offers"),
]
for label, val, sub in kpis:
    kpi_html += f"""<div class='kpi-card'>
        <div class='kpi-label'>{label}</div>
        <div class='kpi-value'>{val}</div>
        <div class='kpi-sub'>{sub}</div>
    </div>"""
kpi_html += "</div>"
st.markdown(kpi_html, unsafe_allow_html=True)
st.markdown("")

# ─── TABS ─────────────────────────────────────────────────────────────────────

t_overview, t_funnel, t_time, t_perf, t_impact, t_insights = st.tabs([
    "📊 Overview", "🔻 Funnel", "⏱ Time", "🧠 Performance", "💣 Impact", "🔍 Insights",
])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 1 — OVERVIEW
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

with t_overview:
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("<div class='sec-label'>Hiring Trend</div>", unsafe_allow_html=True)
        hired_df = df[df["hired"]].copy()
        if not hired_df.empty:
            hired_df["month"] = hired_df["hire_date"].dt.to_period("M").dt.to_timestamp()
            app_df = df.copy()
            app_df["month"] = app_df["application_date"].dt.to_period("M").dt.to_timestamp()
            trend_h = hired_df.groupby("month").size().reset_index(name="Hires")
            trend_a = app_df.groupby("month").size().reset_index(name="Applications")
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=trend_a["month"], y=trend_a["Applications"], name="Applications",
                mode="lines+markers", line=dict(color="#64748B", width=2, dash="dot"),
                marker=dict(size=6, color="#64748B"),
            ))
            fig.add_trace(go.Scatter(
                x=trend_h["month"], y=trend_h["Hires"], name="Hires",
                mode="lines+markers", line=dict(color=C["green"], width=3),
                marker=dict(size=8, color=C["green"]),
                fill="tozeroy", fillcolor="rgba(16,185,129,0.10)",
            ))
            styled(fig, yaxis_title="Count", hovermode="x unified",
                   legend=dict(orientation="h", y=1.08, x=0.5, xanchor="center"))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hire data for current filters.")

    with c2:
        st.markdown("<div class='sec-label'>Source Performance</div>", unsafe_allow_html=True)
        src = df.groupby("source").agg(
            Applicants=("candidate_id", "count"), Hires=("hired", "sum"),
        ).reset_index().sort_values("Applicants", ascending=False)
        src["Hires"] = src["Hires"].astype(int)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=src["source"], y=src["Applicants"], name="Applicants",
            marker_color="#93C5FD", text=src["Applicants"], textposition="outside",
            textfont=dict(color="#1E3A5F", size=11),
        ))
        fig.add_trace(go.Bar(
            x=src["source"], y=src["Hires"], name="Hires",
            marker_color=C["green"], text=src["Hires"], textposition="outside",
            textfont=dict(color="#065F46", size=11),
        ))
        styled(fig, barmode="group", yaxis_title="Count",
               legend=dict(orientation="h", y=1.08, x=0.5, xanchor="center"))
        st.plotly_chart(fig, use_container_width=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 2 — FUNNEL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

with t_funnel:
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("<div class='sec-label'>Candidate Funnel</div>", unsafe_allow_html=True)
        stages = ["Applied", "Screened", "Interviewed", "Offered", "Hired"]
        counts = [N, n_screen, n_interview, n_offer, n_hire]
        fig = go.Figure(go.Funnel(
            y=stages, x=counts, textinfo="value+percent initial",
            textfont=dict(color="#FFFFFF", size=13),
            marker=dict(color=C["funnel"]),
            connector=dict(line=dict(color="#E2E8F0", width=1)),
        ))
        styled(fig, h=380)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("<div class='sec-label'>Drop-offs by Stage</div>", unsafe_allow_html=True)
        drop_labels = ["At Screening", "At Interview", "At Offer", "At Hire"]
        drop_vals = [drop_screen, drop_interview, drop_offer, drop_hire]
        max_drop = max(drop_vals) if drop_vals else 0
        colors = [C["red"] if v == max_drop else "#F87171" for v in drop_vals]
        pcts = [
            drop_screen / N * 100 if N else 0,
            drop_interview / n_screen * 100 if n_screen else 0,
            drop_offer / n_interview * 100 if n_interview else 0,
            drop_hire / n_offer * 100 if n_offer else 0,
        ]
        fig = go.Figure(go.Bar(
            x=drop_labels, y=drop_vals,
            text=[f"{v} ({p:.0f}%)" for v, p in zip(drop_vals, pcts)],
            textposition="outside", marker_color=colors,
            textfont=dict(color="#991B1B", size=11),
        ))
        styled(fig, h=380, yaxis_title=dict(text="Candidates Lost", font=dict(color="#FFFFFF")))
        st.plotly_chart(fig, use_container_width=True)

    # conversion table
    st.markdown("<div class='sec-label'>Stage Conversion Detail</div>", unsafe_allow_html=True)
    conv_df = pd.DataFrame({
        "Transition": ["Applied → Screened", "Screened → Interviewed",
                        "Interviewed → Offered", "Offered → Hired"],
        "From": [N, n_screen, n_interview, n_offer],
        "To": [n_screen, n_interview, n_offer, n_hire],
        "Converted %": [f"{cr_screen:.1f}%", f"{cr_interview:.1f}%",
                         f"{cr_offer:.1f}%", f"{cr_hire:.1f}%"],
        "Dropped": [drop_screen, drop_interview, drop_offer, drop_hire],
    })
    st.dataframe(conv_df, use_container_width=True, hide_index=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 3 — TIME
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

with t_time:
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("<div class='sec-label'>Avg Days per Stage</div>", unsafe_allow_html=True)
        slowest = max(avg_t, key=avg_t.get)
        bar_colors = [C["red"] if k == slowest else C["blue"] for k in avg_t]
        fig = go.Figure(go.Bar(
            x=list(avg_t.keys()), y=[round(v, 1) for v in avg_t.values()],
            text=[f"<b>{v:.1f}</b> days" for v in avg_t.values()],
            textposition="outside", marker_color=bar_colors,
            textfont=dict(size=11),
        ))
        styled(fig, h=380, yaxis_title="Avg Days",
               title=dict(text=f"⚠ Slowest: {slowest} ({avg_t[slowest]:.1f}d)",
                          font=dict(size=13, color=C["red"], family="Inter, sans-serif")))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("<div class='sec-label'>Time-to-Hire Distribution</div>", unsafe_allow_html=True)
        tth_data = df.loc[df["hired"], "time_to_hire"].dropna()
        if not tth_data.empty:
            fig = go.Figure(go.Histogram(
                x=tth_data, nbinsx=20,
                marker_color=C["blue"], marker_line=dict(color="#FFFFFF", width=0.5),
                hovertemplate="Days: %{x}<br>Candidates: %{y}<extra></extra>",
            ))
            fig.add_vline(x=avg_tth, line_dash="dash", line_color=C["red"], line_width=2,
                          annotation_text=f"  Avg: {avg_tth:.0f}d", annotation_position="top left",
                          annotation_font=dict(color=C["red"], size=12, family="Inter, sans-serif"),
                          annotation_bgcolor="rgba(255,255,255,0.85)")
            styled(fig, h=380, xaxis_title="Days to Hire", yaxis_title="Candidates")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hire data for current filters.")

    # Heatmap: time × job role
    st.markdown("<div class='sec-label'>Avg Days per Stage × Job Role</div>", unsafe_allow_html=True)
    heat = df.groupby("job_role").agg(
        s=("time_to_screen", "mean"), i=("time_to_interview", "mean"),
        o=("time_to_offer", "mean"), h=("time_to_hire_from_offer", "mean"),
    ).round(1)
    heat.columns = list(avg_t.keys())
    z_vals = heat.values
    z_flat = z_vals.flatten()
    z_min, z_max = (np.nanmin(z_flat), np.nanmax(z_flat)) if len(z_flat) else (0, 1)
    z_mid = (z_min + z_max) / 2
    text_colors = [["#FFFFFF" if (v >= z_mid or pd.isna(v)) else "#1E293B" for v in row] for row in z_vals]

    fig = go.Figure(go.Heatmap(
        z=z_vals, x=heat.columns.tolist(), y=heat.index.tolist(),
        text=z_vals, texttemplate="%{text:.1f}d",
        textfont=dict(size=12),
        colorscale=[[0, "#DBEAFE"], [0.5, "#3B82F6"], [1, "#991B1B"]],
        colorbar=dict(title=dict(text="Days", font=dict(color="#1E293B"))),
    ))
    for i, row in enumerate(text_colors):
        for j, tc in enumerate(row):
            fig.add_annotation(
                x=heat.columns[j], y=heat.index[i],
                text=f"{z_vals[i][j]:.1f}d" if pd.notna(z_vals[i][j]) else "",
                showarrow=False, font=dict(color=tc, size=12),
            )
    fig.update_traces(texttemplate="")
    styled(fig, h=300)
    st.plotly_chart(fig, use_container_width=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 4 — PERFORMANCE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

with t_perf:

    # ── Source efficiency ──
    st.markdown("<div class='sec-label'>Efficiency Score by Source</div>", unsafe_allow_html=True)
    src_e = df.groupby("source").agg(
        n=("candidate_id", "count"), h=("hired", "sum"),
        o=("offered", "sum"), tth=("time_to_hire", "mean"),
    ).reset_index()
    src_e["cr"] = np.where(src_e["n"] > 0, src_e["h"] / src_e["n"] * 100, 0)
    src_e["oar"] = np.where(src_e["o"] > 0, src_e["h"] / src_e["o"] * 100, 0)
    raw_s = [efficiency(r["cr"], r["oar"], r["tth"]) for _, r in src_e.iterrows()]
    mx = max(raw_s) if raw_s and max(raw_s) > 0 else 1
    src_e["eff"] = [round(s / mx * 100, 1) for s in raw_s]
    src_e = src_e.sort_values("eff", ascending=True)

    fig = go.Figure(go.Bar(
        y=src_e["source"], x=src_e["eff"], orientation="h",
        text=[f"<b>{v}</b>" for v in src_e["eff"]], textposition="outside",
        marker_color=[C["green"] if v >= 60 else C["amber"] if v >= 30 else C["red"] for v in src_e["eff"]],
        textfont=dict(size=12, color="#FFFFFF"),
    ))
    styled(fig, h=260, xaxis_title="Efficiency Score (0–100)", xaxis_range=[0, 120])
    st.plotly_chart(fig, use_container_width=True)

    # ── Recruiter table ──
    st.markdown("<div class='sec-label'>Recruiter Scorecard</div>", unsafe_allow_html=True)
    rec = df.groupby("recruiter").agg(
        Applicants=("candidate_id", "count"), Screened=("screened", "sum"),
        Interviewed=("interviewed", "sum"), Offered=("offered", "sum"),
        Hired=("hired", "sum"), TTH=("time_to_hire", "mean"),
    ).reset_index()
    rec["Conv %"] = (rec["Hired"] / rec["Applicants"] * 100).round(1)
    rec["Offer Accept %"] = np.where(rec["Offered"] > 0, (rec["Hired"] / rec["Offered"] * 100).round(1), 0)
    rec["TTH"] = rec["TTH"].round(1)
    raw_r = [efficiency(r["Conv %"], r["Offer Accept %"], r["TTH"]) for _, r in rec.iterrows()]
    mx_r = max(raw_r) if raw_r and max(raw_r) > 0 else 1
    rec["Efficiency"] = [round(s / mx_r * 100, 1) for s in raw_r]
    rec = rec.sort_values("Efficiency", ascending=False)

    show = rec[["recruiter", "Applicants", "Hired", "Conv %", "TTH", "Offer Accept %", "Efficiency"]].copy()
    show.columns = ["Recruiter", "Applicants", "Hires", "Conv %", "Avg TTH (d)", "Offer Accept %", "Efficiency"]
    show["Hires"] = show["Hires"].astype(int)
    show["Applicants"] = show["Applicants"].astype(int)

    def _color_eff(v):
        if v >= 70: return "background-color:#D1FAE5;color:#065F46"
        if v >= 40: return "background-color:#FEF3C7;color:#854D0E"
        return "background-color:#FEE2E2;color:#991B1B"

    def _color_conv(v):
        if v >= 20: return "background-color:#D1FAE5;color:#065F46"
        if v >= 12: return "background-color:#FEF3C7;color:#854D0E"
        return "background-color:#FEE2E2;color:#991B1B"

    def _color_tth(v):
        if pd.isna(v): return ""
        if v <= 16: return "background-color:#D1FAE5;color:#065F46"
        if v <= 22: return "background-color:#FEF3C7;color:#854D0E"
        return "background-color:#FEE2E2;color:#991B1B"

    st.dataframe(
        show.style
            .map(_color_eff, subset=["Efficiency"])
            .map(_color_conv, subset=["Conv %"])
            .map(_color_tth, subset=["Avg TTH (d)"])
            .format({"Conv %": "{:.1f}", "Avg TTH (d)": "{:.1f}",
                      "Offer Accept %": "{:.1f}", "Efficiency": "{:.1f}"}),
        use_container_width=True, height=280, hide_index=True,
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 5 — IMPACT  (Hero Tab)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

with t_impact:
    st.markdown(f"""
    <div class='hero-card'>
        <div class='hero-emoji'>🚀</div>
        <div class='hero-value'>+{extra_hires} hires</div>
        <div class='hero-label'>if <b>{worst_stage}</b> conversion improves by +10%</div>
        <div class='hero-sub'>Current {worst_stage} conversion: {worst_cr:.1f}% → Simulated: {min(100, worst_cr+10):.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([1, 1])

    with c1:
        st.markdown("<div class='sec-label'>Current vs Improved Hires</div>", unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=["Current", "After +10% Fix"],
            y=[n_hire, n_hire + extra_hires],
            text=[f"<b>{n_hire}</b>", f"<b>{n_hire + extra_hires}</b>  (+{extra_hires})"],
            textposition="outside",
            marker_color=[C["blue"], C["green"]],
            textfont=dict(size=13),
            width=0.45,
        ))
        styled(fig, h=340, yaxis_title="Hires",
               yaxis_range=[0, (n_hire + extra_hires) * 1.25])
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("<div class='sec-label'>Stage Conversion: Current vs Simulated</div>", unsafe_allow_html=True)
        stage_labels = ["Screening", "Interview", "Offer", "Hire"]
        simulated_crs = list(cr_list)
        simulated_crs[idx_map[worst_stage]] = min(100, simulated_crs[idx_map[worst_stage]] + 10)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Current", x=stage_labels, y=[round(v, 1) for v in cr_list],
            marker_color="#93C5FD", text=[f"{v:.1f}%" for v in cr_list], textposition="outside",
            textfont=dict(color="#1E3A5F", size=11),
        ))
        fig.add_trace(go.Bar(
            name="Simulated", x=stage_labels, y=[round(v, 1) for v in simulated_crs],
            marker_color=C["green"], text=[f"{v:.1f}%" for v in simulated_crs], textposition="outside",
            textfont=dict(color="#065F46", size=11),
        ))
        styled(fig, h=340, barmode="group", yaxis_title="Conversion %",
               legend=dict(orientation="h", y=1.08, x=0.5, xanchor="center"))
        st.plotly_chart(fig, use_container_width=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 6 — INSIGHTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

with t_insights:
    st.markdown("<div class='sec-label'>Auto-Generated Decision Insights</div>", unsafe_allow_html=True)

    bullets = []

    # 1. worst drop-off
    drop_pcts = {
        "Screening": drop_screen / N * 100 if N else 0,
        "Interview": drop_interview / n_screen * 100 if n_screen else 0,
        "Offer": drop_offer / n_interview * 100 if n_interview else 0,
        "Hire": drop_hire / n_offer * 100 if n_offer else 0,
    }
    worst_drop = max(drop_pcts, key=drop_pcts.get)
    bullets.append((
        f"⚠️ <b>{worst_drop}</b> stage has the highest drop-off — "
        f"<b>{drop_pcts[worst_drop]:.0f}%</b> of candidates are lost here. This is the #1 bottleneck.",
        "red",
    ))

    # 2. leakage opportunity
    bullets.append((
        f"🎯 Improving <b>{worst_stage}</b> conversion by +10% yields <b>+{extra_hires} additional hires</b> — "
        f"the single highest-leverage fix available.",
        "red",
    ))

    # 3. best source
    src_cr = df.groupby("source").agg(n=("candidate_id", "count"), h=("hired", "sum")).reset_index()
    src_cr["cr"] = (src_cr["h"] / src_cr["n"] * 100).round(1)
    if len(src_cr) >= 2:
        best = src_cr.loc[src_cr["cr"].idxmax()]
        worst = src_cr.loc[src_cr["cr"].idxmin()]
        ratio = best["cr"] / worst["cr"] if worst["cr"] > 0 else 0
        bullets.append((
            f"🏆 <b>{best['source']}</b> converts at <b>{best['cr']}%</b>"
            + (f" — <b>{ratio:.1f}x</b> better than {worst['source']} ({worst['cr']}%)" if ratio else "")
            + ". Invest more here.",
            "green",
        ))

    # 4. slowest role
    role_tth = df[df["hired"]].groupby("job_role")["time_to_hire"].mean().round(1)
    if not role_tth.empty:
        sr = role_tth.idxmax()
        bullets.append((
            f"🐢 <b>{sr}</b> roles take the longest to hire — <b>{role_tth[sr]:.0f} days</b> avg. "
            f"Investigate process delays for this role.",
            "red",
        ))

    # 5. best / worst recruiter
    if not rec.empty:
        best_r = rec.iloc[0]
        bullets.append((
            f"🌟 <b>{best_r['recruiter']}</b> has the highest efficiency score (<b>{best_r['Efficiency']}</b>) — "
            f"Conv: {best_r['Conv %']}%, TTH: {best_r['TTH']}d.",
            "green",
        ))
        if len(rec) > 1:
            worst_r = rec.iloc[-1]
            bullets.append((
                f"🔻 <b>{worst_r['recruiter']}</b> has the lowest efficiency (<b>{worst_r['Efficiency']}</b>) — "
                f"may need coaching or workload redistribution.",
                "red",
            ))

    # 6. overall health
    if cr_overall >= 15:
        bullets.append((f"✅ Overall conversion at <b>{cr_overall:.1f}%</b> is strong. Focus on scaling volume.", "green"))
    elif cr_overall >= 8:
        bullets.append((f"📊 Overall conversion at <b>{cr_overall:.1f}%</b> is moderate. Targeted fixes can drive big gains.", "blue"))
    else:
        bullets.append((f"🚨 Overall conversion at <b>{cr_overall:.1f}%</b> is low. Urgent funnel optimization needed.", "red"))

    c1, c2 = st.columns(2)
    mid = (len(bullets) + 1) // 2
    with c1:
        for text, var in bullets[:mid]:
            st.markdown(f"<div class='ins ins-{var}'>{text}</div>", unsafe_allow_html=True)
    with c2:
        for text, var in bullets[mid:]:
            st.markdown(f"<div class='ins ins-{var}'>{text}</div>", unsafe_allow_html=True)

# ─── Footer ───────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#94A3B8;font-size:0.75rem;padding:4px 0;'>"
    "Hiring Funnel Dashboard  •  Decision Intelligence for Leadership</div>",
    unsafe_allow_html=True,
)
