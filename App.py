import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os

# =============================================================
# PAGE CONFIG (doit etre en premier)
# =============================================================
st.set_page_config(
    page_title="Famille Faure - Tracker",
    page_icon="https://cdn-icons-png.flaticon.com/512/2830/2830284.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================
# CONFIG
# =============================================================
DATA_FILE = "portfolio_data.json"
ALERTS_FILE = "alerts_data.json"
PASS = "Faure2026!"
BENCH_TICKER = "^FCHI"
BENCH_NAME = "CAC 40"
FAMILY = ["Patrick", "Nicolas", "Guillaume", "Florian"]

NAME_TO_TICKER = {
    "CAPGEMINI": "CAP.PA", "ALSTOM": "ALO.PA",
    "DASSAULT SYSTEMES": "DSY.PA", "ENGIE": "ENGI.PA",
    "RENAULT": "RNO.PA", "STELLANTIS": "STLAP.PA", "STELLANTIS NV": "STLAP.PA",
    "AIR LIQUIDE": "AI.PA", "TOTALENERGIES": "TTE.PA", "TOTAL": "TTE.PA",
    "BNP PARIBAS": "BNP.PA", "LVMH": "MC.PA",
    "L'OREAL": "OR.PA", "L OREAL": "OR.PA", "LOREAL": "OR.PA",
    "HERMES": "RMS.PA", "HERMES INTERNATIONAL": "RMS.PA",
    "ORANGE": "ORA.PA", "SCHNEIDER": "SU.PA", "SCHNEIDER ELECTRIC": "SU.PA",
    "AXA": "CS.PA", "VINCI": "DG.PA", "SANOFI": "SAN.PA",
    "SAFRAN": "SAF.PA", "SAINT-GOBAIN": "SGO.PA", "SAINT GOBAIN": "SGO.PA",
    "SOCIETE GENERALE": "GLE.PA", "CREDIT AGRICOLE": "ACA.PA",
    "DANONE": "BN.PA", "PERNOD RICARD": "RI.PA", "MICHELIN": "ML.PA",
    "KERING": "KER.PA", "BOUYGUES": "EN.PA", "CHRISTIAN DIOR": "CDI.PA",
    "VEOLIA": "VIE.PA", "LEGRAND": "LR.PA", "THALES": "HO.PA",
    "PUBLICIS": "PUB.PA", "ARKEMA": "AKE.PA",
    "TELEPERFORMANCE": "TEP.PA", "EUROFINS": "ERF.PA",
    "STMICROELECTRONICS": "STM.PA", "WORLDLINE": "WLN.PA",
    "CARREFOUR": "CA.PA", "ACCOR": "AC.PA", "VIVENDI": "VIV.PA",
    "EDENRED": "EDEN.PA", "ESSILOR": "EL.PA", "ESSILORLUXOTTICA": "EL.PA",
    "AIRBUS": "AIR.PA", "VALEO": "FR.PA", "NEXITY": "NXI.PA",
    "EIFFAGE": "FGR.PA", "AMUNDI": "AMUN.PA", "RUBIS": "RUI.PA",
    "NEXANS": "NEX.PA", "IPSEN": "IPN.PA", "BIOMERIEUX": "BIM.PA",
    "BUREAU VERITAS": "BVI.PA", "SODEXO": "SW.PA",
    "DASSAULT AVIATION": "AM.PA", "SCOR": "SCR.PA",
    "REMY COINTREAU": "RCO.PA", "FAURECIA": "EO.PA", "FORVIA": "FRVIA.PA",
    "UNIBAIL": "URW.PA", "GECINA": "GFC.PA", "COVIVIO": "COV.PA",
}

# =============================================================
# CSS PRO
# =============================================================
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] {font-family: 'Inter', sans-serif;}

