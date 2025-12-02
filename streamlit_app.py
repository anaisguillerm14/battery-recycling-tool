import streamlit as st
import numpy as np
import pandas as pd

# --- CONSTANTES ET HYPOTHÈSES DE BASE ---
# Ces valeurs sont des placeholders et doivent être affinées par la recherche de votre équipe.

# Constantes Techniques
CONVERSION_BM_PCAM = 0.45   # Fraction de la Black Mass transformable en pCAM utile
ANCIEN_TAUX_RECUP_NI = 0.90 # Taux de récupération de Nickel de référence (cible 2027)

# Constantes Économiques (en €/tonne)
PRIX_PCAM_TONNE_VENTE = 25000.0   # Prix de vente de référence pour le pCAM
COUT_PCAM_REF_ASIE = 21000.0      # Coût unitaire du pCAM importé (cycle ouvert / référence Asie)
CAPEX_USINE_TONNE_AN = 1500.0     # CAPEX annualisé pour l'usine d'hydrométallurgie/pCAM par tonne de BM traitée
KWH_PAR_TONNE_BM = 5500.0         # Consommation électrique estimée par tonne de Black Mass traitée

# Constantes Réglementaires (pour le Recycled Content)
COUT_NON_CONFORMITE = 5000.0      # Pénalité hypothétique si les cibles ne sont pas atteintes (€/tonne)
CIBLE_REC_CONTENT_NI_2031 = 0.06  # 6% de contenu recyclé en Nickel d'ici 2031 
CIBLE_REC_CONTENT_LI_2031 = 0.06  # 6% de contenu recyclé en Lithium d'ici 2031 


# --- FONCTION DE MODÉLISATION DU COÛT ---
def run_pcam_model(volume_bm, eff_ni, eff_li, cost_energy, cost_bm, cap_usine):
    
    # 1. CALCULS TECHNIQUES DE PRODUCTION
    pcam_output_tonnes = volume_bm * CONVERSION_BM_PCAM * 1000 # Conversion en tonnes
    
    # 2. CALCULS ÉCONOMIQUES (CYCLE FERMÉ - EUROPE)
    
    # Coûts de traitement (OPEX)
    cost_energy_total = volume_bm * 1000 * KWH_PAR_TONNE_BM * cost_energy # Coût total de l'énergie
    
    # Coût d'achat de la matière première (Black Mass)
    cost_bm_total = volume_bm * 1000 * cost_bm
    
    # Coût d'investissement annualisé (CAPEX)
    cost_capex_total = volume_bm * 1000 * cap_usine
    
    # Coût total (OPEX + CAPEX)
    cost_total_eu = cost_energy_total + cost_bm_total + cost_capex_total
    
    # Coût unitaire par tonne de pCAM produite
    if pcam_output_tonnes > 0:
        cost_pcam_unit_eu = cost_total_eu / pcam_output_tonnes
    else:
        cost_pcam_unit_eu = 0.0
        
    # 3. ANALYSE REGLEMENTAIRE
    
    # Impact de l'efficacité de récupération sur la quantité de métaux disponibles
    ni_recovered_tonnes = volume_bm * 1000 * 0.05 * eff_ni # Hypothèse: 5% de Ni dans la BM
    li_recovered_tonnes = volume_bm * 1000 * 0.01 * eff_li # Hypothèse: 1% de Li dans la BM
    
    # Pénalité de non-conformité au contenu recyclé (si la production est faible)
    production_batterie_cible = pcam_output_tonnes * 10 # Estimation pour le marché
    
    # Simplification : vérification rapide du taux de Ni recyclé
    taux_recyclage_ni = ni_recovered_tonnes / production_batterie_cible if production_batterie_cible > 0 else 0
    
    penalite_reglementaire = 0.0
    if taux_recyclage_ni < CIBLE_REC_CONTENT_NI_2031:
        penalite_reglementaire = COUT_NON_CONFORMITE * production_batterie_cible
        
    # 4. RENTABILITÉ FINALE
    revenue_total = pcam_output_tonnes * PRIX_PCAM_TONNE_VENTE
    marge_brute = revenue_total - cost_total_eu - penalite_reglementaire
    
    return pcam_output_tonnes, cost_pcam_unit_eu, cost_total_eu, revenue_total, marge_brute, taux_recyclage_ni

