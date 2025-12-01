import streamlit as st

st.set_page_config(
    page_title="European pCAM Reshoring Decision Tool",
    layout="wide"
)

# HEADER
st.markdown("""
# European pCAM Reshoring Decision Tool  
Version 1.0 — Prototype pour décision stratégique Verkor / IFP School
""")

st.markdown("""
Ce logiciel d’aide à la décision permet d’évaluer la pertinence d’une relocalisation européenne
de la production de pré-cathode active material (pCAM), basée sur le recyclage de “black mass”.
Il intègre des scénarios techniques, économiques, industriels et géopolitiques.
""")

# LIENS VERS LES SECTIONS
st.markdown("## Aller à :")
st.markdown("""
- **ACCUEIL**
- **SCÉNARIOS**
- **PARAMÈTRES TECHNIQUES**
- **ANALYSE ÉCONOMIQUE**
- **RÉSULTATS**
- **CONCLUSION**
""")

st.info("Utilisez le menu latéral pour naviguer entre les pages.")

import streamlit as st

st.title("SCÉNARIOS")

st.markdown("""
Cette section permet de configurer les grands scénarios prospectifs pour l’Europe,
en lien avec la production de black mass, le recyclage, et la fabrication de pCAM.
""")

st.subheader("Choix du scénario global")

scenario = st.selectbox(
    "Scénario prospectif",
    ["Optimiste 2035", "Réaliste 2035", "Conservateur 2035"]
)

if scenario == "Optimiste 2035":
    st.markdown("""
    **Hypothèses principales :**
    - Forte croissance du VE  
    - Taux de collecte EOL élevé  
    - Rendements de recyclage améliorés  
    - Forte disponibilité en black mass  
    - Investissements industriels élevés  
    """)
elif scenario == "Réaliste 2035":
    st.markdown("""
    **Hypothèses principales :**
    - Croissance VE modérée  
    - Recyclage maîtrisé mais limité par volumes  
    - Rendements stables  
    - Compétition accrue sur les matières  
    """)
else:  
    st.markdown("""
    **Hypothèses principales :**
    - Retards industriels  
    - Volumes faibles  
    - Forte concurrence sur les imports  
    - Rentabilité incertaine en Europe  
    """)

import streamlit as st

st.title("PARAMÈTRES TECHNIQUES")

st.markdown("Définissez ici les paramètres techniques utilisés dans le modèle.")

col1, col2, col3 = st.columns(3)

with col1:
    nb_batteries = st.number_input("Nombre de batteries recyclées / an", 0, 20000000, 1000000)
    masse_moyenne = st.number_input("Masse moyenne d'une batterie (kg)", 50, 800, 250)

with col2:
    fraction_black_mass = st.slider("Fraction de black mass dans la batterie (%)", 5, 40, 20)
    rendement_recyclage = st.slider("Rendement global du recyclage (%)", 40, 95, 70)

with col3:
    teneur_Ni = st.slider("Teneur en Nickel (%)", 0, 50, 25)
    teneur_Co = st.slider("Teneur en Cobalt (%)", 0, 50, 12)
    teneur_Li = st.slider("Teneur en Lithium (%)", 0, 20, 7)

st.session_state["inputs"] = {
    "nb_batteries": nb_batteries,
    "masse_moyenne": masse_moyenne,
    "fraction_black_mass": fraction_black_mass / 100,
    "rendement": rendement_recyclage / 100,
    "Ni": teneur_Ni / 100,
    "Co": teneur_Co / 100,
    "Li": teneur_Li / 100,
}

import streamlit as st

st.title("ANALYSE ÉCONOMIQUE")

st.markdown("Définissez ici les hypothèses économiques pour le modèle.")

col1, col2 = st.columns(2)

with col1:
    prix_Ni = st.number_input("Prix du Nickel (€/kg)", 5, 200, 22)
    prix_Co = st.number_input("Prix du Cobalt (€/kg)", 5, 200, 35)
    prix_Li = st.number_input("Prix du Lithium (€/kg)", 5, 200, 45)

with col2:
    capex_europe = st.number_input("CAPEX usine Europe (M€)", 10, 2000, 600)
    opex_europe = st.number_input("OPEX Europe (€/t)", 1000, 20000, 4500)
    energie_europe = st.number_input("Coût énergie Europe (€/MWh)", 20, 300, 120)

st.session_state["eco"] = {
    "prix_Ni": prix_Ni,
    "prix_Co": prix_Co,
    "prix_Li": prix_Li,
    "capex": capex_europe,
    "opex": opex_europe,
    "energie": energie_europe,
}

import streamlit as st

st.title("RÉSULTATS")

if "inputs" not in st.session_state or "eco" not in st.session_state:
    st.error("Veuillez remplir les sections 'PARAMÈTRES TECHNIQUES' et 'ANALYSE ÉCONOMIQUE'.")
    st.stop()

a = st.session_state["inputs"]
e = st.session_state["eco"]

# CALCULS
tonnes_batteries = a["nb_batteries"] * a["masse_moyenne"] / 1000
tonnes_blackmass = tonnes_batteries * a["fraction_black_mass"]
tonnes_metaux = {
    "Ni": tonnes_blackmass * a["Ni"] * a["rendement"],
    "Co": tonnes_blackmass * a["Co"] * a["rendement"],
    "Li": tonnes_blackmass * a["Li"] * a["rendement"]
}
revenu = (tonnes_metaux["Ni"] * e["prix_Ni"]
         + tonnes_metaux["Co"] * e["prix_Co"]
         + tonnes_metaux["Li"] * e["prix_Li"])

# AFFICHAGE
st.subheader("Volumes calculés")
st.write(f"- Batteries : **{tonnes_batteries:,.0f} t/an**")
st.write(f"- Black mass : **{tonnes_blackmass:,.0f} t/an**")
st.write(f"- Nickel récupéré : **{tonnes_metaux['Ni']:,.0f} t/an**")
st.write(f"- Cobalt récupéré : **{tonnes_metaux['Co']:,.0f} t/an**")
st.write(f"- Lithium récupéré : **{tonnes_metaux['Li']:,.0f} t/an**")

st.subheader("Résultats économiques")
st.write(f"Revenu total estimé : **{revenu/1e6:.2f} M€ / an**")

# RECOMMANDATION
st.subheader("Recommandation stratégique")

if revenu > e["capex"] * 1e6 / 10:
    st.success("La relocalisation européenne apparaît **économiquement favorable**.")
else:
    st.warning("La relocalisation européenne est **risquée économiquement** dans ce scénario.")

import streamlit as st

st.title("CONCLUSION")

st.markdown("""
### Synthèse stratégique

Ce prototype d’outil permet d’évaluer les conditions dans lesquelles
une relocalisation européenne de la production de pCAM devient réaliste
et économiquement pertinente.

### Points clés à retenir

- Les volumes européens de black mass seront critiques avant 2030  
- La rentabilité dépend fortement des prix Ni / Co / Li  
- Les coûts énergétiques européens restent un frein majeur  
- Les politiques publiques et réglementations (EU Battery Regulation) seront déterminantes  
- La concurrence asiatique restera forte au niveau pCAM/CAM  

### Prochaines étapes
- Intégration de données industrielles réelles  
- Ajout d’analyses ACV / carbone  
- Modèle économique détaillé  
- Module géopolitique (export de black mass)
""")

streamlit
plotly
pandas
numpy
