import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from datetime import datetime, timedelta
import json, os

# =============================================================
st.set_page_config(page_title="Famille Faure", page_icon="https://cdn-icons-png.flaticon.com/512/2830/2830284.png",
    layout="wide", initial_sidebar_state="expanded")

# =============================================================
# CONFIG
# =============================================================
DATA_FILE = "portfolio_data.json"
ALERTS_FILE = "alerts_data.json"
PASS = "Faure2026!"
FAMILY = ["Patrick", "Nicolas", "Guillaume", "Florian"]
BENCHMARKS = {"^FCHI": "CAC 40", "^SBF120": "SBF 120"}

NAME_TO_TICKER = {
    "CAPGEMINI": "CAP.PA", "ALSTOM": "ALO.PA", "DASSAULT SYSTEMES": "DSY.PA",
    "ENGIE": "ENGI.PA", "RENAULT": "RNO.PA", "STELLANTIS": "STLAP.PA",
    "STELLANTIS NV": "STLAP.PA", "AIR LIQUIDE": "AI.PA", "TOTALENERGIES": "TTE.PA",
    "TOTAL": "TTE.PA", "BNP PARIBAS": "BNP.PA", "LVMH": "MC.PA",
    "L'OREAL": "OR.PA", "L OREAL": "OR.PA", "LOREAL": "OR.PA",
    "HERMES": "RMS.PA", "HERMES INTERNATIONAL": "RMS.PA", "ORANGE": "ORA.PA",
    "SCHNEIDER": "SU.PA", "SCHNEIDER ELECTRIC": "SU.PA", "AXA": "CS.PA",
    "VINCI": "DG.PA", "SANOFI": "SAN.PA", "SAFRAN": "SAF.PA",
    "SAINT-GOBAIN": "SGO.PA", "SAINT GOBAIN": "SGO.PA", "SOCIETE GENERALE": "GLE.PA",
    "CREDIT AGRICOLE": "ACA.PA", "DANONE": "BN.PA", "PERNOD RICARD": "RI.PA",
    "MICHELIN": "ML.PA", "KERING": "KER.PA", "BOUYGUES": "EN.PA",
    "CHRISTIAN DIOR": "CDI.PA", "VEOLIA": "VIE.PA", "LEGRAND": "LR.PA",
    "THALES": "HO.PA", "PUBLICIS": "PUB.PA", "ARKEMA": "AKE.PA",
    "TELEPERFORMANCE": "TEP.PA", "EUROFINS": "ERF.PA", "STMICROELECTRONICS": "STM.PA",
    "WORLDLINE": "WLN.PA", "CARREFOUR": "CA.PA", "ACCOR": "AC.PA",
    "VIVENDI": "VIV.PA", "EDENRED": "EDEN.PA", "ESSILOR": "EL.PA",
    "ESSILORLUXOTTICA": "EL.PA", "AIRBUS": "AIR.PA", "VALEO": "FR.PA",
    "NEXITY": "NXI.PA", "EIFFAGE": "FGR.PA", "AMUNDI": "AMUN.PA",
    "RUBIS": "RUI.PA", "NEXANS": "NEX.PA", "IPSEN": "IPN.PA",
    "BIOMERIEUX": "BIM.PA", "BUREAU VERITAS": "BVI.PA", "SODEXO": "SW.PA",
    "DASSAULT AVIATION": "AM.PA", "SCOR": "SCR.PA", "REMY COINTREAU": "RCO.PA",
    "FAURECIA": "EO.PA", "FORVIA": "FRVIA.PA", "UNIBAIL": "URW.PA",
    "GECINA": "GFC.PA", "COVIVIO": "COV.PA",
}