# --- CONFIGURATION DE L'APPLICATION STREAMLIT ---

st.set_page_config(layout="wide", page_title="SIMULATEUR PCAM EUROPEEN")

st.title("SIMULATEUR : RELOCALISATION PCAM VIA RECYCLAGE EUROPEEN")
st.markdown("### ÉVALUATION STRATÉGIQUE DU CYCLE FERMÉ : EUROPE VS ASIE (HORIZON 2030-2035)")
st.markdown("---")


# --- BARRE LATERALE (INPUTS) ---
st.sidebar.header("PARAMÈTRES DE SCÉNARIO")

# SECTION 1: VOLUME ET OFFRE (Technico-économique)
st.sidebar.subheader("1. OFFRE DE MATIÈRE ET VOLUMES")
eol_volume = st.sidebar.slider(
    "BLACK MASS DISPONIBLE EN EUROPE (K TONNES/AN)", 
    min_value=50, 
    max_value=500, 
    value=150, 
    step=25
)

# SECTION 2: EFFICACITÉ TECHNIQUE (Réglementaire)
st.sidebar.subheader("2. EFFICACITÉ DE RÉCUPÉRATION (RÈGLEMENT UE)")

st.sidebar.markdown("**Cibles 2031 (Taux de Récupération - En %)**")
col_ni, col_li = st.sidebar.columns(2)

with col_ni:
    eff_ni = st.slider(
        "NICKEL (Ni)", 
        min_value=80, 
        max_value=98, 
        value=95, # Cible 2031: 95% pour Co & Ni [cite: 172]
        step=1
    ) / 100.0

with col_li:
    eff_li = st.slider(
        "LITHIUM (Li)", 
        min_value=40, 
        max_value=85, 
        value=80, # Cible 2031: 80% [cite: 172]
        step=1
    ) / 100.0


# SECTION 3: COÛTS OPÉRATIONNELS ET FINANCIERS (Économique)
st.sidebar.subheader("3. COÛTS UNITAIRES ET OPEX")

cost_energy_eu = st.sidebar.number_input(
    "COÛT ÉNERGÉTIQUE EUROPE (€/KWH)", 
    min_value=0.10, 
    max_value=0.30, 
    value=0.18, 
    step=0.01, 
    format="%.2f",
    help="Facteur OPEX majeur pour l'hydrométallurgie."
)

cost_bm_achat = st.sidebar.number_input(
    "COÛT D'ACHAT DE LA BLACK MASS (€/TONNE)", 
    min_value=1500, 
    max_value=3000, 
    value=2200, 
    step=100
)

cap_usine = st.sidebar.number_input(
    "CAPEX ANNUALISÉ USINE (€/TONNE BM TRAITÉE)", 
    min_value=1000, 
    max_value=3000, 
    value=CAPEX_USINE_TONNE_AN, 
    step=100,
    help="Coût d'investissement de l'usine ramené à la tonne traitée annuellement."
)

# --- EXÉCUTION DU MODÈLE ---
pcam_pot, cost_eu, cost_total_eu, revenue_total, marge_brute, taux_rec_ni = run_pcam_model(
    eol_volume, eff_ni, eff_li, cost_energy_eu, cost_bm_achat, cap_usine
)


# --- SECTION 1 : RÉSULTATS ÉCONOMIQUES CLÉS ---
st.header("1. COMPARAISON TECHNICO-ÉCONOMIQUE (CYCLE FERMÉ VS OUVERT)")
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="PRODUCTION PCAM POTENTIELLE", 
        value=f"{pcam_pot / 1000:,.1f} K TONNES/AN",
        help="Volume de pCAM produit annuellement par le scénario Européen."
    )

