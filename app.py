import streamlit as st
import pandas as pd
import os
from datetime import datetime

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
            --vert-fonce: #145A32;
            --vert-clair: #7DCEA0;
            --jaune-mbb: #F4D03F;
            --blanc: #FFFFFF;
        }

        .stApp {
            background: linear-gradient(120deg, var(--vert-fonce), var(--jaune-mbb));
            color: var(--blanc);
            font-family: "Segoe UI", sans-serif;
        }

        h1, h2, h3 {
            color: #FFFFFF !important;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.4);
        }

        p, label, span, div {
            color: #FDFEFE !important;
        }

        /* ======= TABLEAU ======= */
        .stDataFrame {
            border: 2px solid var(--blanc);
            border-radius: 12px;
            background-color: rgba(255, 255, 255, 0.95);
            color: black !important;
        }

        [data-testid="stDataFrame"] table {
            color: black !important;
            background-color: white !important;
        }

        [data-testid="stDataFrame"] table tbody tr:hover {
            background-color: #FCF3CF !important;
            color: #000000 !important;
            cursor: pointer;
        }

        /* ======= CHAMPS DE FORMULAIRE ======= */
        input, textarea {
            border-radius: 8px !important;
            border: 1px solid #ccc !important;
            color: #000000 !important;
            background-color: #FFFFFF !important;
        }

        /* ======= BOUTONS ======= */
        .stButton>button {
            background: linear-gradient(45deg, var(--vert-fonce), var(--jaune-mbb));
            color: white;
            border-radius: 10px;
            font-weight: bold;
            border: none;
            box-shadow: 1px 1px 4px rgba(0,0,0,0.3);
        }

        .stButton>button:hover {
            background: linear-gradient(45deg, var(--jaune-mbb), var(--vert-fonce));
            color: black;
        }

        /* ======= BANNIÈRE ======= */
        .banner {
            background: linear-gradient(90deg, var(--vert-fonce), var(--jaune-mbb));
            color: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            font-weight: bold;
            font-size: 22px;
            margin-bottom: 20px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
        }

        /* ======= ALIGNEMENT DU TITRE ET DU BOUTON ======= */
        .header-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# === VISUEL DU MOUVEMENT ===
if os.path.exists(VISUEL):
    st.image(VISUEL, use_container_width=True)
else:
    st.warning("⚠️ Image du visuel non trouvée.")

# === TITRE + BOUTON ALIGNÉS ===
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown("<div class='banner'>MALIKA BI ÑU BËGG – Une nouvelle ère s’annonce 🌍</div>", unsafe_allow_html=True)
    st.title("📘 Base de données du Mouvement - MBB")
    st.markdown("<p>Bienvenue dans la base de données des membres de <b>Malika Bi Ñu Bëgg</b>.</p>", unsafe_allow_html=True)
with col2:
    afficher_par_quartier = st.button("🏘️ Afficher par quartier")

# === CHARGEMENT DU FICHIER EXCEL ===
if not os.path.exists(FICHIER_EXCEL):
    st.error(f"Le fichier {FICHIER_EXCEL} est introuvable.")
else:
    df = pd.read_excel(FICHIER_EXCEL, sheet_name="Liste des membres", header=1)

    # === TITRE AVEC DATE ===
    date_du_jour = datetime.now().strftime("%d %B %Y")
    st.subheader(f"👥 Liste actuelle des membres à la date du {date_du_jour}")

    if afficher_par_quartier:
        st.markdown("### 🏘️ Membres regroupés par adresse (quartier)")
        quartiers_uniques = df["Adresse"].dropna().unique()
        for quartier in sorted(quartiers_uniques):
            st.markdown(f"#### 📍 {quartier}")
            membres_quartier = df[df["Adresse"] == quartier][["Prénom", "Nom", "Téléphone", "Profession", "Commission"]]
            st.dataframe(membres_quartier, use_container_width=True)
            st.divider()
    else:
        st.dataframe(df, use_container_width=True)

    st.divider()

    # === FORMULAIRE D’AJOUT ===
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
                if prenom and nom and telephone:
                    # === Contrôle des doublons sur le numéro de téléphone ===
                    telephone_sans_espaces = str(telephone).replace(" ", "").strip()
                    numeros_existants = df["Téléphone"].astype(str).str.replace(" ", "").str.strip()

                    if telephone_sans_espaces in numeros_existants.values:
                        st.error("❌ Ce numéro de téléphone est déjà enregistré dans la base de données.")
                    else:
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
                    st.warning("⚠️ Merci de renseigner le prénom, le nom et le numéro de téléphone.")
    elif code:
        st.error("❌ Code d'accès incorrect.")
