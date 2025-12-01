import streamlit as st
import pandas as pd
import numpy as np

# ---------------------------------------------------------
# CONFIGURATION DE LA PAGE
# ---------------------------------------------------------
st.set_page_config(
    page_title="EU pCAM Decision Tool",
    page_icon="🔋",
    layout="wide"
)

# ---------------------------------------------------------
# TITRE PRINCIPAL
# ---------------------------------------------------------
st.title("🔋 European pCAM Reshoring Decision Tool")
st.caption("Version 1.0 — Prototype pour décision stratégique Verkor / IFP School")

# ---------------------------------------------------------
# SIDEBAR - NAVIGATION
# ---------------------------------------------------------
st.sidebar.title("📌 Navigation")

page = st.sidebar.radio(
    "Aller à :",
    [
        "🏠 Accueil",
        "📦 Scénarios",
        "⚙️ Paramètres techniques",
        "💰 Analyse économique",
        "📊 Résultats & Recommandation",
        "🧩 Conclusion"
    ]
)

# ---------------------------------------------------------
# VARIABLES GLOBALES — Tout regrouper ici
# ---------------------------------------------------------

st.sidebar.title("🔧 Paramètres rapides")

# Nombre de batteries recyclées
batteries = st.sidebar.number_input(
    "Nombre de batteries recyclées/an",
    min_value=1000,
    max_value=1_000_000,
    value=10000,
    step=1000
)

# Masse moyenne d'une batterie (kg)
battery_mass = st.sidebar.slider(
    "Masse moyenne d'une batterie (kg)",
    100, 700, 450
)

# Teneur en matériaux (% massiques)
st.sidebar.subheader("Composition moyenne (%)")
perc_Li = st.sidebar.slider("Lithium (%)", 0.5, 5.0, 1.5)
perc_Ni = st.sidebar.slider("Nickel (%)", 5.0, 20.0, 10.0)
perc_Co = st.sidebar.slider("Cobalt (%)", 1.0, 10.0, 4.0)

# Rendements de récupération
st.sidebar.subheader("Rendements (%)")
yield_Li = st.sidebar.slider("Rendement Li (%)", 20, 95, 70)
yield_Ni = st.sidebar.slider("Rendement Ni (%)", 40, 98, 90)
yield_Co = st.sidebar.slider("Rendement Co (%)", 40, 98, 92)

# Prix des métaux (€ / tonne)
st.sidebar.subheader("Prix des métaux (€ / tonne)")
price_Li = st.sidebar.number_input("Prix Lithium", value=15000)
price_Ni = st.sidebar.number_input("Prix Nickel", value=18000)
price_Co = st.sidebar.number_input("Prix Cobalt", value=30000)

# Scénario
scenario = st.sidebar.selectbox(
    "Scénario géographique",
    ["Europe", "Chine"]
)

# ---------------------------------------------------------
# CALCULS — matériaux récupérés et valeur
# ---------------------------------------------------------

def calculate_materials():
    total_mass = batteries * battery_mass

    mass_Li = total_mass * (perc_Li/100) * (yield_Li/100)
    mass_Ni = total_mass * (perc_Ni/100) * (yield_Ni/100)
    mass_Co = total_mass * (perc_Co/100) * (yield_Co/100)

    return mass_Li, mass_Ni, mass_Co


def calculate_value(mass_Li, mass_Ni, mass_Co):
    value = (
        mass_Li/1000 * price_Li +
        mass_Ni/1000 * price_Ni +
        mass_Co/1000 * price_Co
    )
    return value


def calculate_costs():
    """
    Exemple : coûts approximatifs (placeholder)
    À remplacer par vos valeurs réelles.
    """
    if scenario == "Europe":
        capex = 120_000_000
        opex = 500 * batteries
    else:
        capex = 70_000_000
        opex = 350 * batteries
    
    return capex + opex


def recommendation(value, costs):
    if value > costs:
        return "🟢 Recommandation : La relocalisation est économiquement viable."
    else:
        return "🔴 Recommandation : La relocalisation n'est PAS rentable dans ce scénario."


