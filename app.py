import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ======================================================
# 🔐 CONFIGURATION GOOGLE SHEETS
# ======================================================

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Charger credentials depuis Streamlit secrets
CREDS = Credentials.from_service_account_info(
    st.secrets["google_service_account"],
    scopes=SCOPE
)

CLIENT = gspread.authorize(CREDS)

# ID Google Sheet depuis secrets
SHEET_ID = st.secrets["SHEET_ID"]

# Chargement du fichier Google Sheets
sheet = CLIENT.open_by_key(SHEET_ID)
worksheet = sheet.worksheet("Liste des membres")


# ===============================
# 🔍 Fonctions utilitaires
# ===============================

def load_data():
    """Charge toutes les lignes du Google Sheet."""
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    return df


def add_member(prenom, nom, adresse, telephone, cni):
    """Ajoute une ligne dans Google Sheets."""
    worksheet.append_row([prenom, nom, adresse, telephone, cni])


# ======================================================
# 🔐 SECTION ADMIN
# ======================================================

USERS = {"admin": "mbb2025"}

st.set_page_config(page_title="Base de données MBB", page_icon="📘", layout="wide")

st.markdown("""
    <style>
        :root { --vert-fonce:#145A32; --jaune-mbb:#F4D03F; }
        .stApp {
            background: linear-gradient(120deg, var(--vert-fonce), var(--jaune-mbb));
            color: white; font-family: "Segoe UI";
        }
        h1,h2,h3 { color: white !important; }
        .banner {
            background: linear-gradient(90deg, var(--vert-fonce), var(--jaune-mbb));
            padding:12px; text-align:center;
            border-radius:10px; font-weight:bold;
            font-size:22px; margin-bottom:20px;
        }
        .stButton>button {
            background: linear-gradient(45deg, var(--vert-fonce), var(--jaune-mbb));
            color:white; border-radius:10px; border:none; width:100%;
        }
        .stButton>button:hover { opacity:0.9; }
    </style>
""", unsafe_allow_html=True)


# ======================================================
# SESSION
# ======================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False


# ======================================================
# 🏠 PAGE D’ACCUEIL : INSCRIPTION + ADMIN LOGIN
# ======================================================

st.markdown("<div class='banner'>Espace membres – BD2027 MBB</div>", unsafe_allow_html=True)
st.title("Plateforme officielle d'inscription MBB")

col1, col2 = st.columns(2)

# ======================================================
# 📝 FORMULAIRE D’INSCRIPTION
# ======================================================

with col1:
    st.subheader("📝 Inscription comme membre")

    prenom = st.text_input("Prénom")
    nom = st.text_input("Nom")
    telephone = st.text_input("Numéro de téléphone")
    adresse = st.text_input("Quartier (Adresse)")
    cni = st.text_input("Numéro de CNI (optionnel)")

    if st.button("Valider mon inscription"):
        if prenom and nom and telephone:
            add_member(prenom, nom, adresse, telephone, cni)
            st.success("🎉 Inscription réussie ! Vous êtes désormais membre de BD2027 – MBB.")
            st.info("📲 Rejoignez-nous sur nos réseaux sociaux.")
        else:
            st.error("⚠️ Merci de remplir au minimum : prénom, nom et numéro de téléphone.")


# ======================================================
# 🔐 CONNEXION ADMIN
# ======================================================

with col2:
    st.subheader("🔐 Connexion administrateur")

    if not st.session_state.authenticated:

        username = st.text_input("Identifiant")
        password = st.text_input("Mot de passe", type="password")

        if st.button("Se connecter"):
            if username in USERS and USERS[username] == password:
                st.session_state.authenticated = True
                st.success("Connexion réussie ✔")
                st.rerun()
            else:
                st.error("❌ Identifiants incorrects.")
    else:
        st.success("Connecté en tant qu’admin")
        if st.button("Déconnexion"):
            st.session_state.authenticated = False
            st.rerun()


# ======================================================
# 👑 ESPACE ADMIN : BASE DE DONNÉES
# ======================================================

if st.session_state.authenticated:

    st.markdown("<hr>", unsafe_allow_html=True)
    st.header("📘 Base de données des membres MBB")

    df = load_data()

    st.subheader("Liste complète des membres")
    st.dataframe(df, use_container_width=True)

    # -----------------------
    # STATS PAR QUARTIER
    # -----------------------
    if "Adresse" in df.columns and df["Adresse"].nunique() > 0:
        st.subheader("📊 Répartition par quartier")

        counts = df["Adresse"].value_counts().reset_index()
        counts.columns = ["Quartier", "Nombre"]

        fig = px.bar(counts, x="Quartier", y="Nombre", color="Quartier", text="Nombre")
        st.plotly_chart(fig, use_container_width=True)

