import streamlit as st
import os
from datetime import datetime
import plotly.express as px
import folium
from streamlit_folium import st_folium

# ============================================================
# 🔧 CONFIGURATION
# ============================================================

FORM_URL = "https://docs.google.com/forms/d/e/XXXXXXXX/viewform?embedded=true"
VISUEL = "561812309_122099008227068424_7173387226638749981_n.jpg"

USERS = {
    "admin": "mbb2025",
    "president": "malika2025"
}

st.set_page_config(
    page_title="Base de données MBB",
    page_icon="📘",
    layout="wide"
)

# ============================================================
# 🎨 STYLE GLOBAL
# ============================================================

st.markdown("""
<style>
:root { --vert:#145A32; --jaune:#F4D03F; }
.stApp {
    background: linear-gradient(120deg, var(--vert), var(--jaune));
    color:white;
    font-family:"Segoe UI", sans-serif;
}
h1,h2,h3 { color:white !important; }
.banner {
    background: linear-gradient(90deg, var(--vert), var(--jaune));
    padding:14px;
    border-radius:12px;
    text-align:center;
    font-size:22px;
    font-weight:bold;
    box-shadow:2px 2px 12px rgba(0,0,0,.35);
}
.stButton>button {
    background: linear-gradient(45deg, var(--vert), var(--jaune));
    color:white;
    font-weight:bold;
    border-radius:12px;
    width:100%;
}
.stButton>button:hover {
    background: linear-gradient(45deg, var(--jaune), var(--vert));
    color:black;
}
header[data-testid="stHeader"], footer, #MainMenu { display:none; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 🔐 SESSION
# ============================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None

# ============================================================
# 🖼️ VISUEL
# ============================================================

if os.path.exists(VISUEL):
    st.image(VISUEL, use_container_width=True)

# ============================================================
# 🧭 NAVIGATION
# ============================================================

tabs = st.tabs([
    "🏠 Accueil",
    "🗳️ Carte électorale",
    "🔐 Administration"
])

# ============================================================
# 🏠 ONGLET ACCUEIL — FORMULAIRE PUBLIC
# ============================================================

with tabs[0]:
    st.markdown("<div class='banner'>MALIKA BI ÑU BËGG – Une nouvelle ère s’annonce 🌍</div>", unsafe_allow_html=True)

    st.title("📘 Mouvement BD2027 – MBB")
    st.subheader("📝 Inscription comme membre")

    st.markdown(
        f"""
        <iframe 
            src="{FORM_URL}" 
            width="100%" 
            height="900" 
            frameborder="0">
        Chargement…
        </iframe>
        """,
        unsafe_allow_html=True
    )

# ============================================================
# 🗳️ ONGLET CARTE ÉLECTORALE
# ============================================================

with tabs[1]:
    st.subheader("🗳️ Carte électorale – Commune de Malika")

    data_centres = {
        "Centre": ["École Malika Montagne", "École Privée Sanka", "École Seydi Anta Gadiaga"],
        "Bureaux": [14, 20, 18],
        "Lat": [14.7889, 14.7858, 14.7915],
        "Lon": [-17.3085, -17.3120, -17.3048]
    }

    fig = px.bar(
        data_centres,
        x="Centre",
        y="Bureaux",
        color="Centre",
        text="Bureaux",
        title="Répartition des bureaux de vote"
    )
    st.plotly_chart(fig, use_container_width=True)

    m = folium.Map(location=[14.7889, -17.3090], zoom_start=15)
    for i in range(len(data_centres["Centre"])):
        folium.Marker(
            [data_centres["Lat"][i], data_centres["Lon"][i]],
            popup=data_centres["Centre"][i],
            icon=folium.Icon(color="green")
        ).add_to(m)

    st_folium(m, height=450)

# ============================================================
# 🔐 ONGLET ADMINISTRATION
# ============================================================

with tabs[2]:
    st.subheader("🔐 Connexion administrateur")

    if not st.session_state.authenticated:
        user = st.text_input("Identifiant")
        pwd = st.text_input("Mot de passe", type="password")

        if st.button("Se connecter"):
            if user in USERS and USERS[user] == pwd:
                st.session_state.authenticated = True
                st.session_state.username = user
                st.success("Connexion réussie ✔")
                st.rerun()
            else:
                st.error("Identifiants incorrects.")
    else:
        st.success(f"Connecté en tant que **{st.session_state.username}**")
        st.info("Les réponses sont stockées automatiquement dans Google Sheets.")
        st.markdown("📊 Consulte-les directement dans Google Forms → Réponses")

        if st.button("Déconnexion"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.rerun()
