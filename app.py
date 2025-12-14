import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import folium
from streamlit_folium import st_folium

# =========================================================
# 🔧 CONFIGURATION (SANS SECRET / SANS CLÉ)
# =========================================================

FORM_URL = "https://docs.google.com/forms/d/e/XXXX/viewform"
SHEET_ID = "1hqZUWm0_i5kruXugBZupfYz967JsqbXhK_cWaV3bsbM"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

VISUEL = "561812309_122099008227068424_7173387226638749981_n.jpg"

USERS = {
    "admin": "mbb2025",
    "president": "malika2025"
}

# =========================================================
# 🎨 PAGE
# =========================================================

st.set_page_config(page_title="Base de données MBB", page_icon="📘", layout="wide")

st.markdown("""
<style>
:root { --vert-fonce:#145A32; --jaune-mbb:#F4D03F; --blanc:#FFFFFF; }
.stApp {
    background: linear-gradient(120deg, var(--vert-fonce), var(--jaune-mbb));
    color: var(--blanc); font-family: "Segoe UI", sans-serif;
}
h1,h2,h3 { color:#FFFFFF !important; }
.banner {
    background: linear-gradient(90deg, var(--vert-fonce), var(--jaune-mbb));
    color:white; padding:12px; border-radius:10px; text-align:center;
    font-weight:bold; font-size:20px; margin-bottom:15px;
}
.stButton>button {
    background: linear-gradient(45deg, var(--vert-fonce), var(--jaune-mbb));
    color:white; border-radius:10px; font-weight:bold; width:100%;
}
header[data-testid="stHeader"], #MainMenu, footer { display:none !important; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 🔐 SESSION
# =========================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None

# =========================================================
# 📥 CHARGEMENT DONNÉES (LECTURE SEULE)
# =========================================================

@st.cache_data(ttl=60)
def load_data():
    return pd.read_csv(CSV_URL)

try:
    df = load_data()
except:
    df = pd.DataFrame()

df.columns = df.columns.str.strip().str.lower()

col_adresse = [c for c in df.columns if "quartier" in c or "adresse" in c]
nb_quartiers = len(df[col_adresse[0]].dropna().unique()) if col_adresse else 0

# =========================================================
# 🧭 NAVIGATION
# =========================================================

tabs = st.tabs([
    "🏠 Accueil",
    f"🏘️ Par Quartier ({nb_quartiers})",
    "🗳️ Carte électorale",
    "📝 Compte rendu"
])

# =========================================================
# 🏠 ACCUEIL
# =========================================================

with tabs[0]:
    st.markdown("<div class='banner'>MALIKA BI ÑU BËGG – Une nouvelle ère s’annonce 🌍</div>", unsafe_allow_html=True)
    st.title("📘 Mouvement BD2027 – MBB")

    st.subheader("📝 Inscription comme membre")
    st.link_button("👉 S'inscrire via le formulaire officiel", FORM_URL)

    st.divider()

    st.subheader("🔐 Connexion administrateur")
    if not st.session_state.authenticated:
        u = st.text_input("Identifiant")
        p = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            if u in USERS and USERS[u] == p:
                st.session_state.authenticated = True
                st.session_state.username = u
                st.success("Connexion réussie")
                st.rerun()
            else:
                st.error("Identifiants incorrects")
    else:
        st.success(f"Connecté en tant que {st.session_state.username}")

# =========================================================
# 🏘️ PAR QUARTIER (ADMIN)
# =========================================================

with tabs[1]:
    if not st.session_state.authenticated:
        st.warning("Accès réservé aux administrateurs")
    else:
        adresse_col = col_adresse[0]
        counts = df[adresse_col].value_counts().reset_index()
        counts.columns = ["Quartier", "Nombre"]

        fig = px.bar(counts, x="Quartier", y="Nombre", color="Quartier", text="Nombre")
        st.plotly_chart(fig, use_container_width=True)

        for q in counts["Quartier"]:
            st.markdown(f"### 📍 {q}")
            st.dataframe(df[df[adresse_col] == q], use_container_width=True)

# =========================================================
# 🗳️ CARTE
# =========================================================

with tabs[2]:
    if not st.session_state.authenticated:
        st.warning("Accès réservé aux administrateurs")
    else:
        m = folium.Map(location=[14.7889, -17.3090], zoom_start=14)
        folium.Marker([14.7889, -17.3085], tooltip="Malika").add_to(m)
        st_folium(m, height=500)

# =========================================================
# 📝 COMPTE RENDU
# =========================================================

with tabs[3]:
    if not st.session_state.authenticated:
        st.warning("Accès réservé aux administrateurs")
    else:
        st.info("Section compte rendu à venir")
