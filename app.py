import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials

# ============================================================
# 🔐 CONFIGURATION GOOGLE SHEETS VIA STREAMLIT SECRETS
# ============================================================

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Charger les credentials depuis Streamlit Secrets
creds = Credentials.from_service_account_info(
    st.secrets["google_service_account"],
    scopes=SCOPES
)

client = gspread.authorize(creds)

# ✅ SHEET_ID À LA RACINE DES SECRETS
SHEET_ID = st.secrets["SHEET_ID"]


st.success("Credentials Google chargés avec succès")

# Ouvrir le Google Sheet
sheet = client.open_by_key(SHEET_ID)
worksheet = sheet.worksheet("Liste des membres")

# ============================================================
# 📥 FONCTIONS DATA
# ============================================================

def load_data():
    data = worksheet.get_all_records()
    return pd.DataFrame(data)

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
# 🎨 CONFIG PAGE & STYLE
# ============================================================

st.set_page_config(page_title="Base MBB", page_icon="📘", layout="wide")

st.markdown("""
    <style>
        :root { --vert-fonce:#145A32; --jaune-mbb:#F4D03F; --blanc:#FFFFFF; }
        .stApp {
            background: linear-gradient(120deg, var(--vert-fonce), var(--jaune-mbb));
            color: var(--blanc);
            font-family: "Segoe UI", sans-serif;
        }
        h1,h2,h3 { color:#FFFFFF !important; }
        .banner {
            background: linear-gradient(90deg, var(--vert-fonce), var(--jaune-mbb));
            color:white;
            padding:12px;
            border-radius:10px;
            text-align:center;
            font-weight:bold;
            font-size:20px;
            margin-bottom:15px;
            box-shadow:2px 2px 10px rgba(0,0,0,0.3);
        }
        .stButton>button {
            background: linear-gradient(45deg, var(--vert-fonce), var(--jaune-mbb));
            color:white;
            border-radius:10px;
            font-weight:bold;
            border:none;
            width:100%;
            box-shadow:1px 1px 4px rgba(0,0,0,0.3);
        }
        .stButton>button:hover {
            background: linear-gradient(45deg, var(--jaune-mbb), var(--vert-fonce));
            color:black;
        }
        header[data-testid="stHeader"], #MainMenu, footer { display:none !important; }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# 🏠 PAGE D’ACCUEIL — INSCRIPTION + CONNEXION ADMIN
# ============================================================

st.markdown("<div class='banner'>Plateforme Officielle — BD2027 MBB</div>", unsafe_allow_html=True)
st.title("Bienvenue sur la plateforme d'inscription")

col_insc, col_conn = st.columns(2)

# ------------------------------------------------------------
# 📝 INSCRIPTION MEMBRE
# ------------------------------------------------------------
with col_insc:
    st.subheader("📝 Inscription comme membre")

    prenom = st.text_input("Prénom")
    nom = st.text_input("Nom")
    telephone = st.text_input("Numéro de téléphone")
    adresse = st.text_input("Adresse (quartier)")
    cni = st.text_input("Numéro de CNI (optionnel)")

    if st.button("Valider mon inscription"):
        if prenom and nom and telephone:
            add_member(prenom, nom, adresse, telephone, cni)
            st.success("🎉 Inscription réussie ! Bienvenue dans le mouvement MBB.")
            st.info("📲 Rejoignez-nous sur Facebook, WhatsApp et Instagram.")
        else:
            st.error("⚠️ Merci de remplir au minimum : prénom, nom et téléphone.")

# ------------------------------------------------------------
# 🔐 CONNEXION ADMIN
# ------------------------------------------------------------
with col_conn:
    st.subheader("🔐 Connexion administrateur")

    if not st.session_state.authenticated:
        username = st.text_input("Identifiant admin")
        password = st.text_input("Mot de passe", type="password")

        if st.button("Se connecter"):
            if username in USERS and USERS[username] == password:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success("Connexion réussie ✔")
                st.rerun()
            else:
                st.error("❌ Identifiants incorrects.")
    else:
        st.success(f"Connecté en tant que **{st.session_state.username}**")
        if st.button("Déconnexion"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.rerun()

# ============================================================
# 📘 ESPACE ADMIN — BASE DE DONNÉES + STATISTIQUES
# ============================================================

if st.session_state.authenticated:

    st.markdown("---")
    st.header("📘 Base de données MBB — Espace Administrateur")

    df = load_data()
    st.dataframe(df, use_container_width=True)

    if "Adresse" in df.columns:
        st.subheader("📊 Répartition des membres par quartier")

        counts = df["Adresse"].value_counts().reset_index()
        counts.columns = ["Quartier", "Nombre"]

        fig = px.bar(
            counts,
            x="Quartier",
            y="Nombre",
            color="Quartier",
            text="Nombre",
            title="Répartition des membres par quartier"
        )
        st.plotly_chart(fig, use_container_width=True)

