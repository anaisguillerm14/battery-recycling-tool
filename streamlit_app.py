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