# =============================================================
# CSS PRO
# =============================================================
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] {font-family:'Inter',sans-serif}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#0f172a,#1e293b)}
section[data-testid="stSidebar"] *{color:#e2e8f0!important}
section[data-testid="stSidebar"] hr{border-color:rgba(148,163,184,.2)!important}
.kpi-row{display:flex;gap:12px;margin-bottom:1.5rem;flex-wrap:wrap}
.kpi{flex:1;min-width:150px;border-radius:16px;padding:18px 14px;color:#fff;position:relative;overflow:hidden}
.kpi::before{content:'';position:absolute;top:-30px;right:-30px;width:80px;height:80px;border-radius:50%;background:rgba(255,255,255,.1)}
.kpi .lb{font-size:.68rem;font-weight:500;text-transform:uppercase;letter-spacing:.08em;opacity:.85;margin-bottom:5px}
.kpi .vl{font-size:1.45rem;font-weight:700;line-height:1.2}
.kpi .sb{font-size:.72rem;opacity:.7;margin-top:3px}
.kpi-blue{background:linear-gradient(135deg,#3b82f6,#6366f1)}
.kpi-green{background:linear-gradient(135deg,#10b981,#059669)}
.kpi-red{background:linear-gradient(135deg,#ef4444,#dc2626)}
.kpi-orange{background:linear-gradient(135deg,#f59e0b,#d97706)}
.kpi-purple{background:linear-gradient(135deg,#8b5cf6,#7c3aed)}
.kpi-teal{background:linear-gradient(135deg,#14b8a6,#0d9488)}
.kpi-slate{background:linear-gradient(135deg,#475569,#334155)}
.member-card{border-radius:16px;padding:20px;color:#fff;margin-bottom:8px}
.member-card .name{font-size:.8rem;font-weight:500;text-transform:uppercase;letter-spacing:.05em;opacity:.85}
.member-card .val{font-size:1.3rem;font-weight:700;margin:4px 0}
.member-card .pnl{font-size:.85rem;font-weight:600}
.sec{font-size:1.15rem;font-weight:600;color:#1e293b;margin:2rem 0 1rem;padding-bottom:8px;border-bottom:2px solid #6366f1}
.ph h1{font-size:1.8rem;font-weight:700;color:#0f172a;margin:0}
.ph p{font-size:.9rem;color:#64748b;margin:4px 0 0}
.hl{height:3px;background:linear-gradient(90deg,#6366f1,#3b82f6,#06b6d4);border-radius:2px;margin:12px 0 24px}
#MainMenu,footer,header{visibility:hidden}
</style>""", unsafe_allow_html=True)

def kpi(lb, vl, sb="", s="kpi-blue"):
    sub = f'<div class="sb">{sb}</div>' if sb else ""
    return f'<div class="kpi {s}"><div class="lb">{lb}</div><div class="vl">{vl}</div>{sub}</div>'

def hdr(t, st_=""):
    st.markdown(f'<div class="ph"><h1>{t}</h1><p>{st_}</p></div><div class="hl"></div>', unsafe_allow_html=True)

def sec(t):
    st.markdown(f'<div class="sec">{t}</div>', unsafe_allow_html=True)

def cpnl(v): return "kpi-green" if v >= 0 else "kpi-red"

PL = dict(font=dict(family="Inter"),plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(t=30,b=30,l=20,r=20),hovermode="x unified",
    legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="center",x=0.5))
CL = ["#6366f1","#3b82f6","#06b6d4","#10b981","#f59e0b","#ef4444","#8b5cf6","#ec4899","#14b8a6","#f97316"]

# =============================================================
# PERSISTENCE
# =============================================================
def load_pf():
    if os.path.exists(DATA_FILE):
        d = json.load(open(DATA_FILE)); [d.setdefault(m, {}) for m in FAMILY]; return d
    return {m: {} for m in FAMILY}

def save_pf(d): json.dump(d, open(DATA_FILE,"w"), indent=2)
def load_al(): return json.load(open(ALERTS_FILE)) if os.path.exists(ALERTS_FILE) else []
def save_al(a): json.dump(a, open(ALERTS_FILE,"w"), indent=2)

def find_tk(name):
    up = name.upper().strip()
    if up in NAME_TO_TICKER: return NAME_TO_TICKER[up]
    for k,v in NAME_TO_TICKER.items():
        if k in up or up in k: return v
    return up.replace(" ","-")+".PA"

def fmt(v):
    if v is None: return "N/A"
    if abs(v)>=1e9: return f"{v/1e9:.1f}Mds"
    if abs(v)>=1e6: return f"{v/1e6:.1f}M"
    return f"{v:,.0f}"

# =============================================================
# YAHOO FINANCE (5 ANS)
# =============================================================
@st.cache_data(ttl=300)
def yf_prices(tickers):
    p={}; tl=[t for t in tickers if t]
    if not tl: return p
    try:
        d=yf.download(tl, period="5y", group_by="ticker", progress=False)
        for t in tl:
            try: p[t]=float(d["Close"].dropna().iloc[-1]) if len(tl)==1 else float(d[t]["Close"].dropna().iloc[-1])
            except: p[t]=0.0
    except:
        for t in tl: p[t]=0.0
    return p

@st.cache_data(ttl=3600)
def yf_info(tickers):
    r={}
    for t in tickers:
        try:
            i=yf.Ticker(t).info
            r[t]={k:i.get(v) for k,v in {"sector":"sector","industry":"industry","pe":"trailingPE",
                "pe_fwd":"forwardPE","dy":"dividendYield","beta":"beta","mcap":"marketCap",
                "h52":"fiftyTwoWeekHigh","l52":"fiftyTwoWeekLow","target":"targetMeanPrice",
                "reco":"recommendationKey","roe":"returnOnEquity","margin":"profitMargins",
                "rev_g":"revenueGrowth","debt":"debtToEquity"}.items()}
            r[t]["sector"]=r[t].get("sector") or "N/A"; r[t]["reco"]=r[t].get("reco") or "N/A"
        except: r[t]={"sector":"N/A","reco":"N/A"}
    return r

@st.cache_data(ttl=600)
def yf_hist(tickers, start):
    try: return yf.download(list(tickers), start=start, progress=False, group_by="ticker")
    except: return pd.DataFrame()

@st.cache_data(ttl=600)
def yf_bench_multi(start):
    """Telecharge CAC 40 et SBF 120."""
    result = {}
    for tk, name in BENCHMARKS.items():
        try:
            d = yf.download(tk, start=start, progress=False)
            result[name] = d["Close"].squeeze()
        except: result[name] = pd.Series()
    return result

@st.cache_data(ttl=600)
def yf_returns_matrix(tickers, start):
    """Matrice de rendements journaliers pour correlation et volatilite."""
    try:
        d = yf.download(list(tickers), start=start, progress=False, group_by="ticker")
        if len(tickers) == 1:
            closes = d["Close"].to_frame(tickers[0])
        else:
            closes = pd.DataFrame({t: d[t]["Close"] for t in tickers if t in d.columns.get_level_values(0)})
        return closes.pct_change().dropna()
    except: return pd.DataFrame()

def pf_value(pf, start):
    tks=list(pf.keys())
    if not tks: return pd.Series()
    h=yf_hist(tuple(tks),start)
    if h.empty: return pd.Series()
    v=pd.Series(0.0,index=h.index)
    for tk,inf in pf.items():
        try:
            c=h["Close"].squeeze() if len(tks)==1 else h[tk]["Close"].squeeze()
            c=c.ffill(); bd=pd.Timestamp(inf["buy_date"])
            c[c.index<bd]=inf["buy_price"]; v+=c*inf["qty"]
        except: pass
    return v

def pf_inv(pf, idx):
    inv=pd.Series(0.0,index=idx)
    for tk,inf in pf.items():
        inv[idx>=pd.Timestamp(inf["buy_date"])]+=inf["buy_price"]*inf["qty"]
    return inv

def member_perf(member_pf, prices):
    """Calcule valorisation et PnL d'un membre."""
    tv=ti=0
    for tk,inf in member_pf.items():
        cur=prices.get(tk,0); tv+=cur*inf["qty"]; ti+=inf["buy_price"]*inf["qty"]
    return tv, ti, tv-ti, ((tv-ti)/ti*100) if ti else 0

# =============================================================
# LOGIN
# =============================================================
if "logged" not in st.session_state: st.session_state.logged=False
if "pf" not in st.session_state: st.session_state.pf=load_pf()

if not st.session_state.logged:
    st.markdown("""<div style="display:flex;justify-content:center;align-items:center;min-height:80vh">
    <div style="text-align:center"><div style="font-size:3rem;font-weight:800;margin-bottom:8px">FAMILLE FAURE</div>
    <div style="font-size:1rem;color:#64748b;margin-bottom:2rem">Tracker Portefeuilles</div></div></div>""",
    unsafe_allow_html=True)
    _,cc,_=st.columns([1.5,1,1.5])
    with cc:
        pw=st.text_input("",type="password",placeholder="Mot de passe",label_visibility="collapsed")
        if st.button("Connexion",type="primary",use_container_width=True):
            if pw==PASS: st.session_state.logged=True; st.rerun()
            else: st.error("Mot de passe incorrect")
    st.stop()

# =============================================================
# SIDEBAR
# =============================================================
PF=st.session_state.pf
with st.sidebar:
    st.markdown("### FAMILLE FAURE")
    st.caption("Tracker Portefeuilles"); st.divider()
    G=st.selectbox("MEMBRE",["Consolide"]+FAMILY)
    st.divider()
    page=st.radio("NAVIGATION",["Dashboard","Analyse fondamentale","Performance",
        "Volatilite et Correlation","Alertes","Recommandations","Gestion"])
    st.divider()
    st.caption(f"{len(FAMILY)} membres | {sum(len(p) for p in PF.values())} positions")
    st.caption(datetime.now().strftime("%d/%m/%Y %H:%M")); st.divider()
    if st.button("Actualiser",use_container_width=True): st.cache_data.clear(); st.rerun()
    if st.button("Deconnexion",use_container_width=True): st.session_state.logged=False; st.rerun()

def get_pf():
    if G=="Consolide":
        c={}
        for m in FAMILY:
            for tk,inf in PF.get(m,{}).items():
                if tk not in c: c[tk]={"qty":0,"tc":0,"bd":inf["buy_date"],"name":inf["name"]}
                c[tk]["qty"]+=inf["qty"]; c[tk]["tc"]+=inf["buy_price"]*inf["qty"]
                c[tk]["bd"]=min(c[tk]["bd"],inf["buy_date"])
        return {t:{"qty":v["qty"],"buy_price":v["tc"]/v["qty"],"buy_date":v["bd"],"name":v["name"]} for t,v in c.items()}
    return PF.get(G,{})

def get_all_tickers():
    return list(set(tk for p in PF.values() for tk in p.keys()))

# =============================================================
# PAGE 1 : DASHBOARD
# =============================================================
if page=="Dashboard":
    hdr("Dashboard",f"Vue d'ensemble - {G}")
    portfolio=get_pf()
    if not portfolio: st.info("Aucune position. Importe un fichier dans Gestion."); st.stop()

    tks=list(portfolio.keys())
    all_tks=get_all_tickers()
    with st.spinner("Chargement..."):
        prices=yf_prices(tuple(all_tks if all_tks else tks))
        fundas=yf_info(tuple(tks))

    # === CARTES MEMBRES (en mode consolide) ===
    if G=="Consolide":
        sec("Performance par membre")
        cols=st.columns(4)
        member_colors=["kpi-blue","kpi-green","kpi-orange","kpi-purple"]
        for i,m in enumerate(FAMILY):
            mp=PF.get(m,{})
            if mp:
                tv,ti,tp,tpct=member_perf(mp,prices)
                with cols[i]:
                    st.markdown(f"""<div class="member-card {member_colors[i]}">
                        <div class="name">{m}</div>
                        <div class="val">{tv:,.0f} EUR</div>
                        <div class="pnl" style="color:{'#bbf7d0' if tp>=0 else '#fecaca'}">{tp:+,.0f} EUR ({tpct:+.1f}%)</div>
                        <div style="font-size:.7rem;opacity:.7;margin-top:4px">{len(mp)} positions | Investi: {ti:,.0f}</div>
                    </div>""", unsafe_allow_html=True)
            else:
                with cols[i]:
                    st.markdown(f"""<div class="member-card kpi-slate">
                        <div class="name">{m}</div>
                        <div class="val">-</div>
                        <div class="pnl">Aucune position</div>
                    </div>""", unsafe_allow_html=True)

    # === KPIs GLOBAUX ===
    rows=[]; ti=tv=td=0
    for tk,inf in portfolio.items():
        cur=prices.get(tk,0); val=cur*inf["qty"]; inv=inf["buy_price"]*inf["qty"]
        pnl=val-inv; pct=(pnl/inv*100) if inv else 0
        f=fundas.get(tk,{}); dy=f.get("dy"); target=f.get("target")
        td+=(val*dy) if dy else 0
        rdt_e=((target-cur)/cur*100) if target and cur>0 else None
        rows.append({"Valeur":inf["name"],"Ticker":tk,"Secteur":f.get("sector","N/A"),
            "Qte":inf["qty"],"PRU":round(inf["buy_price"],2),"Cours":round(cur,2),
            "Valorisation":round(val,0),"PnL (EUR)":round(pnl,0),"PnL (%)":round(pct,1),
            "Rdt espere (%)":round(rdt_e,1) if rdt_e else None,
            "PE":round(f["pe"],1) if f.get("pe") else None,
            "Div (%)":round(dy*100,1) if dy else None,
            "Beta":round(f["beta"],2) if f.get("beta") else None})
        ti+=inv; tv+=val
    tp=tv-ti; tpct=(tp/ti*100) if ti else 0
    re_v=[(r["Rdt espere (%)"],r["Valorisation"]) for r in rows if r["Rdt espere (%)"] is not None]
    rdt_g=sum(r*w for r,w in re_v)/sum(w for _,w in re_v) if re_v else 0

    # Volatilite portefeuille reelle (1 an)
    sd_1y=(datetime.now()-timedelta(days=365)).strftime("%Y-%m-%d")
    pf_val=pf_value(portfolio,sd_1y)
    vol_pf=0
    if not pf_val.empty and len(pf_val)>20:
        vol_pf=float(pf_val.pct_change().dropna().std()*np.sqrt(252)*100)

    sec("Vue globale")
    st.markdown(f"""<div class="kpi-row">
        {kpi("VALORISATION",f"{tv:,.0f} EUR",f"{len(portfolio)} positions","kpi-blue")}
        {kpi("INVESTI",f"{ti:,.0f} EUR","","kpi-purple")}
        {kpi("PLUS-VALUE",f"{tp:+,.0f} EUR",f"{tpct:+.1f}%",cpnl(tp))}
        {kpi("RDT ESPERE",f"{rdt_g:+.1f}%","Consensus analystes","kpi-teal")}
        {kpi("VOLATILITE",f"{vol_pf:.1f}%","Annualisee 1 an","kpi-orange")}
        {kpi("DIVIDENDES/AN",f"{td:,.0f} EUR",f"Yield {(td/tv*100):.1f}%" if tv else "","kpi-slate")}
    </div>""", unsafe_allow_html=True)

    sec("Positions")
    df=pd.DataFrame(rows).sort_values("Valorisation",ascending=False)
    st.dataframe(df,hide_index=True,height=min(800,45+len(df)*35))

    c1,c2=st.columns(2)
    with c1:
        sec("Repartition par valeur")
        f1=px.pie(df,values="Valorisation",names="Valeur",hole=.5,color_discrete_sequence=CL)
        f1.update_traces(textposition="inside",textinfo="percent+label",textfont_size=10)
        f1.update_layout(**PL,showlegend=False,height=380); st.plotly_chart(f1,use_container_width=True)
    with c2:
        sec("Repartition par secteur")
        ds=df.groupby("Secteur")["Valorisation"].sum().reset_index()
        f2=px.pie(ds,values="Valorisation",names="Secteur",hole=.5,color_discrete_sequence=CL)
        f2.update_traces(textposition="inside",textinfo="percent+label",textfont_size=10)
        f2.update_layout(**PL,showlegend=False,height=380); st.plotly_chart(f2,use_container_width=True)

    c1,c2=st.columns(2)
    with c1:
        sec("PnL par position")
        dfb=df.sort_values("PnL (%)")
        fig=go.Figure(go.Bar(x=dfb["PnL (%)"],y=dfb["Valeur"],orientation="h",
            marker_color=["#ef4444" if x<0 else "#10b981" for x in dfb["PnL (%)"]],
            text=[f"{x:+.1f}%" for x in dfb["PnL (%)"]],textposition="outside",textfont=dict(size=11)))
        fig.update_layout(**PL,height=max(350,len(dfb)*50),yaxis=dict(automargin=True))
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        sec("Rendement espere (analystes)")
        dre=df.dropna(subset=["Rdt espere (%)"]).sort_values("Rdt espere (%)")
        if not dre.empty:
            fig=go.Figure(go.Bar(x=dre["Rdt espere (%)"],y=dre["Valeur"],orientation="h",
                marker_color=["#ef4444" if x<0 else "#3b82f6" for x in dre["Rdt espere (%)"]],
                text=[f"{x:+.1f}%" for x in dre["Rdt espere (%)"]],textposition="outside"))
            fig.update_layout(**PL,height=max(350,len(dre)*50),yaxis=dict(automargin=True))
            st.plotly_chart(fig,use_container_width=True)

    if G=="Consolide":
        sec("Repartition par membre")
        mv=[]
        for m in FAMILY:
            val=sum(prices.get(tk,0)*inf["qty"] for tk,inf in PF.get(m,{}).items())
            if val>0: mv.append({"Membre":m,"Valeur":round(val,0)})
        if mv:
            fm=px.pie(pd.DataFrame(mv),values="Valeur",names="Membre",hole=.5,color_discrete_sequence=CL)
            fm.update_traces(textposition="inside",textinfo="percent+label+value")
            fm.update_layout(**PL,height=400); st.plotly_chart(fm,use_container_width=True)


# =============================================================
# PAGE 2 : ANALYSE FONDAMENTALE
# =============================================================
elif page=="Analyse fondamentale":
    hdr("Analyse fondamentale",f"Yahoo Finance - {G}")
    portfolio=get_pf()
    if not portfolio: st.info("Aucune position."); st.stop()
    tks=list(portfolio.keys())
    with st.spinner("Yahoo Finance..."):
        prices=yf_prices(tuple(tks)); fundas=yf_info(tuple(tks))

    for tk,inf in portfolio.items():
        cur=prices.get(tk,0); f=fundas.get(tk,{})
        pnl=((cur-inf["buy_price"])/inf["buy_price"])*100 if inf["buy_price"] else 0
        target=f.get("target"); rdt=((target-cur)/cur*100) if target and cur>0 else None

        st.divider()
        st.markdown(f"#### {inf['name']}  `{tk}`")
        st.caption(f"{f.get('sector','N/A')} | {f.get('industry','N/A')}")
        c1,c2,c3,c4,c5,c6,c7=st.columns(7)
        c1.metric("Cours",f"{cur:.2f}"); c2.metric("PnL",f"{pnl:+.1f}%")
        c3.metric("Rdt espere",f"{rdt:+.1f}%" if rdt else "N/A")
        c4.metric("P/E",f"{f['pe']:.1f}" if f.get("pe") else "N/A")
        c5.metric("Div",f"{f['dy']*100:.1f}%" if f.get("dy") else "N/A")
        c6.metric("Beta",f"{f['beta']:.2f}" if f.get("beta") else "N/A")
        c7.metric("Cap.",fmt(f.get("mcap")))

        c1,c2,c3,c4,c5,c6,c7=st.columns(7)
        c1.metric("P/E fwd",f"{f['pe_fwd']:.1f}" if f.get("pe_fwd") else "N/A")
        c2.metric("Haut 52s",f"{f['h52']:.0f}" if f.get("h52") else "N/A")
        c3.metric("Bas 52s",f"{f['l52']:.0f}" if f.get("l52") else "N/A")
        c4.metric("Objectif",f"{target:.0f}" if target else "N/A")
        c5.metric("Reco",str(f.get("reco","N/A")).upper())
        c6.metric("ROE",f"{f['roe']*100:.1f}%" if f.get("roe") else "N/A")
        c7.metric("Marge",f"{f['margin']*100:.1f}%" if f.get("margin") else "N/A")

    st.divider(); sec("Tableau comparatif")
    comp=[]
    for tk,inf in portfolio.items():
        f=fundas.get(tk,{}); cur=prices.get(tk,0); t=f.get("target")
        comp.append({"Valeur":inf["name"],"Secteur":f.get("sector","N/A"),
            "P/E":round(f["pe"],1) if f.get("pe") else None,
            "P/E fwd":round(f["pe_fwd"],1) if f.get("pe_fwd") else None,
            "Div %":round(f["dy"]*100,1) if f.get("dy") else None,
            "Beta":round(f["beta"],2) if f.get("beta") else None,
            "ROE %":round(f["roe"]*100,1) if f.get("roe") else None,
            "Reco":str(f.get("reco","")).upper(),
            "Objectif":round(t,0) if t else None,
            "Rdt espere %":round((t-cur)/cur*100,1) if t and cur else None})
    st.dataframe(pd.DataFrame(comp),hide_index=True)

    sdf=pd.DataFrame(comp).dropna(subset=["P/E","Div %"])
    if len(sdf)>1:
        sec("P/E vs Dividende")
        fig=px.scatter(sdf,x="P/E",y="Div %",text="Valeur",color="Secteur",color_discrete_sequence=CL)
        fig.update_traces(textposition="top center",textfont_size=10)
        fig.update_layout(**PL,height=450); st.plotly_chart(fig,use_container_width=True)


# =============================================================
# PAGE 3 : PERFORMANCE
# =============================================================
elif page=="Performance":
    hdr("Performance et risque",G)
    portfolio=get_pf()
    if not portfolio: st.info("Aucune position."); st.stop()

    pmap={"1 mois":30,"3 mois":90,"6 mois":180,"1 an":365,"2 ans":730,"3 ans":1095,"5 ans":1825}
    per=st.selectbox("Periode",list(pmap.keys()),index=4)
    sd=(datetime.now()-timedelta(days=pmap[per])).strftime("%Y-%m-%d")

    with st.spinner("Calcul..."):
        pf=pf_value(portfolio,sd); benchmarks=yf_bench_multi(sd)
    if pf.empty: st.warning("Donnees indisponibles."); st.stop()

    inv=pf_inv(portfolio,pf.index); pnl_h=pf-inv
    rets=pf.pct_change().dropna()
    vol=float(rets.std()*np.sqrt(252)*100) if len(rets)>1 else 0
    cmax=pf.cummax(); dd=(pf-cmax)/cmax*100; mdd=float(dd.min())
    pret=float((pf.iloc[-1]/pf.iloc[0]-1)*100) if len(pf)>1 else 0
    ann=float((1+rets.mean())**252-1) if len(rets)>1 else 0
    sh=round((ann-.03)/(float(rets.std())*np.sqrt(252)),2) if vol>0 and len(rets)>20 else 0
    sd2=float(rets[rets<0].std()*np.sqrt(252)) if len(rets[rets<0])>5 else 0
    so=round((ann-.03)/sd2,2) if sd2>0 else 0
    wr=round(int((rets>0).sum())/max(1,int((rets!=0).sum()))*100,1)
    var95=float(np.percentile(rets.dropna(),5)*float(pf.iloc[-1])) if len(rets)>20 else 0
    cal=round(ann/abs(mdd/100),2) if mdd!=0 else 0

    fi=yf_info(tuple(portfolio.keys())); pi=yf_prices(tuple(portfolio.keys()))
    rw=[]
    for tk,inf in portfolio.items():
        cur=pi.get(tk,0); t=fi.get(tk,{}).get("target"); val=cur*inf["qty"]
        if t and cur>0: rw.append(((t-cur)/cur*100,val))
    rdt_esp=sum(r*w for r,w in rw)/sum(w for _,w in rw) if rw else 0

    st.markdown(f"""<div class="kpi-row">
        {kpi("VALORISATION",f"{float(pf.iloc[-1]):,.0f} EUR","","kpi-blue")}
        {kpi("PERFORMANCE",f"{pret:+.1f}%",per,cpnl(pret))}
        {kpi("RDT ANNUALISE",f"{ann*100:+.1f}%","",cpnl(ann))}
        {kpi("VOLATILITE",f"{vol:.1f}%","annualisee","kpi-orange")}
        {kpi("SHARPE",f"{sh}","ratio","kpi-purple")}
        {kpi("MAX DRAWDOWN",f"{mdd:+.1f}%","","kpi-red")}
        {kpi("RDT ESPERE",f"{rdt_esp:+.1f}%","analystes","kpi-teal")}
    </div>""", unsafe_allow_html=True)

    sec("Indicateurs avances")
    c1,c2,c3,c4,c5,c6=st.columns(6)
    c1.metric("Sortino",f"{so}"); c2.metric("Calmar",f"{cal}")
    c3.metric("Win rate",f"{wr}%"); c4.metric("VaR 95%/j",f"{var95:,.0f} EUR")
    c5.metric("Positions",len(portfolio)); c6.metric("Skewness",f"{float(rets.skew()):.2f}" if len(rets)>20 else "N/A")

    sec("Evolution de la valorisation")
    f3=go.Figure()
    f3.add_trace(go.Scatter(x=pf.index,y=pf.values,name="Portefeuille",
        line=dict(color="#6366f1",width=2.5),fill="tozeroy",fillcolor="rgba(99,102,241,0.08)"))
    f3.add_trace(go.Scatter(x=inv.index,y=inv.values,name="Investi",
        line=dict(color="#94a3b8",width=1.5,dash="dash")))
    f3.update_layout(**PL,height=450); st.plotly_chart(f3,use_container_width=True)

    sec("Plus-value cumulee")
    f4=go.Figure()
    f4.add_trace(go.Scatter(x=pnl_h.index,y=pnl_h.values,name="PnL",
        line=dict(color="#10b981",width=2),fill="tozeroy",fillcolor="rgba(16,185,129,0.08)"))
    f4.add_hline(y=0,line_dash="dash",line_color="#94a3b8")
    f4.update_layout(**PL,height=350); st.plotly_chart(f4,use_container_width=True)

    # === BENCHMARKS CAC 40 + SBF 120 ===
    sec("Performance vs CAC 40 et SBF 120")
    if len(pf)>1:
        f5=go.Figure()
        ci_all=pf.index
        pn=(pf/pf.iloc[0])*100
        f5.add_trace(go.Scatter(x=ci_all,y=pn.values,name="Portefeuille",line=dict(color="#6366f1",width=2.5)))
        bench_colors={"CAC 40":"#f59e0b","SBF 120":"#ef4444"}
        for bname,bdata in benchmarks.items():
            if not bdata.empty:
                ci=pf.index.intersection(bdata.index)
                if len(ci)>1:
                    bn=(bdata.loc[ci]/bdata.loc[ci].iloc[0])*100
                    f5.add_trace(go.Scatter(x=ci,y=bn.values,name=bname,
                        line=dict(color=bench_colors.get(bname,"#888"),width=2,dash="dash")))
        f5.add_hline(y=100,line_dash="dot",line_color="#cbd5e1")
        f5.update_layout(**PL,height=450,yaxis_title="Base 100")
        st.plotly_chart(f5,use_container_width=True)

        # Alpha vs chaque bench
        for bname,bdata in benchmarks.items():
            if not bdata.empty:
                ci=pf.index.intersection(bdata.index)
                if len(ci)>1:
                    pr=float((pf.loc[ci].iloc[-1]/pf.loc[ci].iloc[0]-1)*100)
                    br=float((bdata.loc[ci].iloc[-1]/bdata.loc[ci].iloc[0]-1)*100)
                    al=pr-br
                    if al>0: st.success(f"vs {bname}: Ptf {pr:+.1f}% | {bname} {br:+.1f}% | **Alpha {al:+.1f}%**")
                    else: st.error(f"vs {bname}: Ptf {pr:+.1f}% | {bname} {br:+.1f}% | **Alpha {al:+.1f}%**")

    c1,c2=st.columns(2)
    with c1:
        sec("Drawdown")
        f6=go.Figure()
        f6.add_trace(go.Scatter(x=dd.index,y=dd.values,line=dict(color="#ef4444",width=1.5),
            fill="tozeroy",fillcolor="rgba(239,68,68,0.08)"))
        f6.update_layout(**PL,height=300,yaxis_title="%"); st.plotly_chart(f6,use_container_width=True)
    with c2:
        sec("Distribution des rendements")
        f7=go.Figure()
        f7.add_trace(go.Histogram(x=rets.values*100,nbinsx=60,marker_color="#6366f1",opacity=.75))
        f7.add_vline(x=0,line_dash="dash",line_color="#ef4444")
        f7.update_layout(**PL,height=300,xaxis_title="Rendement %"); st.plotly_chart(f7,use_container_width=True)


# =============================================================
# PAGE 4 : VOLATILITE ET CORRELATION
# =============================================================
elif page=="Volatilite et Correlation":
    hdr("Volatilite et Correlation",f"Analyse quantitative - {G}")
    portfolio=get_pf()
    if not portfolio: st.info("Aucune position."); st.stop()

    tks=list(portfolio.keys())
    names={tk:inf["name"] for tk,inf in portfolio.items()}
    pmap2={"6 mois":180,"1 an":365,"2 ans":730,"3 ans":1095,"5 ans":1825}
    per2=st.selectbox("Historique",list(pmap2.keys()),index=2)
    sd2=(datetime.now()-timedelta(days=pmap2[per2])).strftime("%Y-%m-%d")

    with st.spinner("Calcul des rendements historiques..."):
        ret_matrix=yf_returns_matrix(tks,sd2)

    if ret_matrix.empty or len(ret_matrix.columns)<2:
        st.warning("Donnees insuffisantes."); st.stop()

    # Renommer colonnes avec noms
    ret_display=ret_matrix.rename(columns=names)

    # === VOLATILITE INDIVIDUELLE ===
    sec("Volatilite annualisee par position")
    vols=ret_matrix.std()*np.sqrt(252)*100
    vol_df=pd.DataFrame({"Ticker":vols.index,"Valeur":[names.get(t,t) for t in vols.index],
        "Vol annualisee (%)":[round(v,1) for v in vols.values]}).sort_values("Vol annualisee (%)",ascending=True)

    c1,c2=st.columns([2,1])
    with c1:
        fig_vol=go.Figure(go.Bar(x=vol_df["Vol annualisee (%)"],y=vol_df["Valeur"],orientation="h",
            marker_color=[CL[i%len(CL)] for i in range(len(vol_df))],
            text=[f"{v:.1f}%" for v in vol_df["Vol annualisee (%)"]],textposition="outside"))
        fig_vol.update_layout(**PL,height=max(350,len(vol_df)*50),yaxis=dict(automargin=True),
            xaxis_title="Volatilite annualisee (%)")
        st.plotly_chart(fig_vol,use_container_width=True)
    with c2:
        st.dataframe(vol_df[["Valeur","Vol annualisee (%)"]],hide_index=True,height=min(500,45+len(vol_df)*35))
        avg_vol=vols.mean()
        st.metric("Volatilite moyenne",f"{avg_vol:.1f}%")

    # === RENDEMENTS ANNUALISES REELS ===
    sec("Rendement annualise reel (historique)")
    ann_rets=((1+ret_matrix.mean())**252-1)*100
    ann_df=pd.DataFrame({"Valeur":[names.get(t,t) for t in ann_rets.index],
        "Rdt annualise (%)":[round(v,1) for v in ann_rets.values],
        "Vol (%)":[round(v,1) for v in vols.values]}).sort_values("Rdt annualise (%)",ascending=False)
    st.dataframe(ann_df,hide_index=True)

    # Scatter rendement vs volatilite
    sec("Rendement vs Volatilite (frontiere)")
    fig_rv=px.scatter(ann_df,x="Vol (%)",y="Rdt annualise (%)",text="Valeur",
        color_discrete_sequence=CL,size_max=15)
    fig_rv.update_traces(textposition="top center",textfont_size=10,marker=dict(size=12))
    fig_rv.add_hline(y=0,line_dash="dash",line_color="#94a3b8")
    fig_rv.update_layout(**PL,height=450,xaxis_title="Volatilite annualisee (%)",
        yaxis_title="Rendement annualise (%)"); st.plotly_chart(fig_rv,use_container_width=True)

    # === MATRICE DE CORRELATION ===
    sec("Matrice de correlation")
    corr=ret_display.corr()

    fig_corr=go.Figure(go.Heatmap(
        z=corr.values,x=corr.columns,y=corr.index,
        colorscale=[[0,"#ef4444"],[0.5,"#ffffff"],[1,"#3b82f6"]],
        zmin=-1,zmax=1,
        text=np.round(corr.values,2),texttemplate="%{text}",textfont=dict(size=10),
        hovertemplate="Correlation %{x} vs %{y}: %{z:.2f}<extra></extra>"))
    fig_corr.update_layout(**PL,height=max(450,len(corr)*45+100),
        xaxis=dict(tickangle=45),yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_corr,use_container_width=True)

    # Stats correlation
    mask=np.triu(np.ones_like(corr,dtype=bool),k=1)
    upper=corr.where(mask)
    pairs=[]
    for i in range(len(upper.columns)):
        for j in range(i+1,len(upper.columns)):
            pairs.append({"Paire":f"{upper.columns[i]} / {upper.columns[j]}",
                "Correlation":round(upper.iloc[i,j],3)})
    pdf=pd.DataFrame(pairs).sort_values("Correlation",ascending=False)

    c1,c2=st.columns(2)
    with c1:
        sec("Paires les plus correlees")
        st.dataframe(pdf.head(10),hide_index=True)
    with c2:
        sec("Paires les moins correlees")
        st.dataframe(pdf.tail(10).sort_values("Correlation"),hide_index=True)

    avg_corr=pdf["Correlation"].mean()
    if avg_corr>0.6: st.error(f"Correlation moyenne: {avg_corr:.2f} — Portefeuille peu diversifie")
    elif avg_corr>0.4: st.warning(f"Correlation moyenne: {avg_corr:.2f} — Diversification moderee")
    else: st.success(f"Correlation moyenne: {avg_corr:.2f} — Bonne diversification")

    # === ROLLING VOLATILITY ===
    sec("Volatilite glissante du portefeuille (60 jours)")
    pf_val=pf_value(portfolio,sd2)
    if not pf_val.empty:
        roll_vol=pf_val.pct_change().rolling(60).std()*np.sqrt(252)*100
        fig_rv2=go.Figure()
        fig_rv2.add_trace(go.Scatter(x=roll_vol.index,y=roll_vol.values,
            line=dict(color="#f59e0b",width=2),fill="tozeroy",fillcolor="rgba(245,158,11,0.08)"))
        fig_rv2.update_layout(**PL,height=350,yaxis_title="Volatilite annualisee (%)")
        st.plotly_chart(fig_rv2,use_container_width=True)


# =============================================================
# PAGE 5 : ALERTES
# =============================================================
elif page=="Alertes":
    hdr("Alertes","Suivi des seuils et signaux")
    alerts=load_al()
    all_tk=sorted(set(tk for p in PF.values() for tk in p.keys()))
    if not all_tk: st.info("Importez des positions."); st.stop()

    sec("Creer une alerte")
    c1,c2,c3,c4=st.columns([3,3,2,2])
    with c1: a_tk=st.selectbox("Ticker",all_tk)
    with c2: a_type=st.selectbox("Type",["Prix au-dessus","Prix en-dessous","PnL % au-dessus","PnL % en-dessous"])
    with c3: a_val=st.number_input("Seuil",value=0.0,step=1.0)
    with c4:
        st.write(""); st.write("")
        if st.button("Ajouter",type="primary",use_container_width=True):
            alerts.append({"ticker":a_tk,"type":a_type,"value":a_val,
                "created":datetime.now().strftime("%d/%m/%Y %H:%M")})
            save_al(alerts); st.rerun()

    sec("Alertes actives")
    if not alerts: st.info("Aucune alerte.")
    else:
        cp=yf_prices(tuple(set(a["ticker"] for a in alerts)))
        for i,a in enumerate(alerts):
            cur=cp.get(a["ticker"],0); triggered=False
            if "Prix au-dessus"==a["type"] and cur>a["value"]: triggered=True
            elif "Prix en-dessous"==a["type"] and cur<a["value"]: triggered=True
            c1,c2,c3=st.columns([6,2,1])
            with c1: st.markdown(f"**{a['ticker']}** — {a['type']} **{a['value']}** (cours: {cur:.2f}) `{'DECLENCHEE' if triggered else 'En attente'}`")
            with c3:
                if st.button("Suppr",key=f"d{i}"): alerts.pop(i); save_al(alerts); st.rerun()

    sec("Signaux automatiques")
    portfolio=get_pf()
    if portfolio:
        pr=yf_prices(tuple(portfolio.keys())); has=False
        for tk,inf in portfolio.items():
            cur=pr.get(tk,0)
            if cur==0: continue
            pnl=((cur-inf["buy_price"])/inf["buy_price"])*100
            if pnl>30: st.success(f"{inf['name']}: **{pnl:+.1f}%** — Prise de benefice ?"); has=True
            elif pnl<-15: st.error(f"{inf['name']}: **{pnl:+.1f}%** — Surveiller"); has=True
        if not has: st.info("Aucun signal.")


# =============================================================
# PAGE 6 : RECOMMANDATIONS
# =============================================================
elif page=="Recommandations":
    hdr("Recommandations",f"Analyse {G}")
    portfolio=get_pf()
    if not portfolio: st.info("Aucune position."); st.stop()

    tks=list(portfolio.keys())
    with st.spinner("Analyse..."):
        prices=yf_prices(tuple(tks)); fundas=yf_info(tuple(tks))

    tv=sum(prices.get(tk,0)*inf["qty"] for tk,inf in portfolio.items())
    pos=[]
    for tk,inf in portfolio.items():
        cur=prices.get(tk,0); f=fundas.get(tk,{}); t=f.get("target")
        pos.append({"name":inf["name"],"tk":tk,"val":cur*inf["qty"],
            "w":(cur*inf["qty"]/tv*100) if tv else 0,"sector":f.get("sector","N/A"),
            "pe":f.get("pe"),"reco":f.get("reco","N/A"),"target":t,
            "rdt":((t-cur)/cur*100) if t and cur else None,
            "pnl":((cur-inf["buy_price"])/inf["buy_price"])*100 if inf["buy_price"] else 0})
    dfp=pd.DataFrame(pos).sort_values("w",ascending=False)

    sec("Consensus analystes")
    for _,r in dfp.iterrows():
        rc=str(r["reco"]).upper()
        msg=f"**{r['name']}** : {rc}"
        if r["rdt"]: msg+=f" | Rdt espere: {r['rdt']:+.1f}%"
        if rc in ["BUY","STRONG_BUY"]: st.success(msg)
        elif rc in ["SELL","STRONG_SELL"]: st.error(msg)
        else: st.info(msg)

    c1,c2=st.columns(2)
    with c1:
        sec("Concentration")
        mw=dfp["w"].max()
        if mw>40: st.error(f"RISQUE: {dfp.iloc[0]['name']}={mw:.1f}%")
        elif mw>25: st.warning(f"Attention: {dfp.iloc[0]['name']}={mw:.1f}%")
        else: st.success(f"OK: max={mw:.1f}%")
        fig=go.Figure(go.Bar(x=dfp["w"],y=dfp["name"],orientation="h",marker_color="#6366f1",
            text=[f"{w:.1f}%" for w in dfp["w"]],textposition="outside"))
        fig.update_layout(**PL,height=max(300,len(dfp)*50),yaxis=dict(automargin=True))
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        sec("Secteurs")
        ds=dfp.groupby("sector")["w"].sum().sort_values(ascending=False); ns=len(ds)
        if ns<=2: st.error(f"{ns} secteurs")
        elif ns<=4: st.warning(f"{ns} secteurs")
        else: st.success(f"{ns} secteurs")
        st.plotly_chart(px.bar(x=ds.index,y=ds.values,color=ds.values,color_continuous_scale="Viridis",
            labels={"x":"","y":"Poids %"}).update_layout(**PL,height=350),use_container_width=True)

    sec("Actions recommandees")
    recs=[]
    for _,r in dfp.iterrows():
        if r["pnl"]>50: recs.append(("warning",f"Benefice sur **{r['name']}** ({r['pnl']:+.1f}%)"))
        if r["pnl"]<-20: recs.append(("error",f"Reevaluer **{r['name']}** ({r['pnl']:+.1f}%)"))
        if r["pe"] and r["pe"]>40: recs.append(("info",f"PE eleve **{r['name']}** ({r['pe']:.0f}x)"))
    if recs:
        for typ,msg in recs: getattr(st,typ)(msg)
    else: st.success("Portefeuille equilibre !")

    sec("Score")
    sc=100
    if ns<3: sc-=30
    elif ns<5: sc-=15
    if mw>40: sc-=25
    elif mw>30: sc-=10
    if len(portfolio)<4: sc-=20
    sc=max(0,min(100,sc))
    fsc=go.Figure(go.Indicator(mode="gauge+number+delta",value=sc,
        delta={"reference":70},
        gauge={"axis":{"range":[0,100]},"bar":{"color":"#6366f1"},
            "steps":[{"range":[0,40],"color":"rgba(239,68,68,0.1)"},
                     {"range":[40,70],"color":"rgba(245,158,11,0.1)"},
                     {"range":[70,100],"color":"rgba(16,185,129,0.1)"}]}))
    fsc.update_layout(**PL,height=280); st.plotly_chart(fsc,use_container_width=True)


# =============================================================
# PAGE 7 : GESTION
# =============================================================
elif page=="Gestion":
    hdr("Gestion des donnees","Import, export et modification")
    tab1,tab2,tab3=st.tabs(["Ajouter","Importer Excel/CSV","Exporter"])

    with tab1:
        c1,c2,c3=st.columns(3)
        with c1: am=st.selectbox("Membre",FAMILY,key="am")
        with c2: atk=st.text_input("Ticker Yahoo (ex: TTE.PA)",key="atk").upper()
        with c3: an=st.text_input("Nom",key="an")
        c4,c5,c6=st.columns(3)
        with c4: aq=st.number_input("Quantite",min_value=1,value=10,key="aq")
        with c5: ap=st.number_input("Prix achat (EUR)",min_value=0.01,value=100.0,step=0.01,key="ap")
        with c6: ad=st.date_input("Date achat",key="ad")
        if st.button("Ajouter",type="primary"):
            if am and atk and an:
                PF.setdefault(am,{})[atk]={"qty":int(aq),"buy_price":float(ap),
                    "buy_date":ad.strftime("%Y-%m-%d"),"name":an}
                st.session_state.pf=PF; save_pf(PF); st.success(f"OK: {an}"); st.rerun()

    with tab2:
        st.markdown("**Format courtier**: Valeur | Code | Place | Date | Qte | PRU | Cours | Valorisation")
        imp_m=st.selectbox("Membre",FAMILY,key="im")
        uploaded=st.file_uploader("Fichier",type=["csv","xlsx","xls"],key="up")
        if uploaded:
            try:
                idf=pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded)
                idf=idf.dropna(how="all")
                idf=idf[idf.iloc[:,0].notna() & (idf.iloc[:,0].astype(str).str.strip()!="") &
                    (idf.iloc[:,0].astype(str)!="None") &
                    ~idf.iloc[:,0].astype(str).str.upper().str.contains("LIQUIDIT")]
                idf=idf[pd.to_numeric(idf.iloc[:,4],errors="coerce")>0]
                st.dataframe(idf,hide_index=True)
                st.session_state["idata"]=idf.to_dict(); st.session_state["imem"]=imp_m
            except Exception as e: st.error(f"Erreur: {e}")

        if "idata" in st.session_state:
            mode=st.radio("Mode",["Ajouter","Remplacer positions du membre"])
            if st.button("CONFIRMER",type="primary"):
                idf=pd.DataFrame(st.session_state["idata"])
                im=st.session_state.get("imem",FAMILY[0])
                PF.setdefault(im,{})
                if "Remplacer" in mode: PF[im]={}
                ct=er=0
                for _,row in idf.iterrows():
                    try:
                        nm=str(row.iloc[0]).strip(); qt=int(float(row.iloc[4]))
                        pru=float(row.iloc[5]); dv=row.iloc[3]
                        dt=dv.strftime("%Y-%m-%d") if isinstance(dv,pd.Timestamp) else str(dv)[:10]
                        if qt<=0 or pru<=0: continue
                        PF[im][find_tk(nm)]={"qty":qt,"buy_price":pru,"buy_date":dt,"name":nm}; ct+=1
                    except: er+=1
                st.session_state.pf=PF; save_pf(PF)
                if "idata" in st.session_state: del st.session_state["idata"]
                st.success(f"{ct} positions pour {im}"); st.rerun()

    with tab3:
        if st.button("Exporter CSV"):
            rows=[]
            for m in FAMILY:
                for tk,inf in PF.get(m,{}).items():
                    rows.append({"Membre":m,"Ticker":tk,"Nom":inf["name"],
                        "Qte":inf["qty"],"Prix":inf["buy_price"],"Date":inf["buy_date"]})
            edf=pd.DataFrame(rows)
            st.download_button("Telecharger",edf.to_csv(index=False),"faure.csv","text/csv")
            st.dataframe(edf,hide_index=True)

    st.divider(); sec("Supprimer une position")
    c1,c2,c3=st.columns([2,4,2])
    with c1: dm=st.selectbox("Membre",FAMILY,key="dm")
    if PF.get(dm):
        with c2:
            opts=[f"{tk} — {inf['name']}" for tk,inf in PF[dm].items()]
            dp=st.selectbox("Position",opts,key="dp")
        with c3:
            st.write(""); st.write("")
            if st.button("Supprimer",use_container_width=True):
                del PF[dm][dp.split(" — ")[0]]
                st.session_state.pf=PF; save_pf(PF); st.rerun()
    else: st.info(f"Aucune position pour {dm}.")
