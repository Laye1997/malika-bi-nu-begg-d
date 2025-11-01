import streamlit as st
import pandas as pd
import os

# === CONFIGURATION DE BASE ===
FICHIER_EXCEL = "Liste_Membres.xlsx"
CODE_SECRET = "MBB2025"
VISUEL = "561812309_122099008227068424_7173387226638749981_n.jpg"

# === PARAMÈTRES DE LA PAGE ===
st.set_page_config(
    page_title="Base de données MBB",
    page_icon="📘",
    layout="wide",
)

# === STYLE CSS PERSONNALISÉ ===
st.markdownst.markdown("""
    <style>
        /* ======= COULEURS DU MOUVEMENT ======= */
        :root {
            --vert-mbb: #145A32;
            --vert-clair: #D4EFDF;
            --jaune-mbb: #F4D03F;
            --texte-fonce: #1C2833;
            --fond-blanc: #FFFFFF;
        }

        /* ======= PAGE ======= */
        .stApp {
            background-color: var(--fond-blanc);
            color: var(--texte-fonce);
            font-family: "Segoe UI", sans-serif;
        }

        h1, h2, h3, h4 {
            color: var(--vert-mbb) !important;
            font-weight: 700;
        }

        p, label, span, div {
            color: var(--texte-fonce) !important;
        }

        /* ======= TABLEAU ======= */
        .stDataFrame {
            border: 2px solid var(--vert-mbb);
            border-radius: 10px;
        }

        /* ======= Lignes survolées ======= */
        [data-testid="stDataFrame"] table tbody tr:hover {
            background-color: var(--vert-clair) !important;
            color: var(--texte-fonce) !important;
            cursor: pointer;
        }

        /* ======= BARRE DE RECHERCHE & BOUTONS TABLEAU ======= */
        [data-testid="stDataFrame"] input[type="text"] {
            background-color: #FFFFFF !important;
            color: var(--texte-fonce) !important;
            border: 1px solid var(--vert-mbb) !important;
            border-radius: 6px !important;
            padding: 5px 10px !important;
        }

        [data-testid="stDataFrame"] input[type="text"]::placeholder {
            color: #555 !important;
        }

        /* Boutons (loupe, plein écran, téléchargement) */
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

        /* ======= BOUTONS GÉNÉRAUX ======= */
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

        /* ======= SEPARATEURS ======= */
        hr, .stDivider {
            border-top: 2px solid var(--vert-mbb);
        }

        /* ======= CHAMPS DE FORMULAIRE ======= */
        input, textarea {
            border-radius: 8px !important;
            border: 1px solid #ccc !important;
            color: var(--texte-fonce) !important;
        }
    </style>
""", unsafe_allow_html=True)


# === ENTÊTE AVEC VISUEL ===
if os.path.exists(VISUEL):
    st.image(VISUEL, use_container_width=True)
else:
    st.info("🔰 Bienvenue dans la base de données MBB — visuel non chargé.")

st.title("📘 Base de données du Mouvement - MBB")
st.markdown(
    "<p style='font-size:18px;'>Bienvenue dans la base de données des membres de "
    "<b>Malika Bi Ñu Bëgg</b>.<br>"
    "<span style='color:#145A32; font-weight:bold;'>Une nouvelle ère s’annonce 🌍</span></p>",
    unsafe_allow_html=True
)

# === CHARGEMENT DU FICHIER EXCEL ===
if not os.path.exists(FICHIER_EXCEL):
    st.error(f"Le fichier {FICHIER_EXCEL} est introuvable.")
else:
    df = pd.read_excel(FICHIER_EXCEL, sheet_name="Liste des membres", header=1)

    st.markdown("<h2>👥 Liste actuelle des membres</h2>", unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True)

    st.divider()

    # === FORMULAIRE D'AJOUT ===
    st.markdown("<h2>➕ Ajouter un nouveau membre</h2>", unsafe_allow_html=True)

    code = st.text_input("Entrez le code d'accès :", type="password")

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
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    df.to_excel(FICHIER_EXCEL, index=False, sheet_name="Liste des membres")
                    st.success(f"✅ {prenom} {nom} ajouté avec succès !")
                else:
                    st.warning("⚠️ Merci de renseigner au minimum le prénom et le nom.")
    elif code:
        st.error("❌ Code d'accès incorrect.")

