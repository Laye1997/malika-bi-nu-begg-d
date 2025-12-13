import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px

# ======================================================
# 🔐 CONFIGURATION GOOGLE SHEETS
# ======================================================

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

CREDS = Credentials.from_service_account_file(
    "credentials.json",
    scopes=SCOPE
)

CLIENT = gspread.authorize(CREDS)

# ID du google sheet (pris dans ton lien)
SHEET_ID = "1hqZUWm0_i5kruXugBZupfYz967JsqbXhK_cWaV3bsbM"

# Chargement du sheet
sheet = CLIENT.open_by_key(SHEET_ID)
worksheet = sheet.worksheet("Liste des membres")

# ======================================================
# 🟢 Fonction pour lire la base
# ======================================================
def load_data():
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    return df

# ======================================================
# 🔵 Fonction pour ajouter un membre
# ======================================================
def add_member(prenom, nom, adresse, telephone, cni):
    worksheet.append_row([prenom, nom, adresse, telephone, cni])


# ======================================================
# 🚨 AUTHENTIFICATION ADMIN
# ======================================================

USERS = {"admin": "mbb2025"}

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "username" not in st.session_state:
    st.session_state.username = None

# ======================================================
# 🟩 PAGE D’ACCUEIL = INSCRIPTION + ADMIN LOGIN
# ======================================================

st.title("BD2027 – Mouvement MBB")
st.markdown("### Plateforme officielle d'inscription")

col1, col2 = st.columns(2)

# ------------------------------------------------------
# 📝 INSCRIPTION MEMBRE
# ------------------------------------------------------
with col1:
    st.subheader("📝 Inscription comme membre")

    prenom = st.text_input("Prénom")
    nom = st.text_input("Nom")
    telephone = st.text_input("Numéro de téléphone")
    adresse = st.text_input("Adresse (Quartier)")
    cni = st.text_input("Numéro de CNI (optionnel)")

    if st.button("Valider mon inscription"):
        if prenom and nom and telephone:
            add_member(prenom, nom, adresse, telephone, cni)
            st.success("🎉 Inscription réussie ! Vous êtes désormais membre du mouvement MBB.")
        else:
            st.error("Veuillez remplir au moins : Prénom, Nom, Téléphone.")


# ------------------------------------------------------
# 🔐 CONNEXION ADMIN
# ------------------------------------------------------
with col2:
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
                st.error("Identifiants incorrects.")
    else:
        st.success(f"Connecté en tant que : {st.session_state.username}")
        if st.button("Déconnexion"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.rerun()


# ======================================================
# 🟣 ESPACE ADMIN – BASE DE DONNÉES
# ======================================================
if st.session_state.authenticated:

    st.markdown("---")
    st.header("📘 Base de données des membres")

    df = load_data()
    st.dataframe(df, use_container_width=True)

    # ==========================
    # 📊 STATISTIQUES PAR QUARTIER
    # ==========================
    if "Adresse" in df.columns:
        counts = df["Adresse"].value_counts().reset_index()
        counts.columns = ["Quartier", "Nombre"]

        st.subheader("📊 Répartition par quartier")
        fig = px.bar(counts, x="Quartier", y="Nombre", color="Quartier", text="Nombre")
        st.plotly_chart(fig, use_container_width=True)


