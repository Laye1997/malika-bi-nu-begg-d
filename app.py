import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials

# ============================================================
# 🔐 AUTHENTIFICATION GOOGLE SHEETS (MÉTHODE STABLE)
# ============================================================

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# ⚠️ credentials.json DOIT être uploadé dans Streamlit Cloud
creds = Credentials.from_service_account_file(
    "credentials.json",
    scopes=SCOPES
)

client = gspread.authorize(creds)

SHEET_ID = st.secrets["SHEET_ID"]

sheet = client.open_by_key(SHEET_ID)
worksheet = sheet.worksheet("Liste des membres")

# ============================================================
# 📥 FONCTIONS DATA
# ============================================================

def load_data():
    return pd.DataFrame(worksheet.get_all_records())

def add_member(prenom, nom, adresse, telephone, cni):
    worksheet.append_row([prenom, nom, adresse, telephone, cni])

# ============================================================
# 🔐 AUTHENTIFICATION ADMIN
# ============================================================

USERS = {"admin": "mbb2025"}

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "username" not in st.session_state:
    st.session_state.username = None

# ============================================================
# 🎨 CONFIGURATION DE LA PAGE
# ============================================================

st.set_page_config(page_title="BD2027 – MBB", page_icon="📘", layout="wide")

st.markdown("""
    <style>
        :root { --vert-fonce:#145A32; --jaune-mbb:#F4D03F; }
        .stApp {
            background: linear-gradient(120deg, var(--vert-fonce), var(--jaune-mbb));
            color: white;
            font-family: "Segoe UI", sans-serif;
        }
        h1,h2,h3 { color:white !important; }
        .banner {
            background: linear-gradient(90deg, var(--vert-fonce), var(--jaune-mbb));
            padding:12px;
            border-radius:10px;
            text-align:center;
            font-weight:bold;
            font-size:20px;
            margin-bottom:20px;
        }
        header, footer, #MainMenu { display:none !important; }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# 🏠 PAGE D’ACCUEIL
# ============================================================

st.markdown("<div class='banner'>Plateforme Officielle – BD2027 MBB</div>", unsafe_allow_html=True)
st.title("Inscription des membres")

col1, col2 = st.columns(2)

# ------------------------------------------------------------
# 📝 INSCRIPTION MEMBRE
# ------------------------------------------------------------
with col1:
    st.subheader("📝 Inscription")

    prenom = st.text_input("Prénom")
    nom = st.text_input("Nom")
    telephone = st.text_input("Téléphone")
    adresse = st.text_input("Quartier")
    cni = st.text_input("CNI (optionnel)")

    if st.button("S'inscrire"):
        if prenom and nom and telephone:
            add_member(prenom, nom, adresse, telephone, cni)
            st.success("🎉 Inscription réussie ! Bienvenue dans le mouvement MBB.")
        else:
            st.error("⚠️ Prénom, nom et téléphone sont obligatoires.")

# ------------------------------------------------------------
# 🔐 CONNEXION ADMIN
# ------------------------------------------------------------
with col2:
    st.subheader("🔐 Connexion administrateur")

    if not st.session_state.authenticated:
        username = st.text_input("Identifiant")
        password = st.text_input("Mot de passe", type="password")

        if st.button("Connexion"):
            if USERS.get(username) == password:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success("Connexion réussie")
                st.rerun()
            else:
                st.error("Identifiants incorrects")
    else:
        st.success(f"Connecté en tant que **{st.session_state.username}**")
        if st.button("Déconnexion"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.rerun()

# ============================================================
# 📘 ESPACE ADMIN
# ============================================================

if st.session_state.authenticated:
    st.markdown("---")
    st.header("📘 Base de données des membres")

    df = load_data()
    st.dataframe(df, use_container_width=True)

    if "Adresse" in df.columns:
        st.subheader("📊 Répartition par quartier")
        stats = df["Adresse"].value_counts().reset_index()
        stats.columns = ["Quartier", "Nombre"]

        fig = px.bar(stats, x="Quartier", y="Nombre", text="Nombre")
        st.plotly_chart(fig, use_container_width=True)
