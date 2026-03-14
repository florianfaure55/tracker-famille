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
# CONFIG
# =============================================================
DATA_FILE = "portfolio_data.json"
ALERTS_FILE = "alerts_data.json"
PASS = "Faure2026!"
BENCH_TICKER = "^FCHI"
BENCH_NAME = "CAC 40"
FAMILY_MEMBERS = ["Patrick", "Nicolas", "Guillaume", "Florian"]

# Mapping noms francais -> tickers Yahoo Finance
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
    "EDENRED": "EDEN.PA", "ESSILORLUXOTTICA": "EL.PA",
    "ESSILOR": "EL.PA", "AIRBUS": "AIR.PA",
    "PEUGEOT": "STLAP.PA", "UNIBAIL": "URW.PA",
    "UNIBAIL-RODAMCO": "URW.PA", "VALEO": "FR.PA",
    "NEXITY": "NXI.PA", "EIFFAGE": "FGR.PA", "AMUNDI": "AMUN.PA",
    "GECINA": "GFC.PA", "KLEPIERRE": "LI.PA", "COVIVIO": "COV.PA",
    "RUBIS": "RUI.PA", "NEXANS": "NEX.PA", "IPSEN": "IPN.PA",
    "BIOMERIEUX": "BIM.PA", "SARTORIUS STEDIM": "DIM.PA",
    "ORPEA": "ORP.PA", "EURAZEO": "RF.PA", "WENDEL": "MF.PA",
    "BUREAU VERITAS": "BVI.PA", "SODEXO": "SW.PA",
    "DASSAULT AVIATION": "AM.PA", "SCOR": "SCR.PA",
    "CGG": "CGG.PA", "TECHNIP": "FTI.PA", "TECHNIPFMC": "FTI.PA",
    "IMERYS": "NK.PA", "REMY COINTREAU": "RCO.PA",
    "PLASTIC OMNIUM": "POM.PA", "FAURECIA": "EO.PA",
    "FORVIA": "FRVIA.PA",
}

DEFAULT_PORTFOLIOS = {m: {} for m in FAMILY_MEMBERS}

CUSTOM_CSS = """
<style>
    .main-header {font-size:2.2rem;font-weight:700;margin-bottom:0.3rem;color:#1a1a2e;}
    .sub-header {font-size:1rem;color:#6c757d;margin-bottom:1.5rem;}
    .metric-card {padding:1.1rem;border-radius:12px;color:white;text-align:center;margin-bottom:0.8rem;}
    .metric-card h3 {font-size:0.8rem;font-weight:400;margin:0;opacity:0.85;}
    .metric-card h2 {font-size:1.5rem;font-weight:700;margin:0.2rem 0 0 0;}
    .blue-card {background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);}
    .green-card {background:linear-gradient(135deg,#11998e 0%,#38ef7d 100%);}
    .red-card {background:linear-gradient(135deg,#eb3349 0%,#f45c43 100%);}
    .orange-card {background:linear-gradient(135deg,#f7971e 0%,#ffd200 100%);}
    .purple-card {background:linear-gradient(135deg,#a18cd1 0%,#fbc2eb 100%);}
    .section-title {font-size:1.3rem;font-weight:600;color:#1a1a2e;margin-top:1.5rem;
        margin-bottom:1rem;padding-bottom:0.4rem;border-bottom:2px solid #667eea;}
    div[data-testid="stSidebar"] {background:linear-gradient(180deg,#1a1a2e 0%,#16213e 100%);}
    div[data-testid="stSidebar"] * {color:white !important;}
    div[data-testid="stSidebar"] hr {border-color:rgba(255,255,255,0.15) !important;}
</style>
"""


def card(title, value, cls="blue-card"):
    return f'<div class="metric-card {cls}"><h3>{title}</h3><h2>{value}</h2></div>'


# =============================================================
# PERSISTENCE
# =============================================================
def load_portfolios():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        for m in FAMILY_MEMBERS:
            if m not in data:
                data[m] = {}
        return data
    return {m: {} for m in FAMILY_MEMBERS}


def save_portfolios(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_alerts():
    if os.path.exists(ALERTS_FILE):
        with open(ALERTS_FILE, "r") as f:
            return json.load(f)
    return []


def save_alerts(a):
    with open(ALERTS_FILE, "w") as f:
        json.dump(a, f, indent=2)


# =============================================================
# YAHOO FINANCE
# =============================================================
@st.cache_data(ttl=300)
def get_prices(tickers):
    prices = {}
    tklist = [t for t in tickers if t]
    if not tklist:
        return prices
    try:
        data = yf.download(tklist, period="5d", group_by="ticker", progress=False)
        for t in tklist:
            try:
                if len(tklist) == 1:
                    prices[t] = float(data["Close"].dropna().iloc[-1])
                else:
                    prices[t] = float(data[t]["Close"].dropna().iloc[-1])
            except Exception:
                prices[t] = 0.0
    except Exception:
        for t in tklist:
            prices[t] = 0.0
    return prices


@st.cache_data(ttl=3600)
def get_fundamentals(tickers):
    results = {}
    for t in tickers:
        try:
            info = yf.Ticker(t).info
            results[t] = {
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),
                "pe": info.get("trailingPE"), "pe_fwd": info.get("forwardPE"),
                "div_yield": info.get("dividendYield"),
                "beta": info.get("beta"), "mcap": info.get("marketCap"),
                "h52": info.get("fiftyTwoWeekHigh"), "l52": info.get("fiftyTwoWeekLow"),
                "target": info.get("targetMeanPrice"),
                "reco": info.get("recommendationKey", "N/A"),
                "roe": info.get("returnOnEquity"),
                "margin": info.get("profitMargins"),
                "rev_growth": info.get("revenueGrowth"),
                "debt_eq": info.get("debtToEquity"),
                "payout": info.get("payoutRatio"),
            }
        except Exception:
            results[t] = {"sector": "N/A"}
    return results


