import streamlit as st
import pandas as pd
import os
from datetime import datetime

# === CONFIGURATION ===
FICHIER_EXCEL = "Liste_Membres.xlsx"
CODE_SECRET = "MBB2025"
VISUEL = "561812309_122099008227068424_7173387226638749981_n.jpg"

st.set_page_config(page_title="Base de données MBB", page_icon="📘", layout="wide")

# === STYLE ===
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

        .stDataFrame {
            border: 2px solid var(--blanc);
            border-radius: 12px;
            background-color: rgba(255, 255, 255, 0.95);
            color: black !important;
        }

        [data-testid="stDataFrame"] table tbody tr:hover {
            background-color: #FCF3CF !important;
            color: #000000 !important;
        }

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
    </style>
""", unsafe_allow_html=True)

# === VISUEL ===
if os.path.exists(VISUEL):
    st.image(VISUEL, use_container_width=True)

st.markdown("<div class='banner'>MALIKA BI ÑU BËGG – Une nouvelle ère s’annonce 🌍</div>", unsafe_allow_html=True)
st.title("📘 Base de données du Mouvement - MBB")
st.markdown("Bienvenue dans la base de données des membres de **Malika Bi Ñu Bëgg**.")

# === CHARGEMENT DU FICHIER ===
if not os.path.exists(FICHIER_EXCEL):
    st.error(f"Le fichier {FICHIER_EXCEL} est introuvable.")
    st.stop()

df = pd.read_excel(FICHIER_EXCEL, sheet_name="Liste des membres", header=1)

# Normaliser les noms de colonnes
df.columns = (
    df.columns.str.strip()
    .str.lower()
    .str.replace("é", "e")
    .str.replace("è", "e")
    .str.replace("ê", "e")
    .str.replace("à", "a")
    .str.replace("ç", "c")
)
df = df.loc[:, ~df.columns.duplicated()]

# Identifier les colonnes
colonnes = {
    "prenom": [c for c in df.columns if "prenom" in c],
    "nom": [c for c in df.columns if "nom" in c],
    "adresse": [c for c in df.columns if "adres" in c or "quartier" in c],
    "telephone": [c for c in df.columns if "tel" in c],
    "profession": [c for c in df.columns if "prof" in c],
    "commission": [c for c in df.columns if "comm" in c],
}

# Si pas de colonne d’adresse, on la crée
if not colonnes["adresse"]:
    df["adresse (quartier)"] = ""
    adresse_col = "adresse (quartier)"
else:
    adresse_col = colonnes["adresse"][0]

# === AFFICHAGE DE LA DATE ===
date_du_jour = datetime.now().strftime("%d %B %Y")
st.subheader(f"👥 Liste actuelle des membres à la date du {date_du_jour}")

# === BOUTON D’AFFICHAGE PAR QUARTIER ===
afficher_par_quartier = st.button("🏘️ Afficher les membres par quartier")

if afficher_par_quartier:
    st.markdown("### 🏘️ Membres regroupés par adresse (quartier)")
    quartiers_uniques = sorted(df[adresse_col].dropna().unique())

    if len(quartiers_uniques) == 0:
        st.warning("⚠️ Aucune adresse n’est encore enregistrée.")
    else:
        for quartier in quartiers_uniques:
            membres_quartier = df[df[adresse_col] == quartier]
            nb_membres = len(membres_quartier)
            st.markdown(f"#### 📍 {quartier} — {nb_membres} membre(s)")
            st.dataframe(
                membres_quartier[
                    [c[0] for c in colonnes.values() if c and c[0] in df.columns]
                ],
                use_container_width=True,
            )
            st.divider()

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
            # Choix ou ajout de l’adresse
            quartiers = sorted(df[adresse_col].dropna().unique())
            nouvelle_adresse = st.text_input("➕ Nouvelle adresse (si absente)")
            adresse = st.selectbox("Adresse existante (quartier)", [""] + quartiers)

            if nouvelle_adresse:
                adresse = nouvelle_adresse.strip().upper()

            commission = st.text_input("Commission")
            notes = st.text_area("Notes")

        submitted = st.form_submit_button("Ajouter le membre")

        if submitted:
            if prenom and nom and telephone:
                telephone_sans_espaces = str(telephone).replace(" ", "").strip()
                col_tel = [c for c in df.columns if "tel" in c]
                numeros_existants = (
                    df[col_tel[0]].astype(str).str.replace(" ", "").str.strip()
                    if col_tel
                    else pd.Series([])
                )

                if telephone_sans_espaces in numeros_existants.values:
                    st.error("❌ Ce numéro de téléphone est déjà enregistré.")
                else:
                    new_row = {
                        "Prénom": prenom,
                        "Nom": nom,
                        "Adresse (quartier)": adresse,
                        "Téléphone": telephone,
                        "Profession": profession,
                        "Commission": commission,
                        "Notes": notes,
                    }
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    df.to_excel(FICHIER_EXCEL, index=False, sheet_name="Liste des membres")
                    st.success(f"✅ {prenom} {nom} ajouté avec succès à {adresse} !")
            else:
                st.warning("⚠️ Merci de renseigner le prénom, le nom et le numéro de téléphone.")
elif code:
    st.error("❌ Code d'accès incorrect.")
