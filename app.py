import streamlit as st
import pandas as pd
import os

# === CONFIGURATION ===
FICHIER_EXCEL = "Liste_Membres.xlsx"
CODE_SECRET = "MBB2025"
VISUEL = "561812309_122099008227068424_7173387226638749981_n.jpg"

# === PARAMÈTRES DE LA PAGE ===
st.set_page_config(page_title="Base de données MBB", page_icon="📘", layout="wide")

# === STYLE PERSONNALISÉ AUX COULEURS DU VISUEL ===
st.markdown("""
    <style>
        :root {
            --vert-mbb: #145A32;
            --vert-clair: #7DCEA0;
            --jaune-mbb: #F4D03F;
            --fond-blanc: #FFFFFF;
            --texte-fonce: #1C2833;
        }

        .stApp {
            background-color: var(--fond-blanc);
            color: var(--texte-fonce);
            font-family: "Segoe UI", sans-serif;
        }

        h1, h2, h3 {
            color: var(--vert-mbb);
            font-weight: 700;
        }

        p, label, span, div {
            color: var(--texte-fonce);
        }

        /* === Boutons === */
        .stButton>button {
            background-color: var(--vert-mbb);
            color: white;
            border-radius: 10px;
            font-weight: bold;
            border: none;
        }
        .stButton>button:hover {
            background-color: var(--jaune-mbb);
            color: black;
            border: 1px solid var(--vert-mbb);
        }

        /* === Tableau === */
        .stDataFrame {
            border: 2px solid var(--vert-mbb);
            border-radius: 10px;
        }

        [data-testid="stDataFrame"] table tbody tr:hover {
            background-color: #D4EFDF !important;
            color: var(--texte-fonce) !important;
            cursor: pointer;
        }

        /* === Champs de saisie === */
        input, textarea {
            border-radius: 6px !important;
            border: 1px solid #ccc !important;
            color: var(--texte-fonce) !important;
        }

        /* === Barre de recherche et boutons du tableau === */
        [data-testid="stDataFrame"] input[type="text"] {
            background-color: #FFFFFF !important;
            color: var(--texte-fonce) !important;
            border: 1px solid var(--vert-mbb) !important;
            border-radius: 6px !important;
            padding: 5px 10px !important;
        }

        [data-testid="stToolbar"] button {
            background-color: var(--vert-mbb) !important;
            color: white !important;
            border-radius: 6px !important;
            border: none !important;
        }

        [data-testid="stToolbar"] button:hover {
            background-color: var(--jaune-mbb) !important;
            color: black !important;
        }

        /* === Bandeau supérieur === */
        .banner {
            background-color: var(--vert-mbb);
            color: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            font-weight: bold;
            font-size: 22px;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# === AFFICHAGE DU VISUEL ET TITRE ===
if os.path.exists(VISUEL):
    st.image(VISUEL, use_container_width=True)
else:
    st.warning("⚠️ Image du visuel non trouvée.")

st.markdown("<div class='banner'>MALIKA BI ÑU BËGG – Une nouvelle ère s’annonce 🌍</div>", unsafe_allow_html=True)
st.title("📘 Base de données du Mouvement - MBB")
st.markdown("Bienvenue dans la base de données des membres de **Malika Bi Ñu Bëgg**.")

# === AFFICHAGE DU TABLEAU ===
if not os.path.exists(FICHIER_EXCEL):
    st.error(f"Le fichier {FICHIER_EXCEL} est introuvable.")
else:
    df = pd.read_excel(FICHIER_EXCEL, sheet_name="Liste des membres", header=1)

    st.subheader("👥 Liste actuelle des membres")
    st.dataframe(df, use_container_width=True)

    st.divider()

    # === FORMULAIRE D'AJOUT ===
    st.subheader("➕ Ajouter un nouveau membre")

    code = st.text_input("Entrez le code d'accès pour ajouter un membre :", type="password")

    if code == CODE_SECRET:
        with st.form("ajout_membre"):
            col1, col2 = st.columns(2)
            with col1:
                prenom = st.text_input("Prénom")
                nom = st.text_input("Nom")
                telephone = st.text_input("Téléphone")
                profession = st.text_input("Profession")
            with col2:
                adresse = st.text_input("Adresse (quartier)")
                commission = st.text_input("Commission")
                notes = st.text_area("Notes")

            submitted = st.form_submit_button("Ajouter le membre")

            if submitted:
                if prenom and nom:
                    new_row = {
                        "Prénom": prenom,
                        "Nom": nom,
                        "Adresse": adresse,
                        "Téléphone": telephone,
                        "Profession": profession,
                        "Commission": commission,
                        "Notes": notes
                    }
                    df = pd.co