@st.cache_data(ttl=600)
def get_history(tickers, start):
    try:
        return yf.download(list(tickers), start=start, progress=False, group_by="ticker")
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=600)
def get_bench(start):
    try:
        d = yf.download(BENCH_TICKER, start=start, progress=False)
        return d["Close"].squeeze()
    except Exception:
        return pd.Series()


def calc_value(pf, start):
    tks = list(pf.keys())
    if not tks:
        return pd.Series()
    hist = get_history(tuple(tks), start)
    if hist.empty:
        return pd.Series()
    val = pd.Series(0.0, index=hist.index)
    for tk, info in pf.items():
        try:
            c = hist["Close"].squeeze() if len(tks) == 1 else hist[tk]["Close"].squeeze()
            c = c.ffill()
            bd = pd.Timestamp(info["buy_date"])
            c[c.index < bd] = info["buy_price"]
            val = val + c * info["qty"]
        except Exception:
            pass
    return val


def calc_inv(pf, idx):
    inv = pd.Series(0.0, index=idx)
    for tk, info in pf.items():
        bd = pd.Timestamp(info["buy_date"])
        inv[idx >= bd] += info["buy_price"] * info["qty"]
    return inv


def fmt_big(v):
    if v is None: return "N/A"
    if abs(v) >= 1e9: return f"{v/1e9:.1f} Mds"
    if abs(v) >= 1e6: return f"{v/1e6:.1f} M"
    return f"{v:,.0f}"


def find_ticker(name):
    """Trouve le ticker Yahoo a partir du nom de la valeur."""
    up = name.upper().strip()
    if up in NAME_TO_TICKER:
        return NAME_TO_TICKER[up]
    for key, val in NAME_TO_TICKER.items():
        if key in up or up in key:
            return val
    return up.replace(" ", "-") + ".PA"


# =============================================================
# LOGIN
# =============================================================
if "logged" not in st.session_state:
    st.session_state.logged = False
if "portfolios" not in st.session_state:
    st.session_state.portfolios = load_portfolios()

if not st.session_state.logged:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.markdown("")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown('<div class="main-header">Portefeuilles Famille Faure</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Suivi en temps reel de vos investissements</div>', unsafe_allow_html=True)
        st.write("")
        pw = st.text_input("Mot de passe", type="password", placeholder="Mot de passe famille")
        if st.button("Se connecter", type="primary"):
            if pw == PASS:
                st.session_state.logged = True
                st.rerun()
            else:
                st.error("Mot de passe incorrect")
    st.stop()

# =============================================================
# NAVIGATION
# =============================================================
PF = st.session_state.portfolios
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.sidebar.markdown("## FAMILLE FAURE")
st.sidebar.write("Tracker Portefeuilles")
st.sidebar.write("---")
page = st.sidebar.radio("Navigation", [
    "Dashboard", "Analyse fondamentale", "Performance",
    "Alertes", "Recommandations", "Gestion des donnees"])
st.sidebar.write("---")
nb_p = sum(len(p) for p in PF.values())
st.sidebar.write(f"4 membres | {nb_p} positions")
st.sidebar.write(datetime.now().strftime("%d/%m/%Y %H:%M"))
st.sidebar.write("---")
if st.sidebar.button("Actualiser les cours"):
    st.cache_data.clear()
    st.rerun()
if st.sidebar.button("Deconnexion"):
    st.session_state.logged = False
    st.rerun()


