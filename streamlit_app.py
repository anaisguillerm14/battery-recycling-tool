import streamlit as st
import numpy as np

# --- Configuration de la Page ---
st.set_page_config(
    layout="wide", 
    page_title="Simulateur pCAM Européen"
)

# --- Constantes du Modèle ---
# Hypothèses de base (à affiner avec les données réelles)
CONVERSION_BM_PCAM = 0.45  # 45% de la Black Mass devient pCAM
PRIX_PCAM_TONNE = 25000  # Prix de vente estimé du pCAM (€/tonne)

# --- Titre et Introduction ---
st.title("🔋 Simulateur : Relocalisation pCAM via Recyclage Européen")
st.markdown("### Évaluation Stratégique du Cycle Fermé : Europe vs Asie (Horizon 2030-2035)")

st.header("1. Paramètres de Simulation (Inputs)")
st.markdown("---")


# --- 2. Barre Latérale (Inputs) ---
st.sidebar.header("🎯 Variables de Scénario")

# Variables de Volume (Offre)
st.sidebar.subheader("Offre de Matière (Black Mass)")
eol_volume = st.sidebar.slider(
    "Black Mass disponible en Europe (k tonnes/an, 2030)", 
    min_value=50, 
    max_value=500, 
    value=150, 
    step=25
)

# Variables Techniques (Rendements & Qualité)
st.sidebar.subheader("Efficacité Technique et Coûts")
taux_recup_ni = st.sidebar.slider(
    "Taux de Récupération Ni visé (%)", 
    min_value=80, 
    max_value=95, 
    value=90, 
    step=1
)

# Variables Économiques (OPEX)
cost_energy_eu = st.sidebar.number_input(
    "Coût Énergétique Europe (€/kWh)", 
    min_value=0.10, 
    max_value=0.30, 
    value=0.18, 
    step=0.01
)
cost_bm_achat = st.sidebar.number_input(
    "Coût d'achat de la Black Mass (€/tonne)", 
    min_value=1500, 
    max_value=3000, 
    value=2200, 
    step=100
)


# --- 3. Section de Calcul (Backend) ---

def run_pcam_model(volume_bm, efficiency_ni, cost_energy, cost_bm):
    # a. Calcul du potentiel pCAM
    pcam_output = volume_bm * CONVERSION_BM_PCAM
    
    # b. Coût de la Black Mass traitée
    # Simplification: coût d'achat BM + coût de traitement (énergie, etc.)
    cost_bm_processed = (cost_bm + (cost_energy * 5000)) * volume_bm # 5000 kWh/tonne BM (Hypothèse)
    
    # c. Coût Unitaire pCAM Europe (Cycle Fermé)
    cost_pcam_unit_eu = cost_bm_processed / (pcam_output * 1000)
    
    # d. Coût Unitaire Asie (Cycle Ouvert - Réf.)
    # Hypothèse simple pour l'exemple
    cost_pcam_unit_asia = 20000 
    
    # e. Marge et Rentabilité
    revenue = pcam_output * PRIX_PCAM_TONNE
    
    return pcam_output, cost_pcam_unit_eu, cost_pcam_unit_asia, revenue

pcam_pot, cost_eu, cost_asia, revenue_eu = run_pcam_model(
    eol_volume, taux_recup_ni, cost_energy_eu, cost_bm_achat
)


# --- 4. Affichage des Résultats (Outputs) ---

st.header("2. Résultats de l'Analyse Technico-Économique")
st.markdown("---")

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.metric(
        label="Potentiel de Production pCAM", 
        value=f"{pcam_pot:,.0f} kt/an", 
        help="Volume de pCAM produit annuellement par le scénario Européen."
    )

with col_b:
    st.metric(
        label="Coût Unitaire pCAM (Cycle Fermé Europe)", 
        value=f"{cost_eu:,.0f} €/tonne", 
    )

with col_c:
    cost_diff = cost_asia - cost_eu
    st.metric(
        label="Avantage Compétitif vs Asie (Cycle Ouvert)", 
        value=f"{cost_diff:,.0f} €/tonne",
        delta="Si positif, le coût Européen est plus bas."
    )

st.subheader("Analyse de Sensibilité : Impact de l'Énergie sur la Compétitivité")
st.bar_chart({"Europe (Simulé)": cost_eu, "Asie (Référence)": cost_asia})
