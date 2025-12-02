import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Relocalisation PCAM - Simulator",
    page_icon="🔋",
    layout="wide"
)

# --- STYLES CSS PERSONNALISÉS (Pour imiter votre design React) ---
st.markdown("""
    <style>
    /* Fond global */
    .stApp {
        background-color: #F0F3F8;
    }
    /* Carte métrique */
    div[data-testid="metric-container"] {
        background-color: white;
        border: 1px solid #e0e0e0;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    /* Couleurs personnalisées pour les titres */
    h1, h2, h3 {
        color: #2C2E3E;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONSTANTES & PARAMÈTRES ---
COLORS = {
    "dark": "#2C2E3E",
    "orange": "#FF8C66",
    "green": "#A0E8AF",
    "text": "#2C2E3E",
    "red": "#FF5722"
}

BASE_PRICES = {
    "Lithium": 20, 
    "Nickel": 18,  
    "Cobalt": 35,  
    "Manganese": 2,
    "pCAM_Asia_Import": 18 
}

BLACK_MASS_COMPOSITION = {
    "NMC": {"Ni": 0.25, "Co": 0.05, "Mn": 0.05, "Li": 0.04},
    "LFP": {"Ni": 0.00, "Co": 0.00, "Mn": 0.00, "Li": 0.035}
}

SCENARIOS = {
    "pessimiste": {
        "blackMassVolume": 15000, "shareNMC": 60, "metalPrices": 0.8, 
        "energyCostEU": 180, "logisticsCost": 120, "yieldRecovery": 85, "pcamPremium": 2
    },
    "conservateur": {
        "blackMassVolume": 25000, "shareNMC": 75, "metalPrices": 1.0,
        "energyCostEU": 120, "logisticsCost": 90, "yieldRecovery": 90, "pcamPremium": 3.5
    },
    "optimiste": {
        "blackMassVolume": 45000, "shareNMC": 90, "metalPrices": 1.2,
        "energyCostEU": 80, "logisticsCost": 60, "yieldRecovery": 95, "pcamPremium": 5
    }
}

# --- INITIALISATION DE L'ÉTAT (SESSION STATE) ---
if 'params' not in st.session_state:
    st.session_state.params = SCENARIOS['conservateur'].copy()

# --- FONCTIONS UTILITAIRES ---
def load_scenario(name):
    st.session_state.params = SCENARIOS[name].copy()
    st.toast(f"Scénario '{name}' chargé !", icon="✅")

def calculate_economics(params):
    totalBM = params['blackMassVolume']
    volNMC = totalBM * (params['shareNMC'] / 100)
    volLFP = totalBM * (1 - params['shareNMC'] / 100)
    efficiency = params['yieldRecovery'] / 100

    metals = {
        "Ni": (volNMC * BLACK_MASS_COMPOSITION['NMC']['Ni'] * efficiency),
        "Co": (volNMC * BLACK_MASS_COMPOSITION['NMC']['Co'] * efficiency),
        "Li": ((volNMC * BLACK_MASS_COMPOSITION['NMC']['Li'] + volLFP * BLACK_MASS_COMPOSITION['LFP']['Li']) * efficiency),
        "Mn": (volNMC * BLACK_MASS_COMPOSITION['NMC']['Mn'] * efficiency)
    }

    pNi = BASE_PRICES['Nickel'] * params['metalPrices']
    pCo = BASE_PRICES['Cobalt'] * params['metalPrices']
    pLi = BASE_PRICES['Lithium'] * params['metalPrices']
    pMn = BASE_PRICES['Manganese']

    revenueOpenCycle = (metals['Ni'] * pNi + metals['Co'] * pCo + metals['Li'] * pLi + metals['Mn'] * pMn) * 1000
    costHydro = totalBM * 2500
    marginOpenCycle = revenueOpenCycle - costHydro

    massMetalsPCAM = metals['Ni'] + metals['Co'] + metals['Mn']
    pcamVolume = massMetalsPCAM / 0.6 if massMetalsPCAM > 0 else 0
    
    pricePCAM_EU = BASE_PRICES['pCAM_Asia_Import'] + params['pcamPremium']
    revenuePCAM = pcamVolume * pricePCAM_EU * 1000
    revenueLi_Closed = metals['Li'] * pLi * 1000
    totalRevenueClosed = revenuePCAM + revenueLi_Closed

    costPCAMProcessing = pcamVolume * 1500
    totalCostClosed = costHydro + costPCAMProcessing + (totalBM * (params['logisticsCost'] / 10))
    marginClosedCycle = totalRevenueClosed - totalCostClosed

    return {
        "metals": metals,
        "financials": {
            "open": {"revenue": revenueOpenCycle, "cost": costHydro, "margin": marginOpenCycle},
            "closed": {"revenue": totalRevenueClosed, "cost": totalCostClosed, "margin": marginClosedCycle}
        },
        "volumes": {"pcam": pcamVolume}
    }

# --- BARRE LATÉRALE (SIDEBAR) ---
with st.sidebar:
    st.title("⚙️ Configuration")
    st.markdown("---")
    
    st.subheader("Scénarios Rapides")
    col_scen1, col_scen2, col_scen3 = st.columns(3)
    if col_scen1.button("📉 Pess."): load_scenario('pessimiste')
    if col_scen2.button("💾 Cons."): load_scenario('conservateur')
    if col_scen3.button("📈 Opti."): load_scenario('optimiste')
    
    st.markdown("---")
    st.subheader("Paramètres Manuels")
    
    # Inputs liés directement au session_state
    st.session_state.params['blackMassVolume'] = st.slider("Volume Black Mass (T)", 5000, 100000, int(st.session_state.params['blackMassVolume']), step=1000)
    st.session_state.params['shareNMC'] = st.slider("Part Chimie NMC (%)", 0, 100, int(st.session_state.params['shareNMC']))
    st.session_state.params['yieldRecovery'] = st.slider("Rendement Récupération (%)", 50, 99, int(st.session_state.params['yieldRecovery']))
    
    st.markdown("### Coûts & Marché")
    st.session_state.params['metalPrices'] = st.slider("Index Prix Métaux", 0.5, 2.0, float(st.session_state.params['metalPrices']), step=0.1)
    st.session_state.params['energyCostEU'] = st.slider("Coût Élec. Europe (€/MWh)", 40, 300, int(st.session_state.params['energyCostEU']))
    st.session_state.params['pcamPremium'] = st.slider("Premium Made in EU (€/kg)", 0.0, 10.0, float(st.session_state.params['pcamPremium']), step=0.5)
    st.session_state.params['logisticsCost'] = st.slider("Coût Logistique (€/T)", 20, 200, int(st.session_state.params['logisticsCost']))

    st.markdown("---")
    st.subheader("Import / Export")
    
    uploaded_file = st.file_uploader("Importer CSV", type="csv")
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file, header=None, index_col=0)
            new_params = df[1].to_dict()
            st.session_state.params.update(new_params)
            st.toast("Configuration chargée !", icon="📂")
        except:
            st.error("Format CSV invalide")

    # Bouton Export
    df_export = pd.DataFrame(list(st.session_state.params.items()), columns=['Key', 'Value'])
    csv = df_export.to_csv(index=False, header=False)
    st.download_button("Exporter Config", csv, "scenario_pcam.csv", "text/csv")


# --- CALCULS ---
res = calculate_economics(st.session_state.params)
is_closed_better = res['financials']['closed']['margin'] > res['financials']['open']['margin']

# --- INTERFACE PRINCIPALE ---
st.title("RELOCALISATION PCAM 🇪🇺")
st.markdown("**Simulateur d'impact économique : Recyclage Cycle Ouvert vs Fermé**")

# ONGLETS (DASHBOARD vs DÉTAILS)
tab1, tab2 = st.tabs(["📊 Dashboard", "🔍 Détails Opérationnels"])

with tab1:
    # LIGNE 1 : KPIs
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Volume Black Mass", f"{st.session_state.params['blackMassVolume']/1000:.1f}k T", "Input")
    col2.metric("Production pCAM", f"{res['volumes']['pcam']/1000:.1f}k T", "Estimé")
    col3.metric("Marge Cycle Ouvert", f"{res['financials']['open']['margin']/1e6:.1f} M€", "Export sels")
    
    delta_color = "normal" if is_closed_better else "inverse"
    col4.metric("Marge Cycle Fermé", f"{res['financials']['closed']['margin']/1e6:.1f} M€", 
                delta=f"{(res['financials']['closed']['margin'] - res['financials']['open']['margin'])/1e6:.1f} M€ vs Open",
                delta_color=delta_color)

    # LIGNE 2 : Graphiques et Recommandation
    c_left, c_right = st.columns([1, 2])
    
    with c_left:
        st.markdown("### État Stratégique")
        container_bg = COLORS['green'] if is_closed_better else "#FFCCBC"
        text_color = "#155724" if is_closed_better else "#721c24"
        
        st.markdown(f"""
        <div style="background-color: {container_bg}; padding: 20px; border-radius: 10px; color: {text_color};">
            <h3 style="margin:0; color: {text_color};">{ "✅ CYCLE FERMÉ" if is_closed_better else "⚠️ CYCLE OUVERT" }</h3>
            <p style="font-weight: bold; margin-top: 10px;">
                { "La production locale est rentable." if is_closed_better else "L'exportation reste plus sûre économiquement." }
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.info("💡 **Note :** Le cycle fermé sécurise l'approvisionnement des Gigafactories européennes et réduit l'empreinte carbone.")

    with c_right:
        st.markdown("### Comparaison Financière (M€)")
        
        # Préparation données pour Plotly
        categories = ['Cycle Ouvert', 'Cycle Fermé']
        revenus = [res['financials']['open']['revenue']/1e6, res['financials']['closed']['revenue']/1e6]
        couts = [res['financials']['open']['cost']/1e6, res['financials']['closed']['cost']/1e6]
        marges = [res['financials']['open']['margin']/1e6, res['financials']['closed']['margin']/1e6]

        fig = go.Figure()
        fig.add_trace(go.Bar(name='Revenu', x=categories, y=revenus, marker_color=COLORS['dark']))
        fig.add_trace(go.Bar(name='Coût', x=categories, y=couts, marker_color=COLORS['orange']))
        fig.add_trace(go.Bar(name='Marge', x=categories, y=marges, marker_color=COLORS['green']))

        fig.update_layout(
            barmode='group',
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Métaux Récupérés (Tonnes/an)")
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Nickel (Ni)", f"{res['metals']['Ni']:.0f} t")
    col_m2.metric("Cobalt (Co)", f"{res['metals']['Co']:.0f} t")
    col_m3.metric("Lithium (Li)", f"{res['metals']['Li']:.0f} t")
    col_m4.metric("Manganèse (Mn)", f"{res['metals']['Mn']:.0f} t")
    
    st.markdown("---")
    st.subheader("Détail des calculs financiers")
    st.json(res['financials'])