# =============================================================
# PAGE 1 : DASHBOARD
# =============================================================
if page == "Dashboard":
    st.markdown('<div class="main-header">Dashboard</div>', unsafe_allow_html=True)

    member = st.selectbox("Membre", ["Famille Faure (tous)"] + FAMILY_MEMBERS)

    if member == "Famille Faure (tous)":
        consolidated = {}
        for m in FAMILY_MEMBERS:
            for tk, info in PF.get(m, {}).items():
                if tk not in consolidated:
                    consolidated[tk] = {"qty": 0, "total_cost": 0,
                                        "buy_date": info["buy_date"], "name": info["name"]}
                consolidated[tk]["qty"] += info["qty"]
                consolidated[tk]["total_cost"] += info["buy_price"] * info["qty"]
                consolidated[tk]["buy_date"] = min(consolidated[tk]["buy_date"], info["buy_date"])
        portfolio = {t: {"qty": v["qty"], "buy_price": v["total_cost"] / v["qty"],
                         "buy_date": v["buy_date"], "name": v["name"]}
                     for t, v in consolidated.items()}
    else:
        portfolio = PF.get(member, {})

    if not portfolio:
        st.info("Aucune position pour ce membre. Va dans 'Gestion des donnees' pour importer un fichier Excel.")
        st.stop()

    tickers = list(portfolio.keys())
    with st.spinner("Chargement des cours..."):
        prices = get_prices(tuple(tickers))
        fundas = get_fundamentals(tuple(tickers))

    rows = []
    tot_inv = tot_val = tot_div = 0
    for tk, info in portfolio.items():
        cur = prices.get(tk, 0)
        val = cur * info["qty"]
        inv = info["buy_price"] * info["qty"]
        pnl_e = val - inv
        pct = (pnl_e / inv * 100) if inv else 0
        f = fundas.get(tk, {})
        dy = f.get("div_yield")
        tot_div += (val * dy) if dy else 0
        rows.append({
            "Valeur": info["name"], "Ticker": tk,
            "Secteur": f.get("sector", "N/A"),
            "Qte": info["qty"], "PRU": round(info["buy_price"], 2),
            "Cours": round(cur, 2), "Valeur EUR": round(val, 0),
            "PnL EUR": round(pnl_e, 0), "PnL %": round(pct, 2),
            "PE": round(f["pe"], 1) if f.get("pe") else None,
            "Div %": round(dy * 100, 2) if dy else None,
            "Beta": round(f["beta"], 2) if f.get("beta") else None,
        })
        tot_inv += inv
        tot_val += val

    tot_pnl = tot_val - tot_inv
    tot_pct = (tot_pnl / tot_inv * 100) if tot_inv else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(card("VALEUR TOTALE", f"{tot_val:,.0f} EUR", "blue-card"), unsafe_allow_html=True)
    with c2: st.markdown(card("INVESTI", f"{tot_inv:,.0f} EUR", "purple-card"), unsafe_allow_html=True)
    with c3: st.markdown(card("PLUS-VALUE", f"{tot_pnl:+,.0f} EUR ({tot_pct:+.1f}%)",
                              "green-card" if tot_pnl >= 0 else "red-card"), unsafe_allow_html=True)
    with c4: st.markdown(card("DIVIDENDES EST./AN", f"{tot_div:,.0f} EUR", "orange-card"), unsafe_allow_html=True)

    st.markdown('<div class="section-title">Positions</div>', unsafe_allow_html=True)
    df = pd.DataFrame(rows).sort_values("Valeur EUR", ascending=False)
    st.dataframe(df, hide_index=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Repartition par valeur</div>', unsafe_allow_html=True)
        fig1 = px.pie(df, values="Valeur EUR", names="Valeur", hole=0.45,
                       color_discrete_sequence=px.colors.qualitative.Set2)
        fig1.update_traces(textposition="inside", textinfo="percent+label")
        fig1.update_layout(showlegend=False, margin=dict(t=20, b=20))
        st.plotly_chart(fig1)
    with col2:
        st.markdown('<div class="section-title">Repartition par secteur</div>', unsafe_allow_html=True)
        dfs = df.groupby("Secteur")["Valeur EUR"].sum().reset_index()
        fig1b = px.pie(dfs, values="Valeur EUR", names="Secteur", hole=0.45,
                        color_discrete_sequence=px.colors.qualitative.Pastel)
        fig1b.update_traces(textposition="inside", textinfo="percent+label")
        fig1b.update_layout(showlegend=False, margin=dict(t=20, b=20))
        st.plotly_chart(fig1b)

    st.markdown('<div class="section-title">PnL par position</div>', unsafe_allow_html=True)
    dfb = df.sort_values("PnL %")
    colors = ["#ef4444" if x < 0 else "#22c55e" for x in dfb["PnL %"]]
    fig2 = go.Figure(go.Bar(x=dfb["PnL %"], y=dfb["Valeur"], orientation="h",
                            marker_color=colors,
                            text=[f"{x:+.1f}%" for x in dfb["PnL %"]], textposition="outside"))
    fig2.update_layout(height=max(350, len(dfb) * 55), margin=dict(t=20, b=40, r=80))
    st.plotly_chart(fig2)

    # Vue par membre
    if member == "Famille Faure (tous)":
        st.markdown('<div class="section-title">Repartition par membre</div>', unsafe_allow_html=True)
        member_vals = []
        for m in FAMILY_MEMBERS:
            mv = 0
            for tk, info in PF.get(m, {}).items():
                mv += prices.get(tk, 0) * info["qty"]
            if mv > 0:
                member_vals.append({"Membre": m, "Valeur EUR": round(mv, 0)})
        if member_vals:
            dfm = pd.DataFrame(member_vals)
            figm = px.pie(dfm, values="Valeur EUR", names="Membre", hole=0.45,
                           color_discrete_sequence=["#667eea", "#22c55e", "#f59e0b", "#ef4444"])
            figm.update_traces(textposition="inside", textinfo="percent+label+value")
            figm.update_layout(showlegend=True, margin=dict(t=20, b=20))
            st.plotly_chart(figm)


# =============================================================
# PAGE 2 : ANALYSE FONDAMENTALE
# =============================================================
elif page == "Analyse fondamentale":
    st.markdown('<div class="main-header">Analyse fondamentale</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Donnees Yahoo Finance en temps reel</div>', unsafe_allow_html=True)

    member = st.selectbox("Membre", FAMILY_MEMBERS, key="af")
    portfolio = PF.get(member, {})
    if not portfolio:
        st.info("Aucune position."); st.stop()

    tickers = list(portfolio.keys())
    with st.spinner("Yahoo Finance..."):
        prices = get_prices(tuple(tickers))
        fundas = get_fundamentals(tuple(tickers))

    for tk, info in portfolio.items():
        cur = prices.get(tk, 0)
        f = fundas.get(tk, {})
        pnl = ((cur - info["buy_price"]) / info["buy_price"]) * 100 if info["buy_price"] else 0

        st.write("---")
        st.write(f"### {info['name']} ({tk})")
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("Cours", f"{cur:.2f}")
        c2.metric("PnL", f"{pnl:+.1f}%")
        c3.metric("P/E", f"{f['pe']:.1f}" if f.get("pe") else "N/A")
        c4.metric("Dividende", f"{f['div_yield']*100:.2f}%" if f.get("div_yield") else "N/A")
        c5.metric("Beta", f"{f['beta']:.2f}" if f.get("beta") else "N/A")
        c6.metric("Cap.", fmt_big(f.get("mcap")))

        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("P/E fwd", f"{f['pe_fwd']:.1f}" if f.get("pe_fwd") else "N/A")
        c2.metric("Haut 52s", f"{f['h52']:.2f}" if f.get("h52") else "N/A")
        c3.metric("Bas 52s", f"{f['l52']:.2f}" if f.get("l52") else "N/A")
        target = f.get("target")
        if target and cur > 0:
            c4.metric("Objectif", f"{target:.2f}", f"{((target-cur)/cur*100):+.1f}%")
        else:
            c4.metric("Objectif", "N/A")
        c5.metric("Reco", str(f.get("reco", "N/A")).upper())
        c6.metric("ROE", f"{f['roe']*100:.1f}%" if f.get("roe") else "N/A")

        st.write(f"**Secteur** : {f.get('sector','N/A')} | **Industrie** : {f.get('industry','N/A')}")

    st.write("---")
    st.markdown('<div class="section-title">Comparatif</div>', unsafe_allow_html=True)
    comp = []
    for tk, info in portfolio.items():
        f = fundas.get(tk, {})
        t = f.get("target")
        cur = prices.get(tk, 0)
        comp.append({
            "Valeur": info["name"], "Secteur": f.get("sector", "N/A"),
            "P/E": round(f["pe"], 1) if f.get("pe") else None,
            "Div %": round(f["div_yield"]*100, 2) if f.get("div_yield") else None,
            "Beta": round(f["beta"], 2) if f.get("beta") else None,
            "ROE %": round(f["roe"]*100, 1) if f.get("roe") else None,
            "Reco": str(f.get("reco", "")).upper(),
            "Objectif": round(t, 2) if t else None,
            "Upside %": round((t - cur) / cur * 100, 1) if t and cur else None,
        })
    st.dataframe(pd.DataFrame(comp), hide_index=True)

    sdf = pd.DataFrame(comp).dropna(subset=["P/E", "Div %"])
    if len(sdf) > 1:
        st.markdown('<div class="section-title">P/E vs Dividende</div>', unsafe_allow_html=True)
        fig = px.scatter(sdf, x="P/E", y="Div %", text="Valeur", color="Secteur", size_max=15)
        fig.update_traces(textposition="top center")
        fig.update_layout(height=450)
        st.plotly_chart(fig)


# =============================================================
# PAGE 3 : PERFORMANCE
# =============================================================
elif page == "Performance":
    st.markdown('<div class="main-header">Performance et risque</div>', unsafe_allow_html=True)

    c1, c2 = st.columns([2, 1])
    with c1: member = st.selectbox("Membre", FAMILY_MEMBERS, key="p1")
    with c2:
        pmap = {"1 mois": 30, "3 mois": 90, "6 mois": 180, "1 an": 365, "2 ans": 730}
        per = st.selectbox("Periode", list(pmap.keys()), index=3, key="p2")

    portfolio = PF.get(member, {})
    if not portfolio:
        st.info("Aucune position."); st.stop()

    sd = (datetime.now() - timedelta(days=pmap[per])).strftime("%Y-%m-%d")
    with st.spinner("Calcul..."):
        pf = calc_value(portfolio, sd)
        bench = get_bench(sd)
    if pf.empty:
        st.warning("Donnees indisponibles."); st.stop()

    inv = calc_inv(portfolio, pf.index)
    pnl_h = pf - inv
    rets = pf.pct_change().dropna()
    vol = float(rets.std() * np.sqrt(252) * 100) if len(rets) > 1 else 0
    cmax = pf.cummax()
    dd = (pf - cmax) / cmax * 100
    mdd = float(dd.min())
    pret = float((pf.iloc[-1] / pf.iloc[0] - 1) * 100) if len(pf) > 1 else 0
    ann = float((1 + rets.mean()) ** 252 - 1) if len(rets) > 1 else 0
    sh = round((ann - 0.03) / (float(rets.std()) * np.sqrt(252)), 2) if vol > 0 and len(rets) > 20 else 0.0
    sd2 = float(rets[rets < 0].std() * np.sqrt(252)) if len(rets[rets < 0]) > 5 else 0
    so = round((ann - 0.03) / sd2, 2) if sd2 > 0 else 0.0
    cal = round(ann / abs(mdd / 100), 2) if mdd != 0 else 0.0
    wr = round(int((rets > 0).sum()) / max(1, int((rets != 0).sum())) * 100, 1)
    var95 = float(np.percentile(rets.dropna(), 5) * float(pf.iloc[-1])) if len(rets) > 20 else 0

    st.markdown('<div class="section-title">Indicateurs cles</div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Valeur", f"{float(pf.iloc[-1]):,.0f} EUR")
    c2.metric("Perf", f"{pret:+.1f}%")
    c3.metric("Rdt ann.", f"{ann*100:+.1f}%")
    c4.metric("Volatilite", f"{vol:.1f}%")
    c5.metric("Sharpe", f"{sh}")
    c6.metric("Max DD", f"{mdd:+.1f}%")

    st.markdown('<div class="section-title">Indicateurs avances</div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Sortino", f"{so}")
    c2.metric("Calmar", f"{cal}")
    c3.metric("Win rate", f"{wr}%")
    c4.metric("VaR 95%/j", f"{var95:,.0f} EUR")
    c5.metric("Nb positions", len(portfolio))

    st.markdown('<div class="section-title">Evolution de la valeur</div>', unsafe_allow_html=True)
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=pf.index, y=pf.values, name="Portefeuille",
                              line=dict(color="#667eea", width=2.5),
                              fill="tozeroy", fillcolor="rgba(102,126,234,0.1)"))
    fig3.add_trace(go.Scatter(x=inv.index, y=inv.values, name="Investi",
                              line=dict(color="#adb5bd", dash="dash")))
    fig3.update_layout(hovermode="x unified", height=450,
                       legend=dict(orientation="h", yanchor="bottom", y=1.02))
    st.plotly_chart(fig3)

    st.markdown('<div class="section-title">Plus-value cumulee</div>', unsafe_allow_html=True)
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(x=pnl_h.index, y=pnl_h.values, name="PnL",
                              line=dict(color="#22c55e", width=2),
                              fill="tozeroy", fillcolor="rgba(34,197,94,0.1)"))
    fig4.add_hline(y=0, line_dash="dash", line_color="gray")
    fig4.update_layout(hovermode="x unified", height=350)
    st.plotly_chart(fig4)

    st.markdown(f'<div class="section-title">vs {BENCH_NAME}</div>', unsafe_allow_html=True)
    if not bench.empty and len(pf) > 1:
        ci = pf.index.intersection(bench.index)
        if len(ci) > 1:
            pn = (pf.loc[ci] / pf.loc[ci].iloc[0]) * 100
            bn = (bench.loc[ci] / bench.loc[ci].iloc[0]) * 100
            fig5 = go.Figure()
            fig5.add_trace(go.Scatter(x=ci, y=pn.values, name="Portefeuille",
                                      line=dict(color="#667eea", width=2.5)))
            fig5.add_trace(go.Scatter(x=ci, y=bn.values, name=BENCH_NAME,
                                      line=dict(color="#f59e0b", width=2, dash="dash")))
            fig5.add_hline(y=100, line_dash="dot", line_color="gray")
            fig5.update_layout(yaxis_title="Base 100", hovermode="x unified", height=400)
            st.plotly_chart(fig5)
            pr = float((pn.iloc[-1] / 100 - 1) * 100)
            br = float((bn.iloc[-1] / 100 - 1) * 100)
            al = pr - br
            if al > 0: st.success(f"Portefeuille: {pr:+.1f}% vs CAC 40: {br:+.1f}% = Alpha: {al:+.1f}%")
            else: st.error(f"Portefeuille: {pr:+.1f}% vs CAC 40: {br:+.1f}% = Alpha: {al:+.1f}%")

    st.markdown('<div class="section-title">Drawdown</div>', unsafe_allow_html=True)
    fig6 = go.Figure()
    fig6.add_trace(go.Scatter(x=dd.index, y=dd.values, name="DD",
                              line=dict(color="#ef4444", width=1.5),
                              fill="tozeroy", fillcolor="rgba(239,68,68,0.1)"))
    fig6.update_layout(yaxis_title="%", hovermode="x unified", height=300)
    st.plotly_chart(fig6)

    st.markdown('<div class="section-title">Distribution des rendements</div>', unsafe_allow_html=True)
    fig7 = go.Figure()
    fig7.add_trace(go.Histogram(x=rets.values*100, nbinsx=50, marker_color="#667eea", opacity=0.7))
    fig7.add_vline(x=0, line_dash="dash", line_color="red")
    fig7.update_layout(xaxis_title="Rendement %", height=350)
    st.plotly_chart(fig7)


