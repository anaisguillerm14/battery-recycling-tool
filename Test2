import streamlit as st
import plotly.graph_objects as go

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="Battery Dashboard",
    page_icon="🔋",
    layout="wide"
)

# ---------------------------------------------------
# CUSTOM CSS to mimic dashboard UI
# ---------------------------------------------------
st.markdown("""
<style>
/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Top bar */
.top-bar {
    background-color: #f5f7fa;
    padding: 15px 25px;
    border-radius: 8px;
    margin-bottom: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size:18px;
    font-weight:600;
}

/* Card style */
.card {
    background-color: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    text-align:center;
}

.card h3 {
    font-size: 22px;
    margin-bottom: 5px;
    color:#333;
}

.card .value {
    font-size: 30px;
    font-weight:700;
}

.sidebar-icon {
    font-size:22px;
    margin-right:10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# SIDEBAR WITH ICONS
# ---------------------------------------------------
st.sidebar.title("🔧 MENU")

menu = st.sidebar.radio(
    "",
    [
        "🏠 Dashboard",
        "📊 Données",
        "⚙️ Paramètres",
        "📦 Scénarios",
        "💰 Économie",
        "📄 Rapport"
    ]
)

st.sidebar.write("### 🔋 Battery Tool v1.0")
st.sidebar.write("Made by Team 4")

# ---------------------------------------------------
# TOP BAR
# ---------------------------------------------------
st.markdown('<div class="top-bar">🔋 Battery Recycling Dashboard <span>👤 Team 4</span></div>', unsafe_allow_html=True)

# ---------------------------------------------------
# MAIN PAGE — DASHBOARD
# ---------------------------------------------------
if menu == "🏠 Dashboard":
    st.header("📊 Vue d’ensemble")

    # ----------------------------
    # KPI CARDS
    # ----------------------------
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="card"><h3>Total Batteries</h3><div class="value">12,540</div></div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card"><h3>Black Mass (t)</h3><div class="value">354</div></div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="card"><h3>Yield</h3><div class="value">68%</div></div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="card"><h3>Revenue (€)</h3><div class="value">2.4M</div></div>', unsafe_allow_html=True)

    st.write("")

    # ----------------------------
    # LINE CHART (performance)
    # ----------------------------
    st.subheader("📈 Performance")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        y=[50, 55, 53, 60, 58, 62],
        mode="lines+markers",
        line=dict(width=3)
    ))
    fig.update_layout(height=250, margin=dict(l=20,r=20,t=20,b=20))
    st.plotly_chart(fig, use_container_width=True)

    # ----------------------------
    # BAR CHART (orders)
    # ----------------------------
    st.subheader("📦 Total Orders")

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=[f"M{i}" for i in range(1,13)],
        y=[120, 140, 100, 160, 180, 130, 150, 170, 200, 210, 190, 220]
    ))
    fig2.update_layout(height=250, margin=dict(l=20,r=20,t=20,b=20))
    st.plotly_chart(fig2, use_container_width=True)

# ---------------------------------------------------
# OTHER PAGES (empty skeleton)
# ---------------------------------------------------
elif menu == "📊 Données":
    st.header("📊 Données")
    st.write("Page des données brutes (à compléter).")

elif menu == "⚙️ Paramètres":
    st.header("⚙️ Paramètres")
    st.write("Page paramètres techniques et modèles (à compléter).")

elif menu == "📦 Scénarios":
    st.header("📦 Scénarios")
    st.write("Page scénarios cycle ouvert / fermé, Europe vs Chine.")

elif menu == "💰 Économie":
    st.header("💰 Analyse Économique")
    st.write("Page CAPEX/OPEX et rentabilité ici.")

elif menu == "📄 Rapport":
    st.header("📄 Rapport final")
    st.write("Espace générateur de rapport PDF final.")