/* Sidebar */
section[data-testid="stSidebar"] {background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);}
section[data-testid="stSidebar"] * {color: #e2e8f0 !important;}
section[data-testid="stSidebar"] hr {border-color: rgba(148,163,184,0.2) !important;}
section[data-testid="stSidebar"] .stSelectbox label {color: #94a3b8 !important; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em;}
section[data-testid="stSidebar"] .stRadio label {font-size: 0.85rem;}

/* KPI Cards */
.kpi-row {display:flex; gap:12px; margin-bottom:1.5rem; flex-wrap: wrap;}
.kpi {flex:1; min-width:160px; border-radius:16px; padding:20px 16px; color:#fff; position:relative; overflow:hidden;}
.kpi::before {content:''; position:absolute; top:-30px; right:-30px; width:80px; height:80px; border-radius:50%; background:rgba(255,255,255,0.1);}
.kpi .label {font-size:0.7rem; font-weight:500; text-transform:uppercase; letter-spacing:0.08em; opacity:0.85; margin-bottom:6px;}
.kpi .value {font-size:1.55rem; font-weight:700; line-height:1.2;}
.kpi .sub {font-size:0.75rem; opacity:0.7; margin-top:4px;}
.kpi-blue {background: linear-gradient(135deg, #3b82f6, #6366f1);}
.kpi-green {background: linear-gradient(135deg, #10b981, #059669);}
.kpi-red {background: linear-gradient(135deg, #ef4444, #dc2626);}
.kpi-orange {background: linear-gradient(135deg, #f59e0b, #d97706);}
.kpi-purple {background: linear-gradient(135deg, #8b5cf6, #7c3aed);}
.kpi-teal {background: linear-gradient(135deg, #14b8a6, #0d9488);}

/* Section headers */
.sec {font-size:1.15rem; font-weight:600; color:#1e293b; margin:2rem 0 1rem; padding-bottom:8px;
    border-bottom:2px solid #6366f1; display:flex; align-items:center; gap:8px;}
.sec-icon {font-size:1.2rem;}

/* Page header */
.page-header {margin-bottom:0.5rem;}
.page-header h1 {font-size:1.8rem; font-weight:700; color:#0f172a; margin:0;}
.page-header p {font-size:0.9rem; color:#64748b; margin:4px 0 0;}
.header-line {height:3px; background:linear-gradient(90deg, #6366f1, #3b82f6, #06b6d4); border-radius:2px; margin:12px 0 24px;}

/* Tables */
.stDataFrame {border-radius: 12px; overflow: hidden;}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>""", unsafe_allow_html=True)


def kpi_card(label, value, sub="", style="kpi-blue"):
    sub_html = f'<div class="sub">{sub}</div>' if sub else ""
    return f'<div class="kpi {style}"><div class="label">{label}</div><div class="value">{value}</div>{sub_html}</div>'


def page_hdr(title, subtitle=""):
    st.markdown(f'<div class="page-header"><h1>{title}</h1><p>{subtitle}</p></div><div class="header-line"></div>', unsafe_allow_html=True)


def section(title):
    st.markdown(f'<div class="sec">{title}</div>', unsafe_allow_html=True)


# =============================================================
# PERSISTENCE
# =============================================================
def load_pf():
    if os.path.exists(DATA_FILE):
        d = json.load(open(DATA_FILE))
        for m in FAMILY:
            if m not in d: d[m] = {}
        return d
    return {m: {} for m in FAMILY}


def save_pf(d):
    json.dump(d, open(DATA_FILE, "w"), indent=2)


def load_al():
    return json.load(open(ALERTS_FILE)) if os.path.exists(ALERTS_FILE) else []


def save_al(a):
    json.dump(a, open(ALERTS_FILE, "w"), indent=2)


def find_tk(name):
    up = name.upper().strip()
    if up in NAME_TO_TICKER: return NAME_TO_TICKER[up]
    for k, v in NAME_TO_TICKER.items():
        if k in up or up in k: return v
    return up.replace(" ", "-") + ".PA"


# =============================================================
# YAHOO FINANCE
# =============================================================
@st.cache_data(ttl=300)
def yf_prices(tickers):
    p = {}
    tl = [t for t in tickers if t]
    if not tl: return p
    try:
        d = yf.download(tl, period="5d", group_by="ticker", progress=False)
        for t in tl:
            try:
                p[t] = float(d["Close"].dropna().iloc[-1]) if len(tl) == 1 else float(d[t]["Close"].dropna().iloc[-1])
            except: p[t] = 0.0
    except:
        for t in tl: p[t] = 0.0
    return p


@st.cache_data(ttl=3600)
def yf_info(tickers):
    r = {}
    for t in tickers:
        try:
            i = yf.Ticker(t).info
            r[t] = {k: i.get(v) for k, v in {
                "sector": "sector", "industry": "industry", "pe": "trailingPE",
                "pe_fwd": "forwardPE", "dy": "dividendYield", "beta": "beta",
                "mcap": "marketCap", "h52": "fiftyTwoWeekHigh", "l52": "fiftyTwoWeekLow",
                "target": "targetMeanPrice", "reco": "recommendationKey",
                "roe": "returnOnEquity", "margin": "profitMargins",
                "rev_g": "revenueGrowth", "debt": "debtToEquity"}.items()}
            r[t]["sector"] = r[t].get("sector") or "N/A"
            r[t]["reco"] = r[t].get("reco") or "N/A"
        except: r[t] = {"sector": "N/A", "reco": "N/A"}
    return r


@st.cache_data(ttl=600)
def yf_hist(tickers, start):
    try: return yf.download(list(tickers), start=start, progress=False, group_by="ticker")
    except: return pd.DataFrame()


@st.cache_data(ttl=600)
def yf_bench(start):
    try:
        d = yf.download(BENCH_TICKER, start=start, progress=False)
        return d["Close"].squeeze()
    except: return pd.Series()


def pf_value(pf, start):
    tks = list(pf.keys())
    if not tks: return pd.Series()
    h = yf_hist(tuple(tks), start)
    if h.empty: return pd.Series()
    v = pd.Series(0.0, index=h.index)
    for tk, inf in pf.items():
        try:
            c = h["Close"].squeeze() if len(tks) == 1 else h[tk]["Close"].squeeze()
            c = c.ffill(); bd = pd.Timestamp(inf["buy_date"])
            c[c.index < bd] = inf["buy_price"]; v += c * inf["qty"]
        except: pass
    return v


def pf_inv(pf, idx):
    inv = pd.Series(0.0, index=idx)
    for tk, inf in pf.items():
        inv[idx >= pd.Timestamp(inf["buy_date"])] += inf["buy_price"] * inf["qty"]
    return inv


def fmt(v):
    if v is None: return "N/A"
    if abs(v) >= 1e9: return f"{v/1e9:.1f} Mds"
    if abs(v) >= 1e6: return f"{v/1e6:.1f}M"
    return f"{v:,.0f}"


def color_pnl(v):
    return "kpi-green" if v >= 0 else "kpi-red"


PLOTLY_LAYOUT = dict(
    font=dict(family="Inter, sans-serif"),
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(t=30, b=30, l=20, r=20),
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
)

COLORS = ["#6366f1", "#3b82f6", "#06b6d4", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"]


# =============================================================
# LOGIN
# =============================================================
if "logged" not in st.session_state: st.session_state.logged = False
if "pf" not in st.session_state: st.session_state.pf = load_pf()

if not st.session_state.logged:
    st.markdown("""<div style="display:flex; justify-content:center; align-items:center; min-height:80vh;">
    <div style="text-align:center; max-width:400px;">
    <div style="font-size:3rem; margin-bottom:8px;">FAMILLE FAURE</div>
    <div style="font-size:1rem; color:#64748b; margin-bottom:2rem;">Tracker Portefeuilles</div>
    </div></div>""", unsafe_allow_html=True)
    _, cc, _ = st.columns([1.5, 1, 1.5])
    with cc:
        pw = st.text_input("Mot de passe", type="password", label_visibility="collapsed", placeholder="Mot de passe")
        if st.button("Connexion", type="primary", use_container_width=True):
            if pw == PASS: st.session_state.logged = True; st.rerun()
            else: st.error("Mot de passe incorrect")
    st.stop()


# =============================================================
# SIDEBAR GLOBALE
# =============================================================
PF = st.session_state.pf

with st.sidebar:
    st.markdown("### FAMILLE FAURE")
    st.caption("Tracker Portefeuilles")
    st.divider()
    G_MBR = st.selectbox("MEMBRE", ["Consolide"] + FAMILY, label_visibility="visible")
    st.divider()
    page = st.radio("NAVIGATION", [
        "Dashboard", "Analyse fondamentale", "Performance",
        "Alertes", "Recommandations", "Gestion"])
    st.divider()
    nb = sum(len(p) for p in PF.values())
    st.caption(f"{len(FAMILY)} membres  |  {nb} positions")
    st.caption(datetime.now().strftime("%d/%m/%Y  %H:%M"))
    st.divider()
    if st.button("Actualiser", use_container_width=True): st.cache_data.clear(); st.rerun()
    if st.button("Deconnexion", use_container_width=True): st.session_state.logged = False; st.rerun()


def get_pf():
    if G_MBR == "Consolide":
        c = {}
        for m in FAMILY:
            for tk, inf in PF.get(m, {}).items():
                if tk not in c:
                    c[tk] = {"qty": 0, "tc": 0, "bd": inf["buy_date"], "name": inf["name"]}
                c[tk]["qty"] += inf["qty"]
                c[tk]["tc"] += inf["buy_price"] * inf["qty"]
                c[tk]["bd"] = min(c[tk]["bd"], inf["buy_date"])
        return {t: {"qty": v["qty"], "buy_price": v["tc"]/v["qty"],
                     "buy_date": v["bd"], "name": v["name"]} for t, v in c.items()}
    return PF.get(G_MBR, {})


# =============================================================
# PAGE 1 : DASHBOARD
# =============================================================
if page == "Dashboard":
    page_hdr("Dashboard", f"Vue d'ensemble - {G_MBR}")
    portfolio = get_pf()
    if not portfolio: st.info("Aucune position. Importe un fichier dans Gestion."); st.stop()

    tks = list(portfolio.keys())
    with st.spinner("Chargement des cours..."):
        prices = yf_prices(tuple(tks)); fundas = yf_info(tuple(tks))

    rows = []
    ti = tv = td = 0
    for tk, inf in portfolio.items():
        cur = prices.get(tk, 0); val = cur * inf["qty"]; inv = inf["buy_price"] * inf["qty"]
        pnl = val - inv; pct = (pnl / inv * 100) if inv else 0
        f = fundas.get(tk, {}); dy = f.get("dy"); target = f.get("target")
        td += (val * dy) if dy else 0
        rdt_esp = ((target - cur) / cur * 100) if target and cur > 0 else None
        rows.append({
            "Valeur": inf["name"], "Ticker": tk, "Secteur": f.get("sector", "N/A"),
            "Qte": inf["qty"], "PRU": round(inf["buy_price"], 2), "Cours": round(cur, 2),
            "Valorisation": round(val, 0), "PnL (EUR)": round(pnl, 0), "PnL (%)": round(pct, 1),
            "Rdt espere (%)": round(rdt_esp, 1) if rdt_esp else None,
            "PE": round(f["pe"], 1) if f.get("pe") else None,
            "Div (%)": round(dy * 100, 1) if dy else None,
            "Beta": round(f["beta"], 2) if f.get("beta") else None,
        })
        ti += inv; tv += val

    tp = tv - ti; tpct = (tp / ti * 100) if ti else 0
    re_v = [(r["Rdt espere (%)"], r["Valorisation"]) for r in rows if r["Rdt espere (%)"] is not None]
    rdt_g = sum(r * w for r, w in re_v) / sum(w for _, w in re_v) if re_v else 0

    # KPIs
    st.markdown(f"""<div class="kpi-row">
        {kpi_card("VALORISATION", f"{tv:,.0f} EUR", f"{len(portfolio)} positions", "kpi-blue")}
        {kpi_card("INVESTI", f"{ti:,.0f} EUR", "", "kpi-purple")}
        {kpi_card("PLUS-VALUE", f"{tp:+,.0f} EUR", f"{tpct:+.1f}%", color_pnl(tp))}
        {kpi_card("RDT ESPERE", f"{rdt_g:+.1f}%", "Consensus analystes", "kpi-teal")}
        {kpi_card("DIVIDENDES/AN", f"{td:,.0f} EUR", f"Rdt {(td/tv*100):.1f}%" if tv else "", "kpi-orange")}
    </div>""", unsafe_allow_html=True)

    # Table
    section("Positions")
    df = pd.DataFrame(rows).sort_values("Valorisation", ascending=False)
    st.dataframe(df, hide_index=True, height=min(800, 45 + len(df) * 35))

    # Charts
    c1, c2 = st.columns(2)
    with c1:
        section("Par valeur")
        f1 = px.pie(df, values="Valorisation", names="Valeur", hole=0.5, color_discrete_sequence=COLORS)
        f1.update_traces(textposition="inside", textinfo="percent+label", textfont_size=11)
        f1.update_layout(**PLOTLY_LAYOUT, showlegend=False, height=380)
        st.plotly_chart(f1, use_container_width=True)
    with c2:
        section("Par secteur")
        ds = df.groupby("Secteur")["Valorisation"].sum().reset_index()
        f2 = px.pie(ds, values="Valorisation", names="Secteur", hole=0.5, color_discrete_sequence=COLORS)
        f2.update_traces(textposition="inside", textinfo="percent+label", textfont_size=11)
        f2.update_layout(**PLOTLY_LAYOUT, showlegend=False, height=380)
        st.plotly_chart(f2, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        section("PnL par position")
        dfb = df.sort_values("PnL (%)")
        fig = go.Figure(go.Bar(
            x=dfb["PnL (%)"], y=dfb["Valeur"], orientation="h",
            marker_color=["#ef4444" if x < 0 else "#10b981" for x in dfb["PnL (%)"]],
            text=[f"{x:+.1f}%" for x in dfb["PnL (%)"]], textposition="outside",
            textfont=dict(size=11)))
        fig.update_layout(**PLOTLY_LAYOUT, height=max(350, len(dfb) * 50),
                          xaxis_title="PnL (%)", yaxis=dict(automargin=True))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        section("Rendement espere (analystes)")
        dre = df.dropna(subset=["Rdt espere (%)"]).sort_values("Rdt espere (%)")
        if not dre.empty:
            fig = go.Figure(go.Bar(
                x=dre["Rdt espere (%)"], y=dre["Valeur"], orientation="h",
                marker_color=["#ef4444" if x < 0 else "#3b82f6" for x in dre["Rdt espere (%)"]],
                text=[f"{x:+.1f}%" for x in dre["Rdt espere (%)"]], textposition="outside",
                textfont=dict(size=11)))
            fig.update_layout(**PLOTLY_LAYOUT, height=max(350, len(dre) * 50),
                              xaxis_title="Upside (%)", yaxis=dict(automargin=True))
            st.plotly_chart(fig, use_container_width=True)

    if G_MBR == "Consolide":
        section("Repartition par membre")
        mv = []
        for m in FAMILY:
            val = sum(prices.get(tk, 0) * inf["qty"] for tk, inf in PF.get(m, {}).items())
            if val > 0: mv.append({"Membre": m, "Valeur": round(val, 0)})
        if mv:
            fm = px.pie(pd.DataFrame(mv), values="Valeur", names="Membre", hole=0.5,
                         color_discrete_sequence=COLORS)
            fm.update_traces(textposition="inside", textinfo="percent+label+value")
            fm.update_layout(**PLOTLY_LAYOUT, height=400)
            st.plotly_chart(fm, use_container_width=True)


# =============================================================
# PAGE 2 : ANALYSE FONDAMENTALE
# =============================================================
elif page == "Analyse fondamentale":
    page_hdr("Analyse fondamentale", f"Donnees Yahoo Finance - {G_MBR}")
    portfolio = get_pf()
    if not portfolio: st.info("Aucune position."); st.stop()

    tks = list(portfolio.keys())
    with st.spinner("Yahoo Finance..."):
        prices = yf_prices(tuple(tks)); fundas = yf_info(tuple(tks))

    for tk, inf in portfolio.items():
        cur = prices.get(tk, 0); f = fundas.get(tk, {})
        pnl = ((cur - inf["buy_price"]) / inf["buy_price"]) * 100 if inf["buy_price"] else 0
        target = f.get("target")
        rdt_esp = ((target - cur) / cur * 100) if target and cur > 0 else None

        st.divider()
        st.markdown(f"#### {inf['name']}  `{tk}`")
        st.caption(f"{f.get('sector', 'N/A')}  |  {f.get('industry', 'N/A')}")

        c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
        c1.metric("Cours", f"{cur:.2f}")
        c2.metric("PnL", f"{pnl:+.1f}%")
        c3.metric("Rdt espere", f"{rdt_esp:+.1f}%" if rdt_esp else "N/A")
        c4.metric("P/E", f"{f['pe']:.1f}" if f.get("pe") else "N/A")
        c5.metric("Dividende", f"{f['dy']*100:.1f}%" if f.get("dy") else "N/A")
        c6.metric("Beta", f"{f['beta']:.2f}" if f.get("beta") else "N/A")
        c7.metric("Cap.", fmt(f.get("mcap")))

        c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
        c1.metric("P/E fwd", f"{f['pe_fwd']:.1f}" if f.get("pe_fwd") else "N/A")
        c2.metric("Haut 52s", f"{f['h52']:.0f}" if f.get("h52") else "N/A")
        c3.metric("Bas 52s", f"{f['l52']:.0f}" if f.get("l52") else "N/A")
        c4.metric("Objectif", f"{target:.0f}" if target else "N/A")
        c5.metric("Reco", str(f.get("reco", "N/A")).upper())
        c6.metric("ROE", f"{f['roe']*100:.1f}%" if f.get("roe") else "N/A")
        c7.metric("Marge", f"{f['margin']*100:.1f}%" if f.get("margin") else "N/A")

    st.divider()
    section("Tableau comparatif")
    comp = []
    for tk, inf in portfolio.items():
        f = fundas.get(tk, {}); cur = prices.get(tk, 0); t = f.get("target")
        comp.append({"Valeur": inf["name"], "Secteur": f.get("sector", "N/A"),
            "P/E": round(f["pe"], 1) if f.get("pe") else None,
            "P/E fwd": round(f["pe_fwd"], 1) if f.get("pe_fwd") else None,
            "Div %": round(f["dy"]*100, 1) if f.get("dy") else None,
            "Beta": round(f["beta"], 2) if f.get("beta") else None,
            "ROE %": round(f["roe"]*100, 1) if f.get("roe") else None,
            "Marge %": round(f["margin"]*100, 1) if f.get("margin") else None,
            "Reco": str(f.get("reco", "")).upper(),
            "Objectif": round(t, 0) if t else None,
            "Rdt espere %": round((t-cur)/cur*100, 1) if t and cur else None})
    st.dataframe(pd.DataFrame(comp), hide_index=True, height=min(600, 45 + len(comp)*35))

    sdf = pd.DataFrame(comp).dropna(subset=["P/E", "Div %"])
    if len(sdf) > 1:
        section("P/E vs Dividende")
        fig = px.scatter(sdf, x="P/E", y="Div %", text="Valeur", color="Secteur",
                          color_discrete_sequence=COLORS, size_max=15)
        fig.update_traces(textposition="top center", textfont_size=10)
        fig.update_layout(**PLOTLY_LAYOUT, height=450)
        st.plotly_chart(fig, use_container_width=True)


# =============================================================
# PAGE 3 : PERFORMANCE
# =============================================================
elif page == "Performance":
    page_hdr("Performance et risque", f"{G_MBR}")
    portfolio = get_pf()
    if not portfolio: st.info("Aucune position."); st.stop()

    pmap = {"1 mois": 30, "3 mois": 90, "6 mois": 180, "1 an": 365, "2 ans": 730}
    per = st.selectbox("Periode", list(pmap.keys()), index=3)
    sd = (datetime.now() - timedelta(days=pmap[per])).strftime("%Y-%m-%d")

    with st.spinner("Calcul de la performance..."):
        pf = pf_value(portfolio, sd); bench = yf_bench(sd)
    if pf.empty: st.warning("Donnees indisponibles."); st.stop()

    inv = pf_inv(portfolio, pf.index); pnl_h = pf - inv
    rets = pf.pct_change().dropna()
    vol = float(rets.std()*np.sqrt(252)*100) if len(rets) > 1 else 0
    cmax = pf.cummax(); dd = (pf-cmax)/cmax*100; mdd = float(dd.min())
    pret = float((pf.iloc[-1]/pf.iloc[0]-1)*100) if len(pf) > 1 else 0
    ann = float((1+rets.mean())**252-1) if len(rets) > 1 else 0
    sh = round((ann-.03)/(float(rets.std())*np.sqrt(252)), 2) if vol > 0 and len(rets) > 20 else 0
    sd2 = float(rets[rets < 0].std()*np.sqrt(252)) if len(rets[rets < 0]) > 5 else 0
    so = round((ann-.03)/sd2, 2) if sd2 > 0 else 0
    wr = round(int((rets > 0).sum())/max(1, int((rets != 0).sum()))*100, 1)
    var95 = float(np.percentile(rets.dropna(), 5)*float(pf.iloc[-1])) if len(rets) > 20 else 0

    # Rendement espere
    fi = yf_info(tuple(portfolio.keys())); pi = yf_prices(tuple(portfolio.keys()))
    rw = []
    for tk, inf in portfolio.items():
        cur = pi.get(tk, 0); t = fi.get(tk, {}).get("target"); val = cur*inf["qty"]
        if t and cur > 0: rw.append(((t-cur)/cur*100, val))
    rdt_esp = sum(r*w for r, w in rw)/sum(w for _, w in rw) if rw else 0

    # KPIs
    st.markdown(f"""<div class="kpi-row">
        {kpi_card("VALORISATION", f"{float(pf.iloc[-1]):,.0f} EUR", "", "kpi-blue")}
        {kpi_card("PERFORMANCE", f"{pret:+.1f}%", per, color_pnl(pret))}
        {kpi_card("RDT ANNUALISE", f"{ann*100:+.1f}%", "", color_pnl(ann))}
        {kpi_card("VOLATILITE", f"{vol:.1f}%", "annualisee", "kpi-orange")}
        {kpi_card("SHARPE", f"{sh}", "ratio", "kpi-purple")}
        {kpi_card("MAX DRAWDOWN", f"{mdd:+.1f}%", "", "kpi-red")}
        {kpi_card("RDT ESPERE", f"{rdt_esp:+.1f}%", "analystes", "kpi-teal")}
    </div>""", unsafe_allow_html=True)

    section("Indicateurs avances")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Sortino", f"{so}"); c2.metric("Win rate", f"{wr}%")
    c3.metric("VaR 95%/j", f"{var95:,.0f} EUR"); c4.metric("Positions", len(portfolio))
    c5.metric("Div. yield est.", f"{sum(w for _, w in rw)/float(pf.iloc[-1])*100:.1f}%" if rw else "N/A")

    section("Evolution de la valorisation")
    f3 = go.Figure()
    f3.add_trace(go.Scatter(x=pf.index, y=pf.values, name="Portefeuille",
        line=dict(color="#6366f1", width=2.5), fill="tozeroy", fillcolor="rgba(99,102,241,0.08)"))
    f3.add_trace(go.Scatter(x=inv.index, y=inv.values, name="Investi",
        line=dict(color="#94a3b8", width=1.5, dash="dash")))
    f3.update_layout(**PLOTLY_LAYOUT, height=450); st.plotly_chart(f3, use_container_width=True)

    section("Plus-value cumulee")
    f4 = go.Figure()
    f4.add_trace(go.Scatter(x=pnl_h.index, y=pnl_h.values, name="PnL",
        line=dict(color="#10b981", width=2), fill="tozeroy", fillcolor="rgba(16,185,129,0.08)"))
    f4.add_hline(y=0, line_dash="dash", line_color="#94a3b8")
    f4.update_layout(**PLOTLY_LAYOUT, height=350); st.plotly_chart(f4, use_container_width=True)

    section(f"Performance vs {BENCH_NAME}")
    if not bench.empty and len(pf) > 1:
        ci = pf.index.intersection(bench.index)
        if len(ci) > 1:
            pn = (pf.loc[ci]/pf.loc[ci].iloc[0])*100; bn = (bench.loc[ci]/bench.loc[ci].iloc[0])*100
            f5 = go.Figure()
            f5.add_trace(go.Scatter(x=ci, y=pn.values, name="Portefeuille", line=dict(color="#6366f1", width=2.5)))
            f5.add_trace(go.Scatter(x=ci, y=bn.values, name=BENCH_NAME, line=dict(color="#f59e0b", width=2, dash="dash")))
            f5.add_hline(y=100, line_dash="dot", line_color="#cbd5e1")
            f5.update_layout(**PLOTLY_LAYOUT, height=400, yaxis_title="Base 100")
            st.plotly_chart(f5, use_container_width=True)
            pr = float((pn.iloc[-1]/100-1)*100); br = float((bn.iloc[-1]/100-1)*100); al = pr-br
            if al > 0: st.success(f"Portefeuille {pr:+.1f}%  |  {BENCH_NAME} {br:+.1f}%  |  Alpha {al:+.1f}%")
            else: st.error(f"Portefeuille {pr:+.1f}%  |  {BENCH_NAME} {br:+.1f}%  |  Alpha {al:+.1f}%")

    c1, c2 = st.columns(2)
    with c1:
        section("Drawdown")
        f6 = go.Figure()
        f6.add_trace(go.Scatter(x=dd.index, y=dd.values, line=dict(color="#ef4444", width=1.5),
            fill="tozeroy", fillcolor="rgba(239,68,68,0.08)"))
        f6.update_layout(**PLOTLY_LAYOUT, height=300, yaxis_title="%")
        st.plotly_chart(f6, use_container_width=True)
    with c2:
        section("Distribution des rendements")
        f7 = go.Figure()
        f7.add_trace(go.Histogram(x=rets.values*100, nbinsx=50, marker_color="#6366f1", opacity=0.75))
        f7.add_vline(x=0, line_dash="dash", line_color="#ef4444")
        f7.update_layout(**PLOTLY_LAYOUT, height=300, xaxis_title="Rendement journalier (%)")
        st.plotly_chart(f7, use_container_width=True)


# =============================================================
# PAGE 4 : ALERTES
# =============================================================
elif page == "Alertes":
    page_hdr("Alertes", "Suivi des seuils et signaux")
    alerts = load_al()
    all_tk = sorted(set(tk for p in PF.values() for tk in p.keys()))
    if not all_tk: st.info("Importez des positions."); st.stop()

    section("Creer une alerte")
    c1, c2, c3, c4 = st.columns([3, 3, 2, 2])
    with c1: a_tk = st.selectbox("Ticker", all_tk)
    with c2: a_type = st.selectbox("Type", ["Prix au-dessus", "Prix en-dessous", "PnL % au-dessus", "PnL % en-dessous"])
    with c3: a_val = st.number_input("Seuil", value=0.0, step=1.0)
    with c4:
        st.write(""); st.write("")
        if st.button("Ajouter", type="primary", use_container_width=True):
            alerts.append({"ticker": a_tk, "type": a_type, "value": a_val,
                "created": datetime.now().strftime("%d/%m/%Y %H:%M")})
            save_al(alerts); st.rerun()

    section("Alertes actives")
    if not alerts: st.info("Aucune alerte configuree.")
    else:
        cp = yf_prices(tuple(set(a["ticker"] for a in alerts)))
        for i, a in enumerate(alerts):
            cur = cp.get(a["ticker"], 0); triggered = False
            if "Prix au-dessus" == a["type"] and cur > a["value"]: triggered = True
            elif "Prix en-dessous" == a["type"] and cur < a["value"]: triggered = True
            c1, c2, c3 = st.columns([6, 2, 1])
            with c1:
                status = "DECLENCHEE" if triggered else "En attente"
                st.markdown(f"**{a['ticker']}** — {a['type']} **{a['value']}**  (cours: {cur:.2f})  `{status}`")
            with c3:
                if st.button("Suppr", key=f"d{i}"): alerts.pop(i); save_al(alerts); st.rerun()
            if triggered: st.warning(f"ALERTE DECLENCHEE : {a['ticker']} = {cur:.2f}")

    section("Signaux automatiques")
    portfolio = get_pf()
    if portfolio:
        pr = yf_prices(tuple(portfolio.keys()))
        has_signal = False
        for tk, inf in portfolio.items():
            cur = pr.get(tk, 0)
            if cur == 0: continue
            pnl = ((cur - inf["buy_price"]) / inf["buy_price"]) * 100
            if pnl > 30: st.success(f"{inf['name']}: **{pnl:+.1f}%** — Envisager une prise de benefice"); has_signal = True
            elif pnl < -15: st.error(f"{inf['name']}: **{pnl:+.1f}%** — Position a surveiller"); has_signal = True
        if not has_signal: st.info("Aucun signal automatique.")


# =============================================================
# PAGE 5 : RECOMMANDATIONS
# =============================================================
elif page == "Recommandations":
    page_hdr("Recommandations", f"Analyse {G_MBR}")
    portfolio = get_pf()
    if not portfolio: st.info("Aucune position."); st.stop()

    tks = list(portfolio.keys())
    with st.spinner("Analyse en cours..."):
        prices = yf_prices(tuple(tks)); fundas = yf_info(tuple(tks))

    tv = sum(prices.get(tk, 0)*inf["qty"] for tk, inf in portfolio.items())
    pos = []
    for tk, inf in portfolio.items():
        cur = prices.get(tk, 0); f = fundas.get(tk, {}); t = f.get("target")
        pos.append({"name": inf["name"], "tk": tk, "val": cur*inf["qty"],
            "w": (cur*inf["qty"]/tv*100) if tv else 0,
            "sector": f.get("sector", "N/A"), "pe": f.get("pe"), "reco": f.get("reco", "N/A"),
            "target": t, "rdt": ((t-cur)/cur*100) if t and cur else None,
            "pnl": ((cur-inf["buy_price"])/inf["buy_price"])*100 if inf["buy_price"] else 0})
    dfp = pd.DataFrame(pos).sort_values("w", ascending=False)

    section("Consensus analystes")
    for _, r in dfp.iterrows():
        rc = str(r["reco"]).upper()
        msg = f"**{r['name']}** : {rc}"
        if r["rdt"]: msg += f"  |  Objectif: {r['target']:.0f} EUR ({r['rdt']:+.1f}%)"
        if rc in ["BUY", "STRONG_BUY"]: st.success(msg)
        elif rc in ["SELL", "STRONG_SELL"]: st.error(msg)
        else: st.info(msg)

    c1, c2 = st.columns(2)
    with c1:
        section("Concentration")
        mw = dfp["w"].max()
        if mw > 40: st.error(f"RISQUE : {dfp.iloc[0]['name']} = {mw:.1f}% du portefeuille")
        elif mw > 25: st.warning(f"Attention : {dfp.iloc[0]['name']} = {mw:.1f}%")
        else: st.success(f"Bonne diversification (max = {mw:.1f}%)")
        fig = go.Figure(go.Bar(x=dfp["w"], y=dfp["name"], orientation="h",
            marker_color="#6366f1", text=[f"{w:.1f}%" for w in dfp["w"]], textposition="outside"))
        fig.update_layout(**PLOTLY_LAYOUT, height=max(300, len(dfp)*50), yaxis=dict(automargin=True))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        section("Diversification sectorielle")
        ds = dfp.groupby("sector")["w"].sum().sort_values(ascending=False)
        ns = len(ds)
        if ns <= 2: st.error(f"Seulement {ns} secteurs — diversifiez !")
        elif ns <= 4: st.warning(f"{ns} secteurs representes")
        else: st.success(f"{ns} secteurs representes")
        figs = px.bar(x=ds.index, y=ds.values, color=ds.values,
                       color_continuous_scale="Viridis", labels={"x": "", "y": "Poids %"})
        figs.update_layout(**PLOTLY_LAYOUT, height=350, showlegend=False)
        st.plotly_chart(figs, use_container_width=True)

    section("Actions recommandees")
    recs = []
    for _, r in dfp.iterrows():
        if r["pnl"] > 50: recs.append(("warning", f"Prise de benefice sur **{r['name']}** ({r['pnl']:+.1f}%)"))
        if r["pnl"] < -20: recs.append(("error", f"Reevaluer **{r['name']}** ({r['pnl']:+.1f}%)"))
        if r["pe"] and r["pe"] > 40: recs.append(("info", f"PE eleve sur **{r['name']}** ({r['pe']:.0f}x)"))
        if r["reco"] in ["sell", "strong_sell"]: recs.append(("error", f"Signal vente sur **{r['name']}**"))
    if recs:
        for typ, msg in recs: getattr(st, typ)(msg)
    else: st.success("Portefeuille equilibre — pas d'action urgente.")

    section("Score de diversification")
    sc = 100
    if ns < 3: sc -= 30
    elif ns < 5: sc -= 15
    if mw > 40: sc -= 25
    elif mw > 30: sc -= 10
    if len(portfolio) < 4: sc -= 20
    sc = max(0, min(100, sc))
    fsc = go.Figure(go.Indicator(mode="gauge+number+delta", value=sc,
        delta={"reference": 70, "increasing": {"color": "#10b981"}, "decreasing": {"color": "#ef4444"}},
        gauge={"axis": {"range": [0, 100], "tickwidth": 1},
            "bar": {"color": "#6366f1"},
            "steps": [{"range": [0, 40], "color": "rgba(239,68,68,0.1)"},
                      {"range": [40, 70], "color": "rgba(245,158,11,0.1)"},
                      {"range": [70, 100], "color": "rgba(16,185,129,0.1)"}],
            "threshold": {"line": {"color": "#6366f1", "width": 3}, "thickness": 0.8, "value": 70}}))
    fsc.update_layout(**PLOTLY_LAYOUT, height=280)
    st.plotly_chart(fsc, use_container_width=True)


# =============================================================
# PAGE 6 : GESTION
# =============================================================
elif page == "Gestion":
    page_hdr("Gestion des donnees", "Import, export et modification des positions")

    tab1, tab2, tab3 = st.tabs(["Ajouter une position", "Importer Excel/CSV", "Exporter"])

    with tab1:
        c1, c2, c3 = st.columns(3)
        with c1: am = st.selectbox("Membre", FAMILY, key="am")
        with c2: atk = st.text_input("Ticker Yahoo (ex: TTE.PA)", key="atk").upper()
        with c3: an = st.text_input("Nom de la valeur", key="an")
        c4, c5, c6 = st.columns(3)
        with c4: aq = st.number_input("Quantite", min_value=1, value=10, key="aq")
        with c5: ap = st.number_input("Prix d'achat (EUR)", min_value=0.01, value=100.0, step=0.01, key="ap")
        with c6: ad = st.date_input("Date d'achat", key="ad")
        if st.button("Ajouter la position", type="primary"):
            if am and atk and an:
                if am not in PF: PF[am] = {}
                PF[am][atk] = {"qty": int(aq), "buy_price": float(ap),
                    "buy_date": ad.strftime("%Y-%m-%d"), "name": an}
                st.session_state.pf = PF; save_pf(PF)
                st.success(f"{an} ({atk}) ajoute pour {am}"); st.rerun()
            else: st.error("Remplis tous les champs.")

    with tab2:
        st.markdown("**Format courtier** : Valeur | Code | Place | Date | Qte | P.R.U. | Cours | Valorisation")
        imp_m = st.selectbox("Attribuer a :", FAMILY, key="im")
        uploaded = st.file_uploader("Fichier Excel ou CSV", type=["csv", "xlsx", "xls"], key="up")
        if uploaded is not None:
            try:
                idf = pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded)
                idf = idf.dropna(how="all")
                idf = idf[idf.iloc[:, 0].notna()]
                idf = idf[idf.iloc[:, 0].astype(str).str.strip() != ""]
                idf = idf[idf.iloc[:, 0].astype(str) != "None"]
                idf = idf[~idf.iloc[:, 0].astype(str).str.upper().str.contains("LIQUIDIT")]
                idf = idf[pd.to_numeric(idf.iloc[:, 4], errors="coerce") > 0]
                st.dataframe(idf, hide_index=True)
                st.session_state["idata"] = idf.to_dict()
                st.session_state["imem"] = imp_m
            except Exception as e: st.error(f"Erreur : {e}")

        if "idata" in st.session_state:
            mode = st.radio("Mode", ["Ajouter aux existantes", "Remplacer les positions du membre"])
            if st.button("CONFIRMER L'IMPORT", type="primary"):
                idf = pd.DataFrame(st.session_state["idata"])
                im = st.session_state.get("imem", FAMILY[0])
                if im not in PF: PF[im] = {}
                if "Remplacer" in mode: PF[im] = {}
                ct = er = 0
                for _, row in idf.iterrows():
                    try:
                        nm = str(row.iloc[0]).strip()
                        qt = int(float(row.iloc[4])); pru = float(row.iloc[5])
                        dv = row.iloc[3]
                        dt = dv.strftime("%Y-%m-%d") if isinstance(dv, pd.Timestamp) else str(dv)[:10]
                        if qt <= 0 or pru <= 0: continue
                        PF[im][find_tk(nm)] = {"qty": qt, "buy_price": pru, "buy_date": dt, "name": nm}
                        ct += 1
                    except: er += 1
                st.session_state.pf = PF; save_pf(PF)
                if "idata" in st.session_state: del st.session_state["idata"]
                st.success(f"{ct} positions importees pour {im}"); st.rerun()

    with tab3:
        if st.button("Generer l'export"):
            rows = []
            for m in FAMILY:
                for tk, inf in PF.get(m, {}).items():
                    rows.append({"Membre": m, "Ticker": tk, "Nom": inf["name"],
                        "Quantite": inf["qty"], "Prix achat": inf["buy_price"], "Date": inf["buy_date"]})
            edf = pd.DataFrame(rows)
            st.download_button("Telecharger CSV", edf.to_csv(index=False), "faure_portfolios.csv", "text/csv")
            st.dataframe(edf, hide_index=True)

    st.divider()
    section("Supprimer une position")
    c1, c2, c3 = st.columns([2, 4, 2])
    with c1: dm = st.selectbox("Membre", FAMILY, key="dm")
    if PF.get(dm):
        with c2:
            opts = [f"{tk} — {inf['name']}" for tk, inf in PF[dm].items()]
            dp = st.selectbox("Position", opts, key="dp")
        with c3:
            st.write(""); st.write("")
            if st.button("Supprimer", type="secondary", use_container_width=True):
                del PF[dm][dp.split(" — ")[0]]
                st.session_state.pf = PF; save_pf(PF); st.success("Supprime"); st.rerun()
    else: st.info(f"Aucune position pour {dm}.")