# =============================================================
# PAGE 4 : ALERTES
# =============================================================
elif page == "Alertes":
    st.markdown('<div class="main-header">Alertes</div>', unsafe_allow_html=True)
    alerts = load_alerts()

    st.markdown('<div class="section-title">Nouvelle alerte</div>', unsafe_allow_html=True)
    all_tk = sorted(set(tk for p in PF.values() for tk in p.keys()))
    if not all_tk:
        st.info("Importez d abord des positions.")
        st.stop()

    c1, c2, c3 = st.columns(3)
    with c1: a_tk = st.selectbox("Ticker", all_tk)
    with c2: a_type = st.selectbox("Type", ["Prix au-dessus", "Prix en-dessous", "PnL % au-dessus", "PnL % en-dessous"])
    with c3: a_val = st.number_input("Seuil", value=0.0, step=1.0)

    if st.button("Ajouter", type="primary"):
        alerts.append({"ticker": a_tk, "type": a_type, "value": a_val,
                       "created": datetime.now().strftime("%d/%m/%Y %H:%M")})
        save_alerts(alerts)
        st.success("Alerte ajoutee !")
        st.rerun()

    st.markdown('<div class="section-title">Alertes actives</div>', unsafe_allow_html=True)
    if not alerts:
        st.info("Aucune alerte.")
    else:
        atks = list(set(a["ticker"] for a in alerts))
        cp = get_prices(tuple(atks)) if atks else {}
        for i, a in enumerate(alerts):
            cur = cp.get(a["ticker"], 0)
            triggered = False
            if "Prix au-dessus" == a["type"] and cur > a["value"]: triggered = True
            elif "Prix en-dessous" == a["type"] and cur < a["value"]: triggered = True
            elif "PnL" in a["type"]:
                for m, p in PF.items():
                    if a["ticker"] in p:
                        pnl_p = ((cur - p[a["ticker"]]["buy_price"]) / p[a["ticker"]]["buy_price"]) * 100
                        if "au-dessus" in a["type"] and pnl_p > a["value"]: triggered = True
                        elif "en-dessous" in a["type"] and pnl_p < a["value"]: triggered = True
                        break
            c1, c2, c3 = st.columns([5, 2, 1])
            c1.write(f"**{a['ticker']}** {a['type']} **{a['value']}** (cours: {cur:.2f})")
            c2.write("**DECLENCHEE**" if triggered else "En attente")
            if c3.button("X", key=f"d{i}"):
                alerts.pop(i); save_alerts(alerts); st.rerun()
            if triggered:
                st.warning(f"ALERTE : {a['ticker']} - cours = {cur:.2f}")

    st.markdown('<div class="section-title">Alertes automatiques</div>', unsafe_allow_html=True)
    for m in FAMILY_MEMBERS:
        p = PF.get(m, {})
        if not p: continue
        pr = get_prices(tuple(p.keys()))
        for tk, info in p.items():
            cur = pr.get(tk, 0)
            if cur == 0: continue
            pnl = ((cur - info["buy_price"]) / info["buy_price"]) * 100
            if pnl > 30:
                st.success(f"{m} - {info['name']}: {pnl:+.1f}% -> Securiser ?")
            elif pnl < -15:
                st.error(f"{m} - {info['name']}: {pnl:+.1f}% -> Surveiller")