# ---------------------------------------------------------
# PAGE : ACCUEIL
# ---------------------------------------------------------
if page == "🏠 Accueil":
    st.header("🎯 Objectif du simulateur")
    st.write("""
    Cet outil permet d'évaluer **la pertinence économique et stratégique** d'une relocalisation 
    de la production de pCAM en Europe à partir du recyclage des batteries électriques.
    
    Il compare différents scénarios :
    - Recyclage et hydrométallurgie en Europe vs Chine  
    - Cycle ouvert (métaux minés) vs cycle fermé (métaux recyclés)  
    - Rentabilité pour un OEM ou une Gigafactory
    
    👉 L'objectif final : **décider si la relocalisation européenne est viable**.
    """)

# ---------------------------------------------------------
# PAGE : SCÉNARIOS
# ---------------------------------------------------------
elif page == "📦 Scénarios":
    st.header("📦 Scénarios de comparaison")
    st.write("""
    Trois scénarios principaux sont analysés :

    1. **Cycle ouvert – Chine**
       - Importation de métaux neufs
       - Exportation de la black mass
       - Forte dépendance extérieure

    2. **Cycle fermé – Europe**
       - Recyclage local
       - Hydrométallurgie + fabrication de pCAM
       - Réduction de la dépendance stratégique

    3. **Cycle hybride**
       - Black mass envoyée en Europe
       - Hydrométallurgie locale
    """)

# ---------------------------------------------------------
# PAGE : PARAMÈTRES TECHNIQUES
# ---------------------------------------------------------
elif page == "⚙️ Paramètres techniques":
    st.header("⚙️ Paramètres techniques")
    st.write("""
    Tous les paramètres ont été définis dans la barre latérale.
    Utilisez-la pour modifier :
    - le nombre de batteries  
    - la masse moyenne  
    - la composition matériaux  
    - les rendements de récupération  
    """)

# ---------------------------------------------------------
# PAGE : ANALYSE ÉCONOMIQUE
# ---------------------------------------------------------
elif page == "💰 Analyse économique":
    st.header("💰 Analyse économique")

    mass_Li, mass_Ni, mass_Co = calculate_materials()
    value = calculate_value(mass_Li, mass_Ni, mass_Co)
    costs = calculate_costs()

    st.subheader("📦 Matériaux récupérés")
    st.write(f"Lithium récupéré : **{mass_Li/1000:.1f} tonnes**")
    st.write(f"Nickel récupéré : **{mass_Ni/1000:.1f} tonnes**")
    st.write(f"Cobalt récupéré : **{mass_Co/1000:.1f} tonnes**")

    st.subheader("💰 Valeur totale récupérée")
    st.write(f"**{value:,.0f} €**")

    st.subheader("💸 Coûts estimés")
    st.write(f"**{costs:,.0f} €**")

# ---------------------------------------------------------
# PAGE : RÉSULTATS & RECOMMANDATION
# ---------------------------------------------------------
elif page == "📊 Résultats & Recommandation":
    st.header("📊 Résultats")
    mass_Li, mass_Ni, mass_Co = calculate_materials()
    value = calculate_value(mass_Li, mass_Ni, mass_Co)
    costs = calculate_costs()

    st.metric("Valeur totale des métaux récupérés", f"{value:,.0f} €")
    st.metric("Coûts estimés", f"{costs:,.0f} €")

    st.subheader("🔍 Recommandation automatique")
    st.write(recommendation(value, costs))

# ---------------------------------------------------------
# PAGE : CONCLUSION
# ---------------------------------------------------------
elif page == "🧩 Conclusion":
    st.header("🧩 Conclusion")
    st.write("""
    Ce simulateur montre qu'une relocalisation de la production de pCAM dépend fortement :
    
    - du **volume de batteries disponibles**  
    - du **rendement des procédés européens**  
    - des **prix des métaux critiques**  
    - des **coûts industriels en Europe**  

    Le modèle peut être affiné avec :
    - les vraies données industrielles Verkor/IFPEN  
    - l'évolution des prix du marché  
    - les objectifs EU Battery Regulation  

    👉 Prêt à intégrer des données réelles pour une étude complète.
    """)
