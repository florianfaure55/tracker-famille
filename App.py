import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json, os, urllib.request, zipfile, io

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
    "CAPGEMINI":"CAP.PA","ALSTOM":"ALO.PA","DASSAULT SYSTEMES":"DSY.PA",
    "ENGIE":"ENGI.PA","RENAULT":"RNO.PA","STELLANTIS":"STLAP.PA",
    "STELLANTIS NV":"STLAP.PA","AIR LIQUIDE":"AI.PA","TOTALENERGIES":"TTE.PA",
    "TOTAL":"TTE.PA","BNP PARIBAS":"BNP.PA","LVMH":"MC.PA",
    "L'OREAL":"OR.PA","L OREAL":"OR.PA","LOREAL":"OR.PA",
    "HERMES":"RMS.PA","HERMES INTERNATIONAL":"RMS.PA","ORANGE":"ORA.PA",
    "SCHNEIDER":"SU.PA","SCHNEIDER ELECTRIC":"SU.PA","AXA":"CS.PA",
    "VINCI":"DG.PA","SANOFI":"SAN.PA","SAFRAN":"SAF.PA",
    "SAINT-GOBAIN":"SGO.PA","SAINT GOBAIN":"SGO.PA","SOCIETE GENERALE":"GLE.PA",
    "CREDIT AGRICOLE":"ACA.PA","DANONE":"BN.PA","PERNOD RICARD":"RI.PA",
    "MICHELIN":"ML.PA","KERING":"KER.PA","BOUYGUES":"EN.PA",
    "CHRISTIAN DIOR":"CDI.PA","VEOLIA":"VIE.PA","LEGRAND":"LR.PA",
    "THALES":"HO.PA","PUBLICIS":"PUB.PA","ARKEMA":"AKE.PA",
    "TELEPERFORMANCE":"TEP.PA","EUROFINS":"ERF.PA","STMICROELECTRONICS":"STM.PA",
    "WORLDLINE":"WLN.PA","CARREFOUR":"CA.PA","ACCOR":"AC.PA",
    "VIVENDI":"VIV.PA","EDENRED":"EDEN.PA","ESSILOR":"EL.PA",
    "ESSILORLUXOTTICA":"EL.PA","AIRBUS":"AIR.PA","VALEO":"FR.PA",
    "NEXITY":"NXI.PA","EIFFAGE":"FGR.PA","AMUNDI":"AMUN.PA",
    "RUBIS":"RUI.PA","NEXANS":"NEX.PA","IPSEN":"IPN.PA",
    "BIOMERIEUX":"BIM.PA","BUREAU VERITAS":"BVI.PA","SODEXO":"SW.PA",
    "DASSAULT AVIATION":"AM.PA","SCOR":"SCR.PA","REMY COINTREAU":"RCO.PA",
    "FAURECIA":"EO.PA","FORVIA":"FRVIA.PA","UNIBAIL":"URW.PA",
    "GECINA":"GFC.PA","COVIVIO":"COV.PA",
}