# =============================================================
# PAGE 5 : RECOMMANDATIONS
# =============================================================
elif page == "Recommandations":
    st.markdown('<div class="main-header">Recommandations</div>', unsafe_allow_html=True)

    member = st.selectbox("Membre", FAMILY_MEMBERS, key="r1")
    portfolio = PF.get(member, {})
    if not portfolio:
        st.info("Aucune position."); st.stop()

    tickers = list(portfolio.keys())
    with st.spinner("Analyse..."):
        prices = get_prices(tuple(tickers))
        fundas = get_fundamentals(tuple(tickers))

    tv = sum(prices.get(tk, 0) * info["qty"] for tk, info in portfolio.items())
    pos = []
    for tk, info in portfolio.items():
        cur = prices.get(tk, 0)
        f = fundas.get(tk, {})
        pos.append({"name": info["name"], "ticker": tk, "value": cur * info["qty"],
                    "weight": (cur * info["qty"] / tv * 100) if tv else 0,
                    "sector": f.get("sector", "N/A"), "pe": f.get("pe"),
                    "beta": f.get("beta"), "reco": f.get("reco", "N/A"),
                    "target": f.get("target"), "div": f.get("div_yield"),
                    "pnl": ((cur - info["buy_price"]) / info["buy_price"]) * 100 if info["buy_price"] else 0})
    dfp = pd.DataFrame(pos).sort_values("weight", ascending=False)

    # Consensus
    st.markdown('<div class="section-title">1. Consensus analystes</div>', unsafe_allow_html=True)
    for _, r in dfp.iterrows():
        reco = str(r["reco"]).upper()
        t = r["target"]
        cur = prices.get(r["ticker"], 0)
        up = ((t - cur) / cur * 100) if t and cur else None
        msg = f"**{r['name']}** : {reco}"
        if up is not None: msg += f" | Objectif: {t:.0f} EUR ({up:+.1f}%)"
        if reco in ["BUY", "STRONG_BUY"]: st.success(msg)
        elif reco in ["SELL", "STRONG_SELL"]: st.error(msg)
        else: st.info(msg)

    # Concentration
    st.markdown('<div class="section-title">2. Concentration</div>', unsafe_allow_html=True)
    mw = dfp["weight"].max()
    if mw > 40: st.error(f"RISQUE : {dfp.iloc[0]['name']} = {mw:.1f}%")
    elif mw > 25: st.warning(f"Attention : {dfp.iloc[0]['name']} = {mw:.1f}%")
    else: st.success(f"OK : max = {mw:.1f}%")

    fig = go.Figure(go.Bar(x=dfp["weight"], y=dfp["name"], orientation="h",
                           marker_color="#667eea",
                           text=[f"{w:.1f}%" for w in dfp["weight"]], textposition="outside"))
    fig.update_layout(height=max(300, len(dfp) * 50), margin=dict(t=20, b=40))
    st.plotly_chart(fig)

    # Secteurs
    st.markdown('<div class="section-title">3. Secteurs</div>', unsafe_allow_html=True)
    ds = dfp.groupby("sector")["weight"].sum().sort_values(ascending=False)
    ns = len(ds)
    if ns <= 2: st.error(f"{ns} secteurs. Diversifiez !")
    elif ns <= 4: st.warning(f"{ns} secteurs.")
    else: st.success(f"{ns} secteurs.")
    figs = px.bar(x=ds.index, y=ds.values, color=ds.values, color_continuous_scale="Viridis")
    figs.update_layout(height=350)
    st.plotly_chart(figs)

    # Recos
    st.markdown('<div class="section-title">4. Actions recommandees</div>', unsafe_allow_html=True)
    recos = []
    for _, r in dfp.iterrows():
        if r["pnl"] > 50: recos.append(f"Prendre des benefices sur **{r['name']}** ({r['pnl']:+.1f}%)")
        if r["pnl"] < -20: recos.append(f"Reevaluer **{r['name']}** ({r['pnl']:+.1f}%)")
        if r["pe"] and r["pe"] > 40: recos.append(f"PE eleve sur **{r['name']}** ({r['pe']:.0f}x)")
        if r["reco"] in ["sell", "strong_sell"]: recos.append(f"Analystes negatifs sur **{r['name']}**")
    if recos:
        for rc in recos: st.info(rc)
    else:
        st.success("Portefeuille bien equilibre !")

    # Score
    st.markdown('<div class="section-title">5. Score</div>', unsafe_allow_html=True)
    score = 100
    if ns < 3: score -= 30
    elif ns < 5: score -= 15
    if mw > 40: score -= 25
    elif mw > 30: score -= 10
    if len(portfolio) < 4: score -= 20
    score = max(0, min(100, score))
    fsc = go.Figure(go.Indicator(mode="gauge+number", value=score,
        gauge={"axis": {"range": [0, 100]},
               "bar": {"color": "green" if score >= 70 else "orange" if score >= 50 else "red"},
               "steps": [{"range": [0, 40], "color": "rgba(255,0,0,0.1)"},
                         {"range": [40, 70], "color": "rgba(255,165,0,0.1)"},
                         {"range": [70, 100], "color": "rgba(0,128,0,0.1)"}]}))
    fsc.update_layout(height=300)
    st.plotly_chart(fsc)


