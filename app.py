import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
import folium
from streamlit_folium import st_folium

# === CONFIGURATION ===
FICHIER_EXCEL = "Liste_Membres.xlsx"
VISUEL = "561812309_122099008227068424_7173387226638749981_n.jpg"

# === IDENTIFIANTS ADMIN ===
USERS = {
    "admin": "mbb2025"
}

# === PARAMÈTRES DE LA PAGE ===
st.set_page_config(page_title="Base de données MBB", page_icon="📘", layout="wide")

# === STYLE GLOBAL ===
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
            font-weight:bold; font-size:20px; margin-bottom:15px; box-shadow:2px 2px 10px rgba(0,0,0,0.3);
        }
        .stButton>button {
            background: linear-gradient(45deg, var(--vert-fonce), var(--jaune-mbb));
            color:white; border-radius:10px; font-weight:bold; border:none; width:100%;
            box-shadow:1px 1px 4px rgba(0,0,0,0.3);
        }
        .stButton>button:hover {
            background: linear-gradient(45deg, var(--jaune-mbb), var(--vert-fonce)); color:black;
        }
        header[data-testid="stHeader"], #MainMenu, footer { display:none !important; }
    </style>
""", unsafe_allow_html=True)


# === SESSION ===
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None


# === CHARGEMENT DU FICHIER EXCEL ===
if not os.path.exists(FICHIER_EXCEL):
    st.error("❌ ERREUR : Le fichier Liste_Membres.xlsx est introuvable.")
    st.stop()


# Charger l'Excel (les colonnes sont à la ligne 2 → header=1)
df = pd.read_excel(FICHIER_EXCEL, sheet_name="Liste des membres", header=1)

# Normalisation
df.columns = df.columns.str.strip()

# Détection colonne Adresse
col_adresse = [c for c in df.columns if "Adresse" in c]
nb_quartiers = len(df[col_adresse[0]].dropna().unique()) if col_adresse else 0


# ============================================================
# 🔰 PAGE D'ACCUEIL — INSCRIPTION + CONNEXION ADMIN
# ============================================================
st.markdown("<div class='banner'>Espace membres – BD2027 MBB</div>", unsafe_allow_html=True)
st.title("Bienvenue sur la plateforme d'inscription du Mouvement MBB")

col_insc, col_conn = st.columns(2)


# ------------------------------------------------------------
# 🔵 COLONNE D'INSCRIPTION
# ------------------------------------------------------------
with col_insc:
    st.subheader("📝 Inscription comme membre")

    prenom = st.text_input("Prénom")
    nom = st.text_input("Nom")
    telephone = st.text_input("Numéro de téléphone")
    adresse = st.text_input("Quartier (Adresse)")
    cni = st.text_input("Numéro de CNI (optionnel)")

    if st.button("Valider mon inscription"):
        if prenom and nom and telephone:

            new_row = {
                "Prenom": prenom,
                "Nom": nom,
                "Adresse": adresse,
                "Numéro de téléphone": telephone,
                "Profession": None,
                "Commision": None,
                "Notes": cni
            }

            df_to_write = pd.read_excel(FICHIER_EXCEL, sheet_name="Liste des membres", header=1)
            df_to_write = pd.concat([df_to_write, pd.DataFrame([new_row])], ignore_index=True)

            with pd.ExcelWriter(FICHIER_EXCEL, engine="openpyxl", mode="w") as writer:
                df_to_write.to_excel(writer, index=False, sheet_name="Liste des membres")

            st.success("🎉 Inscription réussie ! Vous êtes désormais membre de BD2027 – MBB.")
            st.info("📲 Rejoignez-nous sur nos réseaux sociaux : Facebook, WhatsApp, Instagram…")

        else:
            st.error("⚠️ Merci de remplir au minimum : prénom, nom et numéro de téléphone.")


# ------------------------------------------------------------
# 🔒 COLONNE CONNEXION ADMIN
# ------------------------------------------------------------
with col_conn:
    st.subheader("🔐 Connexion administrateur")

    if not st.session_state.authenticated:

        username_input = st.text_input("Identifiant admin")
        password_input = st.text_input("Mot de passe", type="password")

        if st.button("Se connecter"):
            if username_input in USERS and USERS[username_input] == password_input:
                st.session_state.authenticated = True
                st.session_state.username = username_input
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
# 🔐 ESPACE ADMIN — AFFICHAGE DE LA BASE DE DONNÉES
# ============================================================
if st.session_state.authenticated:

    st.markdown("<hr>", unsafe_allow_html=True)
    st.header("📘 Base de données MBB – Espace Administrateur")

    st.subheader("Liste complète des membres")
    st.dataframe(df, use_container_width=True)

    # Répartition par quartier
    adresse_col = col_adresse[0]
    st.subheader("Répartition des membres par quartier")

    counts = df[adresse_col].value_counts().reset_index()
    counts.columns = ["Quartier", "Nombre de membres"]

    fig = px.bar(counts, x="Quartier", y="Nombre de membres", color="Quartier",
                 text="Nombre de membres", title="Membres par quartier")
    st.plotly_chart(fig, use_container_width=True)