# =============================================================
# CSS
# =============================================================
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#0f172a,#1e293b)}
section[data-testid="stSidebar"] *{color:#e2e8f0!important}
section[data-testid="stSidebar"] hr{border-color:rgba(148,163,184,.2)!important}
.kr{display:flex;gap:12px;margin-bottom:1.5rem;flex-wrap:wrap}
.k{flex:1;min-width:140px;border-radius:16px;padding:18px 14px;color:#fff;position:relative;overflow:hidden}
.k::before{content:'';position:absolute;top:-30px;right:-30px;width:80px;height:80px;border-radius:50%;background:rgba(255,255,255,.1)}
.k .l{font-size:.68rem;font-weight:500;text-transform:uppercase;letter-spacing:.08em;opacity:.85;margin-bottom:5px}
.k .v{font-size:1.4rem;font-weight:700;line-height:1.2}
.k .s{font-size:.72rem;opacity:.7;margin-top:3px}
.kb{background:linear-gradient(135deg,#3b82f6,#6366f1)}
.kg{background:linear-gradient(135deg,#10b981,#059669)}
.kr2{background:linear-gradient(135deg,#ef4444,#dc2626)}
.ko{background:linear-gradient(135deg,#f59e0b,#d97706)}
.kp{background:linear-gradient(135deg,#8b5cf6,#7c3aed)}
.kt{background:linear-gradient(135deg,#14b8a6,#0d9488)}
.ks{background:linear-gradient(135deg,#475569,#334155)}
.mc{border-radius:16px;padding:20px;color:#fff;margin-bottom:8px}
.mc .n{font-size:.8rem;font-weight:500;text-transform:uppercase;letter-spacing:.05em;opacity:.85}
.mc .v{font-size:1.3rem;font-weight:700;margin:4px 0}
.mc .p{font-size:.85rem;font-weight:600}
.sc{font-size:1.1rem;font-weight:600;color:#1e293b;margin:1.8rem 0 .8rem;padding-bottom:8px;border-bottom:2px solid #6366f1}
.ph h1{font-size:1.7rem;font-weight:700;color:#0f172a;margin:0}
.ph p{font-size:.85rem;color:#64748b;margin:4px 0 0}
.hl{height:3px;background:linear-gradient(90deg,#6366f1,#3b82f6,#06b6d4);border-radius:2px;margin:10px 0 20px}
#MainMenu,footer,header{visibility:hidden}
</style>""",unsafe_allow_html=True)

def K(l,v,s="",c="kb"):
    sb=f'<div class="s">{s}</div>' if s else ""
    return f'<div class="k {c}"><div class="l">{l}</div><div class="v">{v}</div>{sb}</div>'
def H(t,s=""): st.markdown(f'<div class="ph"><h1>{t}</h1><p>{s}</p></div><div class="hl"></div>',unsafe_allow_html=True)
def S(t): st.markdown(f'<div class="sc">{t}</div>',unsafe_allow_html=True)
def cc(v): return "kg" if v>=0 else "kr2"

PL=dict(font=dict(family="Inter"),plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(t=30,b=30,l=20,r=20),hovermode="x unified",
    legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="center",x=0.5))
CO=["#6366f1","#3b82f6","#06b6d4","#10b981","#f59e0b","#ef4444","#8b5cf6","#ec4899","#14b8a6","#f97316"]

# =============================================================
# PERSISTENCE
# =============================================================
def load_pf():
    if os.path.exists(DATA_FILE):
        d=json.load(open(DATA_FILE));[d.setdefault(m,{}) for m in FAMILY];return d
    return {m:{} for m in FAMILY}
def save_pf(d): json.dump(d,open(DATA_FILE,"w"),indent=2)
def load_al(): return json.load(open(ALERTS_FILE)) if os.path.exists(ALERTS_FILE) else []
def save_al(a): json.dump(a,open(ALERTS_FILE,"w"),indent=2)
def find_tk(name):
    up=name.upper().strip()
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
# YAHOO FINANCE
# =============================================================
@st.cache_data(ttl=300)
def yf_prices(tickers):
    p={};tl=[t for t in tickers if t]
    if not tl: return p
    try:
        d=yf.download(tl,period="5y",group_by="ticker",progress=False)
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
                "reco":"recommendationKey","roe":"returnOnEquity","margin":"profitMargins"}.items()}
            r[t]["sector"]=r[t].get("sector") or "N/A";r[t]["reco"]=r[t].get("reco") or "N/A"
        except: r[t]={"sector":"N/A","reco":"N/A"}
    return r

@st.cache_data(ttl=600)
def yf_hist(tickers,start):
    try: return yf.download(list(tickers),start=start,progress=False,group_by="ticker")
    except: return pd.DataFrame()

@st.cache_data(ttl=600)
def yf_bench(start):
    r={}
    for tk,nm in BENCHMARKS.items():
        try: d=yf.download(tk,start=start,progress=False);r[nm]=d["Close"].squeeze()
        except: r[nm]=pd.Series()
    return r

@st.cache_data(ttl=600)
def yf_returns(tickers,start):
    try:
        d=yf.download(list(tickers),start=start,progress=False,group_by="ticker")
        if len(tickers)==1: c=d["Close"].to_frame(tickers[0])
        else: c=pd.DataFrame({t:d[t]["Close"] for t in tickers if t in d.columns.get_level_values(0)})
        return c.pct_change().dropna()
    except: return pd.DataFrame()

@st.cache_data(ttl=600)
def yf_rdt_5y(tickers):
    """Rendement annualise reel 5 ans."""
    r={};start=(datetime.now()-timedelta(days=1825)).strftime("%Y-%m-%d")
    try:
        d=yf.download(list(tickers),start=start,progress=False,group_by="ticker")
        for t in tickers:
            try:
                cl=d["Close"].dropna() if len(tickers)==1 else d[t]["Close"].dropna()
                if len(cl)>100:
                    p0=float(cl.iloc[0]);p1=float(cl.iloc[-1])
                    y=(cl.index[-1]-cl.index[0]).days/365.25
                    r[t]=((p1/p0)**(1/y)-1)*100 if p0>0 and y>0.5 else None
                else: r[t]=None
            except: r[t]=None
    except:
        for t in tickers: r[t]=None
    return r

def pf_val(pf,start):
    tks=list(pf.keys())
    if not tks: return pd.Series()
    h=yf_hist(tuple(tks),start)
    if h.empty: return pd.Series()
    v=pd.Series(0.0,index=h.index)
    for tk,inf in pf.items():
        try:
            c=h["Close"].squeeze() if len(tks)==1 else h[tk]["Close"].squeeze()
            c=c.ffill();bd=pd.Timestamp(inf["buy_date"]);c[c.index<bd]=inf["buy_price"];v+=c*inf["qty"]
        except: pass
    return v

def pf_inv(pf,idx):
    inv=pd.Series(0.0,index=idx)
    for tk,inf in pf.items(): inv[idx>=pd.Timestamp(inf["buy_date"])]+=inf["buy_price"]*inf["qty"]
    return inv

def mbr_perf(mp,pr):
    tv=ti=0
    for tk,inf in mp.items(): c=pr.get(tk,0);tv+=c*inf["qty"];ti+=inf["buy_price"]*inf["qty"]
    return tv,ti,tv-ti,((tv-ti)/ti*100) if ti else 0

# =============================================================
# FAMA-FRENCH
# =============================================================
@st.cache_data(ttl=86400)
def dl_ff():
    url="https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/Europe_3_Factors_Daily_CSV.zip"
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
        resp=urllib.request.urlopen(req,timeout=30)
        zf=zipfile.ZipFile(io.BytesIO(resp.read()))
        csv_name=[f for f in zf.namelist() if f.lower().endswith('.csv')][0]
        raw=zf.open(csv_name).read().decode('utf-8').split('\n')
        rows=[]
        for line in raw:
            s=line.strip()
            if not s: continue
            p=[x.strip() for x in s.split(',')]
            if len(p)>=5 and p[0].isdigit() and len(p[0])==8:
                try: rows.append({"date":p[0],"Mkt-RF":float(p[1]),"SMB":float(p[2]),"HML":float(p[3]),"RF":float(p[4])})
                except: continue
        df=pd.DataFrame(rows);df["date"]=pd.to_datetime(df["date"],format="%Y%m%d")
        df.set_index("date",inplace=True);return df/100
    except: return pd.DataFrame()

def ols(y,X):
    n,k=X.shape;b,_,_,_=np.linalg.lstsq(X,y,rcond=None)
    res=y-X@b;ssr=np.sum(res**2);sst=np.sum((y-y.mean())**2)
    r2=1-ssr/sst;s2=ssr/(n-k)
    try: se=np.sqrt(np.diag(s2*np.linalg.inv(X.T@X)))
    except: se=np.zeros(k)
    return b,b/np.where(se>0,se,1),r2

def ff_reg(ret,ff):
    ci=ret.index.intersection(ff.index)
    if len(ci)<60: return None
    y=(ret.loc[ci]-ff.loc[ci,"RF"]).values
    X=np.column_stack([np.ones(len(ci)),ff.loc[ci,"Mkt-RF"].values,ff.loc[ci,"SMB"].values,ff.loc[ci,"HML"].values])
    b,t,r2=ols(y,X)
    return {"alpha":b[0]*252*100,"mkt":b[1],"smb":b[2],"hml":b[3],
        "t_a":t[0],"t_m":t[1],"t_s":t[2],"t_h":t[3],"r2":r2,"n":len(ci)}

# =============================================================
# LOGIN
# =============================================================
if "logged" not in st.session_state: st.session_state.logged=False
if "pf" not in st.session_state: st.session_state.pf=load_pf()

if not st.session_state.logged:
    st.markdown('<div style="display:flex;justify-content:center;align-items:center;min-height:80vh"><div style="text-align:center"><div style="font-size:3rem;font-weight:800;margin-bottom:8px">FAMILLE FAURE</div><div style="font-size:1rem;color:#64748b;margin-bottom:2rem">Tracker Portefeuilles</div></div></div>',unsafe_allow_html=True)
    _,c,_=st.columns([1.5,1,1.5])
    with c:
        pw=st.text_input("",type="password",placeholder="Mot de passe",label_visibility="collapsed")
        if st.button("Connexion",type="primary",use_container_width=True):
            if pw==PASS: st.session_state.logged=True;st.rerun()
            else: st.error("Mot de passe incorrect")
    st.stop()

# =============================================================
# SIDEBAR
# =============================================================
PF=st.session_state.pf
with st.sidebar:
    st.markdown("### FAMILLE FAURE");st.caption("Tracker Portefeuilles");st.divider()
    G=st.selectbox("MEMBRE",["Consolide"]+FAMILY);st.divider()
    page=st.radio("NAVIGATION",["Dashboard","Fondamentaux","Performance",
        "Volatilite / Correlation","Fama-French","Alertes","Recommandations","Gestion"])
    st.divider()
    st.caption(f"{len(FAMILY)} membres | {sum(len(p) for p in PF.values())} positions")
    st.caption(datetime.now().strftime("%d/%m/%Y %H:%M"));st.divider()
    if st.button("Actualiser",use_container_width=True): st.cache_data.clear();st.rerun()
    if st.button("Deconnexion",use_container_width=True): st.session_state.logged=False;st.rerun()

def get_pf():
    if G=="Consolide":
        c={}
        for m in FAMILY:
            for tk,inf in PF.get(m,{}).items():
                if tk not in c: c[tk]={"qty":0,"tc":0,"bd":inf["buy_date"],"name":inf["name"]}
                c[tk]["qty"]+=inf["qty"];c[tk]["tc"]+=inf["buy_price"]*inf["qty"]
                c[tk]["bd"]=min(c[tk]["bd"],inf["buy_date"])
        return {t:{"qty":v["qty"],"buy_price":v["tc"]/v["qty"],"buy_date":v["bd"],"name":v["name"]} for t,v in c.items()}
    return PF.get(G,{})


# =============================================================
# DASHBOARD
# =============================================================
if page=="Dashboard":
    H("Dashboard",f"Vue d'ensemble — {G}")
    pf=get_pf()
    if not pf: st.info("Aucune position. Va dans Gestion pour importer.");st.stop()
    tks=list(pf.keys());all_tks=list(set(tk for p in PF.values() for tk in p.keys()))
    with st.spinner("Chargement..."):
        pr=yf_prices(tuple(all_tks if all_tks else tks));fu=yf_info(tuple(tks));r5=yf_rdt_5y(tuple(tks))

    # Cartes membres
    if G=="Consolide":
        S("Performance par membre")
        cols=st.columns(4);mc=["kb","kg","ko","kp"]
        for i,m in enumerate(FAMILY):
            mp=PF.get(m,{})
            with cols[i]:
                if mp:
                    tv,ti,tp,tpct=mbr_perf(mp,pr)
                    st.markdown(f'<div class="mc {mc[i]}"><div class="n">{m}</div><div class="v">{tv:,.0f} EUR</div><div class="p" style="color:{"#bbf7d0" if tp>=0 else "#fecaca"}">{tp:+,.0f} EUR ({tpct:+.1f}%)</div><div style="font-size:.7rem;opacity:.6;margin-top:4px">{len(mp)} positions</div></div>',unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="mc ks"><div class="n">{m}</div><div class="v">—</div></div>',unsafe_allow_html=True)

    rows=[];ti=tv=td=0
    for tk,inf in pf.items():
        cur=pr.get(tk,0);val=cur*inf["qty"];inv=inf["buy_price"]*inf["qty"]
        pnl=val-inv;pct=(pnl/inv*100) if inv else 0
        f=fu.get(tk,{});dy=f.get("dy")
        if dy and dy<1: td+=val*dy
        elif dy and dy>=1: td+=val*(dy/100)
        rdt=r5.get(tk)
        rows.append({"Valeur":inf["name"],"Ticker":tk,"Secteur":f.get("sector","N/A"),
            "Qte":inf["qty"],"PRU":round(inf["buy_price"],2),"Cours":round(cur,2),
            "Valorisation":round(val,0),"PnL (EUR)":round(pnl,0),"PnL (%)":round(pct,1),
            "Rdt 5a ann. (%)":round(rdt,1) if rdt else None,
            "PE":round(f["pe"],1) if f.get("pe") else None,
            "Div (%)":round(dy*100,1) if dy and dy<1 else None,
            "Beta":round(f["beta"],2) if f.get("beta") else None})
        ti+=inv;tv+=val
    tp=tv-ti;tpct=(tp/ti*100) if ti else 0
    rw=[(r["Rdt 5a ann. (%)"],r["Valorisation"]) for r in rows if r["Rdt 5a ann. (%)"] is not None]
    rdt_g=sum(r*w for r,w in rw)/sum(w for _,w in rw) if rw else 0

    # Vol ponderee
    vol_pf=0
    try:
        rm=yf_returns(tks,(datetime.now()-timedelta(days=730)).strftime("%Y-%m-%d"))
        if not rm.empty and len(rm)>60:
            vt=[t for t in tks if t in rm.columns]
            w=np.array([pr.get(t,0)*pf[t]["qty"]/tv for t in vt]) if tv>0 else np.zeros(len(vt))
            if w.sum()>0: w/=w.sum();vol_pf=float(np.sqrt(w@(rm[vt].cov()*252).values@w)*100)
    except: pass

    dy_pct=(td/tv*100) if tv and td/tv<0.2 else 0
    S("Vue globale")
    st.markdown(f'<div class="kr">{K("VALORISATION",f"{tv:,.0f} EUR",f"{len(pf)} positions","kb")}{K("INVESTI",f"{ti:,.0f} EUR","","kp")}{K("PLUS-VALUE",f"{tp:+,.0f} EUR",f"{tpct:+.1f}%",cc(tp))}{K("RDT 5 ANS ANN.",f"{rdt_g:+.1f}%","Historique reel","kt")}{K("VOLATILITE",f"{vol_pf:.1f}%","Ponderee 2a","ko")}{K("DIVIDENDES/AN",f"{td:,.0f} EUR",f"Yield {dy_pct:.1f}%" if dy_pct>0 else "","ks")}</div>',unsafe_allow_html=True)

    S("Positions")
    df=pd.DataFrame(rows).sort_values("Valorisation",ascending=False)
    st.dataframe(df,hide_index=True,height=min(700,45+len(df)*35))

    c1,c2=st.columns(2)
    with c1:
        S("Par valeur")
        fig=px.pie(df,values="Valorisation",names="Valeur",hole=.5,color_discrete_sequence=CO)
        fig.update_traces(textposition="inside",textinfo="percent+label",textfont_size=10)
        fig.update_layout(**PL,showlegend=False,height=360);st.plotly_chart(fig,use_container_width=True)
    with c2:
        S("Par secteur")
        ds=df.groupby("Secteur")["Valorisation"].sum().reset_index()
        fig=px.pie(ds,values="Valorisation",names="Secteur",hole=.5,color_discrete_sequence=CO)
        fig.update_traces(textposition="inside",textinfo="percent+label",textfont_size=10)
        fig.update_layout(**PL,showlegend=False,height=360);st.plotly_chart(fig,use_container_width=True)

    c1,c2=st.columns(2)
    with c1:
        S("PnL par position")
        d2=df.sort_values("PnL (%)")
        fig=go.Figure(go.Bar(x=d2["PnL (%)"],y=d2["Valeur"],orientation="h",
            marker_color=["#ef4444" if x<0 else "#10b981" for x in d2["PnL (%)"]],
            text=[f"{x:+.1f}%" for x in d2["PnL (%)"]],textposition="outside"))
        fig.update_layout(**PL,height=max(300,len(d2)*45),yaxis=dict(automargin=True))
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        S("Rendement annualise 5 ans")
        d3=df.dropna(subset=["Rdt 5a ann. (%)"]).sort_values("Rdt 5a ann. (%)")
        if not d3.empty:
            fig=go.Figure(go.Bar(x=d3["Rdt 5a ann. (%)"],y=d3["Valeur"],orientation="h",
                marker_color=["#ef4444" if x<0 else "#3b82f6" for x in d3["Rdt 5a ann. (%)"]],
                text=[f"{x:+.1f}%" for x in d3["Rdt 5a ann. (%)"]],textposition="outside"))
            fig.update_layout(**PL,height=max(300,len(d3)*45),yaxis=dict(automargin=True))
            st.plotly_chart(fig,use_container_width=True)

    if G=="Consolide":
        S("Par membre")
        mv=[{"Membre":m,"Valeur":round(sum(pr.get(tk,0)*inf["qty"] for tk,inf in PF.get(m,{}).items()),0)} for m in FAMILY]
        mv=[x for x in mv if x["Valeur"]>0]
        if mv:
            fig=px.pie(pd.DataFrame(mv),values="Valeur",names="Membre",hole=.5,color_discrete_sequence=CO)
            fig.update_traces(textposition="inside",textinfo="percent+label+value")
            fig.update_layout(**PL,height=360);st.plotly_chart(fig,use_container_width=True)


# =============================================================
# FONDAMENTAUX
# =============================================================
elif page=="Fondamentaux":
    H("Analyse fondamentale",f"Yahoo Finance — {G}")
    pf=get_pf()
    if not pf: st.info("Aucune position.");st.stop()
    tks=list(pf.keys())
    with st.spinner("Chargement..."): pr=yf_prices(tuple(tks));fu=yf_info(tuple(tks));r5=yf_rdt_5y(tuple(tks))

    for tk,inf in pf.items():
        cur=pr.get(tk,0);f=fu.get(tk,{});rdt=r5.get(tk)
        pnl=((cur-inf["buy_price"])/inf["buy_price"])*100 if inf["buy_price"] else 0
        st.divider();st.markdown(f"#### {inf['name']}  `{tk}`")
        st.caption(f"{f.get('sector','N/A')} | {f.get('industry','N/A')}")
        c1,c2,c3,c4,c5,c6=st.columns(6)
        c1.metric("Cours",f"{cur:.2f}");c2.metric("PnL",f"{pnl:+.1f}%")
        c3.metric("Rdt 5a",f"{rdt:+.1f}%/an" if rdt else "N/A")
        c4.metric("P/E",f"{f['pe']:.1f}" if f.get("pe") else "N/A")
        c5.metric("Div",f"{f['dy']*100:.1f}%" if f.get("dy") and f["dy"]<1 else "N/A")
        c6.metric("Beta",f"{f['beta']:.2f}" if f.get("beta") else "N/A")
        c1,c2,c3,c4,c5,c6=st.columns(6)
        c1.metric("Cap.",fmt(f.get("mcap")));c2.metric("Haut 52s",f"{f['h52']:.0f}" if f.get("h52") else "N/A")
        c3.metric("Bas 52s",f"{f['l52']:.0f}" if f.get("l52") else "N/A")
        c4.metric("Reco",str(f.get("reco","N/A")).upper())
        c5.metric("ROE",f"{f['roe']*100:.1f}%" if f.get("roe") else "N/A")
        c6.metric("Marge",f"{f['margin']*100:.1f}%" if f.get("margin") else "N/A")

    st.divider();S("Comparatif")
    comp=[]
    for tk,inf in pf.items():
        f=fu.get(tk,{});rdt=r5.get(tk)
        comp.append({"Valeur":inf["name"],"Secteur":f.get("sector","N/A"),
            "Rdt 5a %":round(rdt,1) if rdt else None,
            "P/E":round(f["pe"],1) if f.get("pe") else None,
            "Div %":round(f["dy"]*100,1) if f.get("dy") and f["dy"]<1 else None,
            "Beta":round(f["beta"],2) if f.get("beta") else None,
            "ROE %":round(f["roe"]*100,1) if f.get("roe") else None,
            "Reco":str(f.get("reco","")).upper()})
    st.dataframe(pd.DataFrame(comp),hide_index=True)


# =============================================================
# PERFORMANCE (simplifie)
# =============================================================
elif page=="Performance":
    H("Performance",G)
    pf=get_pf()
    if not pf: st.info("Aucune position.");st.stop()
    pmap={"1M":30,"3M":90,"6M":180,"1A":365,"2A":730,"3A":1095,"5A":1825}
    per=st.selectbox("Periode",list(pmap.keys()),index=4)
    sd=(datetime.now()-timedelta(days=pmap[per])).strftime("%Y-%m-%d")
    with st.spinner("Calcul..."): v=pf_val(pf,sd);bench=yf_bench(sd)
    if v.empty: st.warning("Donnees indisponibles.");st.stop()

    inv=pf_inv(pf,v.index);rets=v.pct_change().dropna()
    vol=float(rets.std()*np.sqrt(252)*100) if len(rets)>1 else 0
    cmx=v.cummax();dd=(v-cmx)/cmx*100;mdd=float(dd.min())
    perf=float((v.iloc[-1]/v.iloc[0]-1)*100) if len(v)>1 else 0
    ann=float((1+rets.mean())**252-1) if len(rets)>1 else 0
    sh=round((ann-.03)/(float(rets.std())*np.sqrt(252)),2) if vol>0 and len(rets)>20 else 0

    st.markdown(f'<div class="kr">{K("VALEUR",f"{float(v.iloc[-1]):,.0f} EUR","","kb")}{K("PERF",f"{perf:+.1f}%",per,cc(perf))}{K("RDT ANN.",f"{ann*100:+.1f}%","",cc(ann))}{K("VOL",f"{vol:.1f}%","ann.","ko")}{K("SHARPE",f"{sh}","","kp")}{K("MAX DD",f"{mdd:+.1f}%","","kr2")}</div>',unsafe_allow_html=True)

    # Valorisation + Investi
    S("Valorisation")
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=v.index,y=v.values,name="Portefeuille",line=dict(color="#6366f1",width=2.5),fill="tozeroy",fillcolor="rgba(99,102,241,0.06)"))
    fig.add_trace(go.Scatter(x=inv.index,y=inv.values,name="Investi",line=dict(color="#94a3b8",width=1.5,dash="dash")))
    fig.update_layout(**PL,height=400);st.plotly_chart(fig,use_container_width=True)

    # Benchmark
    S("vs CAC 40 / SBF 120")
    if len(v)>1:
        fig=go.Figure();pn=(v/v.iloc[0])*100
        fig.add_trace(go.Scatter(x=v.index,y=pn.values,name="Portefeuille",line=dict(color="#6366f1",width=2.5)))
        bc={"CAC 40":"#f59e0b","SBF 120":"#ef4444"}
        for bn,bd in bench.items():
            if not bd.empty:
                ci=v.index.intersection(bd.index)
                if len(ci)>1:
                    bn2=(bd.loc[ci]/bd.loc[ci].iloc[0])*100
                    fig.add_trace(go.Scatter(x=ci,y=bn2.values,name=bn,line=dict(color=bc.get(bn,"#888"),width=2,dash="dash")))
        fig.add_hline(y=100,line_dash="dot",line_color="#cbd5e1")
        fig.update_layout(**PL,height=400,yaxis_title="Base 100");st.plotly_chart(fig,use_container_width=True)
        for bn,bd in bench.items():
            if not bd.empty:
                ci=v.index.intersection(bd.index)
                if len(ci)>1:
                    pr2=float((v.loc[ci].iloc[-1]/v.loc[ci].iloc[0]-1)*100)
                    br2=float((bd.loc[ci].iloc[-1]/bd.loc[ci].iloc[0]-1)*100);al=pr2-br2
                    (st.success if al>0 else st.error)(f"vs {bn} : Ptf {pr2:+.1f}% | {bn} {br2:+.1f}% | Alpha **{al:+.1f}%**")

    c1,c2=st.columns(2)
    with c1:
        S("Drawdown")
        fig=go.Figure(go.Scatter(x=dd.index,y=dd.values,line=dict(color="#ef4444",width=1.5),fill="tozeroy",fillcolor="rgba(239,68,68,0.06)"))
        fig.update_layout(**PL,height=280,yaxis_title="%");st.plotly_chart(fig,use_container_width=True)
    with c2:
        S("Distribution des rendements")
        fig=go.Figure(go.Histogram(x=rets.values*100,nbinsx=50,marker_color="#6366f1",opacity=.75))
        fig.add_vline(x=0,line_dash="dash",line_color="#ef4444")
        fig.update_layout(**PL,height=280,xaxis_title="%");st.plotly_chart(fig,use_container_width=True)


# =============================================================
# VOLATILITE / CORRELATION
# =============================================================
elif page=="Volatilite / Correlation":
    H("Volatilite et Correlation",f"Analyse quantitative — {G}")
    pf=get_pf()
    if not pf: st.info("Aucune position.");st.stop()
    tks=list(pf.keys());nm={tk:inf["name"] for tk,inf in pf.items()}
    pm2={"6M":180,"1A":365,"2A":730,"3A":1095,"5A":1825}
    p2=st.selectbox("Historique",list(pm2.keys()),index=2)
    sd2=(datetime.now()-timedelta(days=pm2[p2])).strftime("%Y-%m-%d")
    with st.spinner("Calcul..."): rm=yf_returns(tks,sd2)
    if rm.empty or len(rm.columns)<2: st.warning("Donnees insuffisantes.");st.stop()
    rd=rm.rename(columns=nm)

    S("Volatilite annualisee")
    vols=rm.std()*np.sqrt(252)*100
    vdf=pd.DataFrame({"Valeur":[nm.get(t,t) for t in vols.index],"Vol (%)":[round(v,1) for v in vols.values]}).sort_values("Vol (%)")
    c1,c2=st.columns([2,1])
    with c1:
        fig=go.Figure(go.Bar(x=vdf["Vol (%)"],y=vdf["Valeur"],orientation="h",
            marker_color=[CO[i%len(CO)] for i in range(len(vdf))],
            text=[f"{v:.1f}%" for v in vdf["Vol (%)"]],textposition="outside"))
        fig.update_layout(**PL,height=max(300,len(vdf)*45),yaxis=dict(automargin=True))
        st.plotly_chart(fig,use_container_width=True)
    with c2: st.dataframe(vdf,hide_index=True);st.metric("Moyenne",f"{vols.mean():.1f}%")

    S("Rendement vs Volatilite")
    ar=((1+rm.mean())**252-1)*100
    adf=pd.DataFrame({"Valeur":[nm.get(t,t) for t in ar.index],"Rdt (%)":[round(v,1) for v in ar.values],"Vol (%)":[round(v,1) for v in vols.values]})
    fig=px.scatter(adf,x="Vol (%)",y="Rdt (%)",text="Valeur",color_discrete_sequence=CO)
    fig.update_traces(textposition="top center",marker=dict(size=12))
    fig.add_hline(y=0,line_dash="dash",line_color="#94a3b8")
    fig.update_layout(**PL,height=420);st.plotly_chart(fig,use_container_width=True)

    S("Matrice de correlation")
    corr=rd.corr()
    fig=go.Figure(go.Heatmap(z=corr.values,x=corr.columns,y=corr.index,
        colorscale=[[0,"#ef4444"],[.5,"#ffffff"],[1,"#3b82f6"]],zmin=-1,zmax=1,
        text=np.round(corr.values,2),texttemplate="%{text}",textfont=dict(size=10)))
    fig.update_layout(**PL,height=max(400,len(corr)*40+80),yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig,use_container_width=True)

    mask=np.triu(np.ones_like(corr,dtype=bool),k=1);up=corr.where(mask)
    pairs=[]
    for i in range(len(up.columns)):
        for j in range(i+1,len(up.columns)):
            if not np.isnan(up.iloc[i,j]): pairs.append({"Paire":f"{up.columns[i]} / {up.columns[j]}","Corr":round(up.iloc[i,j],3)})
    if pairs:
        pdf=pd.DataFrame(pairs).sort_values("Corr",ascending=False)
        c1,c2=st.columns(2)
        with c1: S("Plus correlees");st.dataframe(pdf.head(8),hide_index=True)
        with c2: S("Moins correlees");st.dataframe(pdf.tail(8).sort_values("Corr"),hide_index=True)
        avg=pdf["Corr"].mean()
        (st.error if avg>.6 else st.warning if avg>.4 else st.success)(f"Correlation moyenne : {avg:.2f}")


# =============================================================
# FAMA-FRENCH
# =============================================================
elif page=="Fama-French":
    H("Fama-French 3 facteurs",f"Facteurs europeens — {G}")
    st.markdown("""**Mkt-RF** : prime de marche | **SMB** : effet taille (small vs large) | **HML** : effet value (value vs growth) | **Alpha** : surperformance residuelle""")

    pf=get_pf()
    if not pf: st.info("Aucune position.");st.stop()
    tks=list(pf.keys());nm={tk:inf["name"] for tk,inf in pf.items()}
    pm={"1A":365,"2A":730,"3A":1095,"5A":1825}
    pff=st.selectbox("Periode",list(pm.keys()),index=3)
    sdf=(datetime.now()-timedelta(days=pm[pff])).strftime("%Y-%m-%d")

    with st.spinner("Telechargement facteurs Fama-French..."): ff=dl_ff()
    if ff.empty: st.error("Erreur telechargement. Reessayez.");st.stop()
    ff=ff[ff.index>=sdf]
    st.caption(f"{len(ff)} jours | {ff.index.min().strftime('%d/%m/%Y')} — {ff.index.max().strftime('%d/%m/%Y')}")

    with st.spinner("Regressions..."): rm=yf_returns(tks,sdf)
    if rm.empty: st.warning("Donnees insuffisantes.");st.stop()

    # Portefeuille
    S("Regression portefeuille")
    pr=yf_prices(tuple(tks))
    tv=sum(pr.get(tk,0)*pf[tk]["qty"] for tk in tks)
    vt=[t for t in tks if t in rm.columns]
    w=np.array([pr.get(t,0)*pf[t]["qty"]/tv if tv>0 else 0 for t in vt])
    if w.sum()>0: w/=w.sum()
    pfr=(rm[vt]*w).sum(axis=1)

    res=ff_reg(pfr,ff)
    if res:
        sig="Significatif" if abs(res["t_a"])>1.96 else "Non significatif"
        sc="kg" if abs(res["t_a"])>1.96 and res["alpha"]>0 else "ko" if abs(res["t_a"])<=1.96 else "kr2"
        st.markdown(f'<div class="kr">{K("ALPHA",f"{res[\"alpha\"]:+.2f}%/an",f"t={res[\"t_a\"]:.2f} ({sig})",sc)}{K("BETA MKT",f"{res[\"mkt\"]:.2f}",f"t={res[\"t_m\"]:.1f}","kb")}{K("SMB (Taille)",f"{res[\"smb\"]:+.2f}",f"t={res[\"t_s\"]:.1f}","kp")}{K("HML (Value)",f"{res[\"hml\"]:+.2f}",f"t={res[\"t_h\"]:.1f}","kt")}{K("R CARRE",f"{res[\"r2\"]*100:.1f}%",f"{res[\"n\"]} obs","ks")}</div>',unsafe_allow_html=True)

        # Interpretation
        st.markdown("#### Lecture des resultats")
        if abs(res["t_a"])>1.96:
            st.info(f"**Alpha {'positif' if res['alpha']>0 else 'negatif'}** ({res['alpha']:+.2f}%/an) : {'surperformance' if res['alpha']>0 else 'sous-performance'} apres ajustement des facteurs de risque.")
        else:
            st.info(f"**Alpha non significatif** ({res['alpha']:+.2f}%/an) : la performance est expliquee par l'exposition aux facteurs.")
        if res["mkt"]>1.1: st.warning(f"Beta marche {res['mkt']:.2f} : profil offensif.")
        elif res["mkt"]<0.9: st.success(f"Beta marche {res['mkt']:.2f} : profil defensif.")
        if abs(res["smb"])>0.2: st.info(f"SMB {res['smb']:+.2f} : biais {'small caps' if res['smb']>0 else 'large caps'}.")
        if abs(res["hml"])>0.2: st.info(f"HML {res['hml']:+.2f} : biais {'value' if res['hml']>0 else 'growth'}.")

        S("Exposition aux facteurs")
        fig=go.Figure(go.Bar(x=["Marche","Taille (SMB)","Value (HML)"],y=[res["mkt"],res["smb"],res["hml"]],
            marker_color=["#3b82f6","#8b5cf6","#14b8a6"],
            text=[f"{res['mkt']:.2f}",f"{res['smb']:+.2f}",f"{res['hml']:+.2f}"],textposition="outside",textfont=dict(size=14)))
        fig.add_hline(y=0,line_dash="dash",line_color="#94a3b8")
        fig.add_hline(y=1,line_dash="dot",line_color="#cbd5e1",annotation_text="Beta=1")
        fig.update_layout(**PL,height=320);st.plotly_chart(fig,use_container_width=True)

    # Regressions individuelles
    S("Par titre")
    sr=[]
    for tk in vt:
        r=ff_reg(rm[tk],ff)
        if r: sr.append({"Valeur":nm.get(tk,tk),"Alpha %/an":round(r["alpha"],2),"t-stat":round(r["t_a"],2),
            "Beta Mkt":round(r["mkt"],2),"SMB":round(r["smb"],2),"HML":round(r["hml"],2),"R2 %":round(r["r2"]*100,1)})
    if sr:
        sdf2=pd.DataFrame(sr).sort_values("Alpha %/an",ascending=False)
        st.dataframe(sdf2,hide_index=True)

        c1,c2=st.columns(2)
        with c1:
            S("Alpha par titre")
            s3=sdf2.sort_values("Alpha %/an")
            fig=go.Figure(go.Bar(x=s3["Alpha %/an"],y=s3["Valeur"],orientation="h",
                marker_color=["#ef4444" if x<0 else "#10b981" for x in s3["Alpha %/an"]],
                text=[f"{x:+.2f}%" for x in s3["Alpha %/an"]],textposition="outside"))
            fig.add_vline(x=0,line_dash="dash",line_color="#94a3b8")
            fig.update_layout(**PL,height=max(300,len(s3)*45),yaxis=dict(automargin=True))
            st.plotly_chart(fig,use_container_width=True)
        with c2:
            S("Style : SMB vs HML")
            fig=px.scatter(sdf2,x="SMB",y="HML",text="Valeur",color_discrete_sequence=CO)
            fig.update_traces(textposition="top center",marker=dict(size=12))
            fig.add_hline(y=0,line_dash="dash",line_color="#94a3b8")
            fig.add_vline(x=0,line_dash="dash",line_color="#94a3b8")
            fig.update_layout(**PL,height=380,xaxis_title="SMB (+ = Small)",yaxis_title="HML (+ = Value)")
            st.plotly_chart(fig,use_container_width=True)

    # Rolling alpha
    S("Alpha glissant 6 mois")
    if res and len(pfr)>130:
        ci=pfr.index.intersection(ff.index);pfr2=pfr.loc[ci];ffc=ff.loc[ci]
        ra=[]
        for i in range(126,len(ci)):
            y_w=(pfr2.iloc[i-126:i]-ffc["RF"].iloc[i-126:i]).values
            X_w=np.column_stack([np.ones(126),ffc["Mkt-RF"].iloc[i-126:i].values,ffc["SMB"].iloc[i-126:i].values,ffc["HML"].iloc[i-126:i].values])
            try: b,_,_,_=np.linalg.lstsq(X_w,y_w,rcond=None);ra.append({"d":ci[i],"a":b[0]*252*100})
            except: pass
        if ra:
            rad=pd.DataFrame(ra)
            fig=go.Figure(go.Scatter(x=rad["d"],y=rad["a"],line=dict(color="#6366f1",width=2),fill="tozeroy",fillcolor="rgba(99,102,241,0.06)"))
            fig.add_hline(y=0,line_dash="dash",line_color="#ef4444")
            fig.update_layout(**PL,height=320,yaxis_title="Alpha ann. (%)");st.plotly_chart(fig,use_container_width=True)


# =============================================================
# ALERTES
# =============================================================
elif page=="Alertes":
    H("Alertes","Seuils et signaux")
    alerts=load_al()
    all_tk=sorted(set(tk for p in PF.values() for tk in p.keys()))
    if not all_tk: st.info("Importez des positions.");st.stop()
    S("Nouvelle alerte")
    c1,c2,c3,c4=st.columns([3,3,2,2])
    with c1: a_tk=st.selectbox("Ticker",all_tk)
    with c2: a_tp=st.selectbox("Type",["Prix au-dessus","Prix en-dessous","PnL % au-dessus","PnL % en-dessous"])
    with c3: a_vl=st.number_input("Seuil",value=0.0,step=1.0)
    with c4:
        st.write("");st.write("")
        if st.button("Ajouter",type="primary",use_container_width=True):
            alerts.append({"ticker":a_tk,"type":a_tp,"value":a_vl,"created":datetime.now().strftime("%d/%m/%Y %H:%M")})
            save_al(alerts);st.rerun()
    if alerts:
        S("Actives")
        cp=yf_prices(tuple(set(a["ticker"] for a in alerts)))
        for i,a in enumerate(alerts):
            cur=cp.get(a["ticker"],0);tr=False
            if "au-dessus" in a["type"] and "Prix" in a["type"] and cur>a["value"]: tr=True
            elif "en-dessous" in a["type"] and "Prix" in a["type"] and cur<a["value"]: tr=True
            c1,c2=st.columns([9,1])
            with c1: st.markdown(f"**{a['ticker']}** — {a['type']} **{a['value']}** (cours: {cur:.2f}) `{'DECLENCHEE' if tr else 'Attente'}`")
            with c2:
                if st.button("X",key=f"d{i}"): alerts.pop(i);save_al(alerts);st.rerun()
    S("Signaux auto")
    pf=get_pf()
    if pf:
        pr=yf_prices(tuple(pf.keys()));has=False
        for tk,inf in pf.items():
            cur=pr.get(tk,0)
            if cur==0: continue
            pnl=((cur-inf["buy_price"])/inf["buy_price"])*100
            if pnl>30: st.success(f"{inf['name']}: **{pnl:+.1f}%** — Benefice ?");has=True
            elif pnl<-15: st.error(f"{inf['name']}: **{pnl:+.1f}%** — Surveiller");has=True
        if not has: st.info("Aucun signal.")


# =============================================================
# RECOMMANDATIONS
# =============================================================
elif page=="Recommandations":
    H("Recommandations",G)
    pf=get_pf()
    if not pf: st.info("Aucune position.");st.stop()
    tks=list(pf.keys())
    with st.spinner("Analyse..."): pr=yf_prices(tuple(tks));fu=yf_info(tuple(tks))
    tv=sum(pr.get(tk,0)*inf["qty"] for tk,inf in pf.items())
    pos=[]
    for tk,inf in pf.items():
        cur=pr.get(tk,0);f=fu.get(tk,{});t=f.get("target")
        pos.append({"name":inf["name"],"w":(cur*inf["qty"]/tv*100) if tv else 0,
            "sector":f.get("sector","N/A"),"pe":f.get("pe"),"reco":f.get("reco","N/A"),
            "rdt":((t-cur)/cur*100) if t and cur else None,
            "pnl":((cur-inf["buy_price"])/inf["buy_price"])*100 if inf["buy_price"] else 0})
    dfp=pd.DataFrame(pos).sort_values("w",ascending=False)

    S("Consensus analystes")
    for _,r in dfp.iterrows():
        rc=str(r["reco"]).upper();msg=f"**{r['name']}** : {rc}"
        if r["rdt"]: msg+=f" | Objectif: {r['rdt']:+.1f}%"
        (st.success if rc in ["BUY","STRONG_BUY"] else st.error if rc in ["SELL","STRONG_SELL"] else st.info)(msg)

    c1,c2=st.columns(2)
    mw=dfp["w"].max()
    with c1:
        S("Concentration")
        (st.error if mw>40 else st.warning if mw>25 else st.success)(f"Max: {dfp.iloc[0]['name']} = {mw:.1f}%")
        fig=go.Figure(go.Bar(x=dfp["w"],y=dfp["name"],orientation="h",marker_color="#6366f1",
            text=[f"{w:.1f}%" for w in dfp["w"]],textposition="outside"))
        fig.update_layout(**PL,height=max(280,len(dfp)*45),yaxis=dict(automargin=True))
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        S("Secteurs")
        ds=dfp.groupby("sector")["w"].sum().sort_values(ascending=False);ns=len(ds)
        (st.error if ns<=2 else st.warning if ns<=4 else st.success)(f"{ns} secteurs")
        fig=px.bar(x=ds.index,y=ds.values,color=ds.values,color_continuous_scale="Viridis")
        fig.update_layout(**PL,height=320);st.plotly_chart(fig,use_container_width=True)

    S("Actions a considerer")
    recs=[]
    for _,r in dfp.iterrows():
        if r["pnl"]>50: recs.append(("warning",f"Prise de benefice sur **{r['name']}** ({r['pnl']:+.1f}%)"))
        if r["pnl"]<-20: recs.append(("error",f"Reevaluer **{r['name']}** ({r['pnl']:+.1f}%)"))
        if r["pe"] and r["pe"]>40: recs.append(("info",f"PE eleve sur **{r['name']}** ({r['pe']:.0f}x)"))
    if recs:
        for typ,msg in recs: getattr(st,typ)(msg)
    else: st.success("Portefeuille equilibre.")


# =============================================================
# GESTION
# =============================================================
elif page=="Gestion":
    H("Gestion","Import, export, modification")
    t1,t2,t3=st.tabs(["Ajouter","Importer Excel/CSV","Exporter"])

    with t1:
        c1,c2,c3=st.columns(3)
        with c1: am=st.selectbox("Membre",FAMILY,key="am")
        with c2: atk=st.text_input("Ticker Yahoo",key="atk").upper()
        with c3: an=st.text_input("Nom",key="an")
        c4,c5,c6=st.columns(3)
        with c4: aq=st.number_input("Qte",min_value=1,value=10,key="aq")
        with c5: ap=st.number_input("Prix",min_value=0.01,value=100.0,step=0.01,key="ap")
        with c6: ad=st.date_input("Date",key="ad")
        if st.button("Ajouter",type="primary"):
            if am and atk and an:
                PF.setdefault(am,{})[atk]={"qty":int(aq),"buy_price":float(ap),"buy_date":ad.strftime("%Y-%m-%d"),"name":an}
                st.session_state.pf=PF;save_pf(PF);st.success(f"OK : {an}");st.rerun()

    with t2:
        st.caption("Format courtier : Valeur | Code | Place | Date | Qte | PRU | Cours | Valorisation")
        im=st.selectbox("Membre",FAMILY,key="im")
        up=st.file_uploader("Fichier",type=["csv","xlsx","xls"],key="up")
        if up:
            try:
                idf=pd.read_csv(up) if up.name.endswith(".csv") else pd.read_excel(up)
                idf=idf.dropna(how="all")
                idf=idf[idf.iloc[:,0].notna()&(idf.iloc[:,0].astype(str).str.strip()!="")&~idf.iloc[:,0].astype(str).str.upper().str.contains("LIQUIDIT",na=False)]
                idf=idf[pd.to_numeric(idf.iloc[:,4],errors="coerce")>0]
                st.dataframe(idf,hide_index=True)
                st.session_state["idata"]=idf.to_dict();st.session_state["imem"]=im
            except Exception as e: st.error(f"Erreur: {e}")
        if "idata" in st.session_state:
            mode=st.radio("Mode",["Ajouter","Remplacer"])
            if st.button("CONFIRMER",type="primary"):
                idf=pd.DataFrame(st.session_state["idata"]);imm=st.session_state.get("imem",FAMILY[0])
                PF.setdefault(imm,{})
                if "Remplacer" in mode: PF[imm]={}
                ct=0
                for _,row in idf.iterrows():
                    try:
                        nm2=str(row.iloc[0]).strip();qt=int(float(row.iloc[4]));pru=float(row.iloc[5])
                        dv=row.iloc[3];dt=dv.strftime("%Y-%m-%d") if isinstance(dv,pd.Timestamp) else str(dv)[:10]
                        if qt>0 and pru>0: PF[imm][find_tk(nm2)]={"qty":qt,"buy_price":pru,"buy_date":dt,"name":nm2};ct+=1
                    except: pass
                st.session_state.pf=PF;save_pf(PF)
                if "idata" in st.session_state: del st.session_state["idata"]
                st.success(f"{ct} positions");st.rerun()

    with t3:
        if st.button("Generer CSV"):
            rows=[{"Membre":m,"Ticker":tk,"Nom":inf["name"],"Qte":inf["qty"],"Prix":inf["buy_price"],"Date":inf["buy_date"]} for m in FAMILY for tk,inf in PF.get(m,{}).items()]
            edf=pd.DataFrame(rows)
            st.download_button("Telecharger",edf.to_csv(index=False),"faure.csv","text/csv")
            st.dataframe(edf,hide_index=True)

    st.divider();S("Supprimer")
    c1,c2,c3=st.columns([2,4,2])
    with c1: dm=st.selectbox("Membre",FAMILY,key="dm")
    if PF.get(dm):
        with c2: dp=st.selectbox("Position",[f"{tk} — {inf['name']}" for tk,inf in PF[dm].items()],key="dp")
        with c3:
            st.write("");st.write("")
            if st.button("Supprimer",use_container_width=True): del PF[dm][dp.split(" — ")[0]];st.session_state.pf=PF;save_pf(PF);st.rerun()
    else: st.info(f"Aucune position pour {dm}.")