with col2:
    st.metric(
        label="COÛT UNITAIRE PCAM (EUROPE)", 
        value=f"{cost_eu:,.0f} €/TONNE",
        delta_color="inverse",
        delta=f"VS RÉFÉRENCE ASIE ({COUT_PCAM_REF_ASIE:,.0f} €/TONNE)"
    )

with col3:
    st.metric(
        label="MARGE BRUTE ANNUELLE DU PROJET", 
        value=f"{marge_brute / 1000000:,.0f} M€",
    )

with col4:
    st.metric(
        label="POINT MORT (ESTIMÉ)", 
        value=f"{cost_total_eu / revenue_total * 100:,.1f} %",
        help="Pourcentage de capacité à atteindre pour couvrir les coûts totaux."
    )

st.markdown("---")

# --- SECTION 2 : ANALYSE DE SENSIBILITÉ ET COÛT ---
st.header("2. ANALYSE DE SENSIBILITÉ ET DE CONTRAINTE")
st.markdown("---")

df_couts = pd.DataFrame({
    'COÛT': ['CYCLE FERMÉ EUROPE', 'CYCLE OUVERT ASIE (RÉFÉRENCE)'],
    'VALEUR': [cost_eu, COUT_PCAM_REF_ASIE]
})

st.subheader("COÛT UNITAIRE PCAM : COMPARAISON EU/ASIE")
st.bar_chart(df_couts.set_index('COÛT'))

# Détail des coûts
st.subheader("DÉTAIL DES COÛTS DU CYCLE FERMÉ (EUROPE)")
df_detail_cout = pd.DataFrame({
    'POSTE DE COÛT': ['ACHAT BLACK MASS', 'ÉNERGIE (OPEX)', 'INVESTISSEMENT (CAPEX)'],
    'PART (€)': [cost_bm_achat * 1000, cost_energy_eu * 1000, cap_usine * 1000],
    'POURCENTAGE (%)': [
        (cost_bm_achat * 1000) / (cost_bm_achat * 1000 + cost_energy_eu * 1000 + cap_usine * 1000) * 100,
        (cost_energy_eu * 1000) / (cost_bm_achat * 1000 + cost_energy_eu * 1000 + cap_usine * 1000) * 100,
        (cap_usine * 1000) / (cost_bm_achat * 1000 + cost_energy_eu * 1000 + cap_usine * 1000) * 100
    ]
})
st.dataframe(df_detail_cout.style.format({'PART (€)': "{:,.0f}", 'POURCENTAGE (%)': "{:,.1f}%"}))

# Dans la section CONSTANTES ET HYPOTHÈSES DE BASE, vérifiez que cette ligne est correcte :
CAPEX_USINE_TONNE_AN = 1500.0     # Valeur numérique avec .0 pour être sûr

# Dans la section sidebar :
# Utiliser 'format="%.2f"' pour les décimales et 'format="%d"' pour les entiers si besoin
cost_energy_eu = st.sidebar.number_input(
    "COÛT ÉNERGÉTIQUE EUROPE (€/KWH)", 
    min_value=0.10, 
    max_value=0.30, 
    value=0.18, 
    step=0.01, 
    format="%.2f", # Maintenu avec formatage si vous voulez deux décimales
    help="Facteur OPEX majeur pour l'hydrométallurgie."
)

cost_bm_achat = st.sidebar.number_input(
    "COÛT D'ACHAT DE LA BLACK MASS (€/TONNE)", 
    min_value=1500, 
    max_value=3000, 
    value=2200, 
    step=100,
    format="%d" # Forcer l'entier
)

cap_usine = st.sidebar.number_input(
    "CAPEX ANNUALISÉ USINE (€/TONNE BM TRAITÉE)", 
    min_value=1000, 
    max_value=3000, 
    value=1500, # CAPEX_USINE_TONNE_AN était 1500.0, valeur initiale rétablie
    step=100,
    format="%d", # Forcer l'entier
    help="Coût d'investissement de l'usine ramené à la tonne traitée annuellement."
)