# =============================================================
# PAGE 6 : GESTION DES DONNEES
# =============================================================
elif page == "Gestion des donnees":
    st.markdown('<div class="main-header">Gestion des donnees</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Ajouter position", "Importer Excel", "Exporter"])

    with tab1:
        st.write("### Ajouter une position")
        c1, c2 = st.columns(2)
        with c1:
            am = st.selectbox("Membre", FAMILY_MEMBERS, key="am")
        with c2:
            atk = st.text_input("Ticker Yahoo (ex: TTE.PA)", key="atk").upper()
            an = st.text_input("Nom", key="an")
        c3, c4, c5 = st.columns(3)
        with c3: aq = st.number_input("Quantite", min_value=1, value=10, key="aq")
        with c4: ap = st.number_input("Prix achat", min_value=0.01, value=100.0, step=0.01, key="ap")
        with c5: ad = st.date_input("Date achat", key="ad")
        if st.button("Ajouter", type="primary", key="add_btn"):
            if am and atk and an:
                if am not in PF: PF[am] = {}
                PF[am][atk] = {"qty": int(aq), "buy_price": float(ap),
                                "buy_date": ad.strftime("%Y-%m-%d"), "name": an}
                st.session_state.portfolios = PF
                save_portfolios(PF)
                st.success(f"Ajoute : {an} pour {am}")
                st.rerun()

    with tab2:
        st.write("### Importer depuis Excel (.xlsx) ou CSV (.csv)")
        st.write("**Format de ton courtier** : Valeur | Code | Place | Date | Qte | P.R.U. | Cours | Valorisation")

        imp_member = st.selectbox("Ce fichier appartient a :", FAMILY_MEMBERS, key="imp_m")

        uploaded = st.file_uploader("Choisis le fichier", type=["csv", "xlsx", "xls"], key="up")
        if uploaded is not None:
            try:
                if uploaded.name.endswith(".csv"):
                    imp_df = pd.read_csv(uploaded)
                else:
                    imp_df = pd.read_excel(uploaded)

                imp_df = imp_df.dropna(how="all")
                imp_df = imp_df[imp_df.iloc[:, 0].notna()]
                imp_df = imp_df[imp_df.iloc[:, 0].astype(str).str.strip() != ""]
                imp_df = imp_df[imp_df.iloc[:, 0].astype(str) != "None"]
                imp_df = imp_df[~imp_df.iloc[:, 0].astype(str).str.upper().str.contains("LIQUIDIT")]
                imp_df = imp_df[pd.to_numeric(imp_df.iloc[:, 4], errors="coerce") > 0]

                st.write(f"**{len(imp_df)} positions detectees :**")
                st.dataframe(imp_df, hide_index=True)
                st.session_state["imp_data"] = imp_df.to_dict()
                st.session_state["imp_member"] = imp_member
            except Exception as e:
                st.error(f"Erreur : {e}")

        if "imp_data" in st.session_state:
            imp_df = pd.DataFrame(st.session_state["imp_data"])
            imp_m = st.session_state.get("imp_member", FAMILY_MEMBERS[0])
            mode = st.radio("Mode", ["Ajouter aux existantes", "Remplacer les positions de ce membre"])

            if st.button("CONFIRMER L IMPORT", type="primary", key="confirm"):
                if imp_m not in PF: PF[imp_m] = {}
                if "Remplacer" in mode: PF[imp_m] = {}

                count = err = 0
                skipped = []
                for _, row in imp_df.iterrows():
                    try:
                        name = str(row.iloc[0]).strip()
                        qt = int(float(row.iloc[4]))
                        pru = float(row.iloc[5])
                        dv = row.iloc[3]
                        dt = dv.strftime("%Y-%m-%d") if isinstance(dv, pd.Timestamp) else str(dv)[:10]
                        if qt <= 0 or pru <= 0: continue
                        ticker = find_ticker(name)
                        PF[imp_m][ticker] = {"qty": qt, "buy_price": pru,
                                              "buy_date": dt, "name": name}
                        count += 1
                        if ticker.endswith("-") or "N/A" in ticker:
                            skipped.append(f"{name} -> {ticker}")
                    except Exception:
                        err += 1
                st.session_state.portfolios = PF
                save_portfolios(PF)
                if "imp_data" in st.session_state: del st.session_state["imp_data"]
                st.success(f"{count} positions importees pour {imp_m} !")
                if skipped: st.warning("Tickers a verifier : " + ", ".join(skipped))
                if err: st.warning(f"{err} lignes ignorees")
                st.rerun()

    with tab3:
        st.write("### Exporter")
        if st.button("Generer CSV"):
            rows = []
            for m in FAMILY_MEMBERS:
                for tk, info in PF.get(m, {}).items():
                    rows.append({"Membre": m, "Ticker": tk, "Nom": info["name"],
                                 "Quantite": info["qty"], "Prix": info["buy_price"],
                                 "Date": info["buy_date"]})
            edf = pd.DataFrame(rows)
            st.download_button("Telecharger", edf.to_csv(index=False),
                               "portefeuilles_faure.csv", "text/csv")
            st.dataframe(edf, hide_index=True)

    st.write("---")
    st.write("### Supprimer une position")
    dm = st.selectbox("Membre", FAMILY_MEMBERS, key="dm")
    if PF.get(dm):
        opts = [f"{tk} - {info['name']}" for tk, info in PF[dm].items()]
        dp = st.selectbox("Position", opts, key="dp")
        if st.button("Supprimer"):
            del PF[dm][dp.split(" - ")[0]]
            st.session_state.portfolios = PF
            save_portfolios(PF)
            st.success("Supprime !")
            st.rerun()
    else:
        st.info("Aucune position pour ce membre.")