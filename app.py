import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import folium
from streamlit_folium import st_folium
import requests

# ============================================================
# 🔗 GOOGLE FORM & GOOGLE SHEET
# ============================================================

# Google Form (formResponse)
FORM_BASE_URL = "https://docs.google.com/forms/d/13sosy-0J8AXQVWf3DDKoy8cY9qv_ODJGgaKt08ENrAI/formResponse"

# IDs des champs (entry.xxxxx)
ENTRY_PRENOM = "entry.1181294215"
ENTRY_NOM = "entry.2048123513"
ENTRY_TEL = "entry.915975688"
ENTRY_ADRESSE = "entry.1503668516"
ENTRY_CNI = "entry.732417991"

# Google Sheet → onglet "Form Responses 1"
CSV_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1hqZUWm0_i5kruXugBZupfYz967JsqbXhK_cWaV3bsbM"
    "/export?format=csv&gid=1085189072"
)

# ============================================================
# 🔐 UTILISATEURS ADMIN
# ============================================================

USERS = {
    "admin": "mbb2025",
    "president": "malika2025",
}

# ============================================================
# 🎛️ PAGE
# ============================================================

st.set_page_config(page_title="Base de données MBB", page_icon="📘", layout="wide")

st.markdown("""
<style>
:root { --vert:#145A32; --jaune:#F4D03F; }
.stApp {
    background: linear-gradient(120deg, var(--vert), var(--jaune));
    color:white;
    font-family: "Segoe UI", sans-serif;
}
h1,h2,h3 { color:white !important; }
.banner {
    background: linear-gradient(90deg, var(--vert), var(--jaune));
    padding:14px;
    border-radius:12px;
    text-align:center;
    font-size:22px;
    font-weight:bold;
    margin-bottom:20px;
}
.stButton>button {
    background: linear-gradient(45deg, var(--vert), var(--jaune));
    color:white;
    font-weight:bold;
    border-radius:10px;
    border:none;
}
header, footer, #MainMenu { display:none !important; }
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
# 📥 FONCTIONS
# ============================================================

def post_to_google_form(prenom, nom, tel, adresse, cni):
    payload = {
        ENTRY_PRENOM: prenom,
        ENTRY_NOM: nom,
        ENTRY_TEL: tel,
        ENTRY_ADRESSE: adresse,
        ENTRY_CNI: cni,
    }
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.post(FORM_BASE_URL, data=payload, headers=headers)
    return r.status_code in (200, 302)


@st.cache_data(ttl=30)
def load_google_sheet():
    df = pd.read_csv(CSV_URL)
    df.columns = (
        df.columns.astype(str)
        .str.strip().str.lower()
        .str.replace("é", "e")
        .str.replace("è", "e")
        .str.replace("ê", "e")
        .str.replace("à", "a")
        .str.replace("ç", "c")
    )
    return df


df = load_google_sheet()

# ============================================================
# 🧭 NAVIGATION
# ============================================================

tabs = st.tabs([
    "🏠 Accueil",
    "🏘️ Par Quartier",
    "🗳️ Carte électorale",
    "📝 Compte Rendu"
])

# ============================================================
# 🏠 ACCUEIL
# ============================================================

with tabs[0]:
    st.markdown("<div class='banner'>MALIKA BI ÑU BËGG – Une nouvelle ère s’annonce 🌍</div>", unsafe_allow_html=True)
    st.title("📘 Mouvement BD2027 – MBB")

    st.subheader("📝 Inscription comme membre")

    col_form, col_login = st.columns(2)

    # ================= FORMULAIRE =================
    with col_form:
        with st.form("inscription"):
            prenom = st.text_input("Prénom")
            nom = st.text_input("Nom")
            tel = st.text_input("Numéro de téléphone")
            adresse = st.text_input("Quartier (Adresse)")
            cni = st.text_input("Numéro de CNI (optionnel)")
            submit = st.form_submit_button("Valider mon inscription")

            if submit:
                if not (prenom and nom and tel and adresse):
                    st.warning("⚠️ Champs obligatoires manquants.")
                elif post_to_google_form(prenom, nom, tel, adresse, cni):
                    st.success("✅ Inscription réussie !")
                    st.cache_data.clear()
                else:
                    st.error("❌ Erreur lors de l’envoi.")

    # ================= ADMIN LOGIN =================
    with col_login:
        st.subheader("🔐 Connexion administrateur")
        if not st.session_state.authenticated:
            u = st.text_input("Identifiant")
            p = st.text_input("Mot de passe", type="password")
            if st.button("Se connecter"):
                if u in USERS and USERS[u] == p:
                    st.session_state.authenticated = True
                    st.session_state.username = u
                    st.rerun()
                else:
                    st.error("Identifiants incorrects")
        else:
            st.success(f"Connecté : {st.session_state.username}")
            if st.button("Déconnexion"):
                st.session_state.authenticated = False
                st.session_state.username = None
                st.rerun()

    # ================= LISTE =================
    if st.session_state.authenticated:
        st.divider()
        st.subheader("📋 Liste des membres")
        st.dataframe(df, use_container_width=True)

# ============================================================
# 🏘️ PAR QUARTIER
# ============================================================

with tabs[1]:
    if not st.session_state.authenticated:
        st.warning("🔐 Accès réservé aux administrateurs.")
    else:
        if "adresse" not in df.columns:
            st.error("Colonne adresse introuvable.")
        else:
            stats = df["adresse"].value_counts().reset_index()
            stats.columns = ["Quartier", "Nombre"]
            fig = px.bar(stats, x="Quartier", y="Nombre", color="Quartier", text="Nombre")
            st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 🗳️ CARTE
# ============================================================

with tabs[2]:
    if not st.session_state.authenticated:
        st.warning("🔐 Accès réservé.")
    else:
        m = folium.Map(location=[14.7889, -17.3090], zoom_start=14)
        folium.Marker([14.7889, -17.3085], tooltip="Malika").add_to(m)
        st_folium(m, width=800)

# ============================================================
# 📝 COMPTE RENDU
# ============================================================

with tabs[3]:
    if not st.session_state.authenticated:
        st.warning("🔐 Accès réservé.")
    else:
        st.info("À venir.")
