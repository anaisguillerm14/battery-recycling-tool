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
