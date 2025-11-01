import streamlit as st
import pandas as pd
import os

FICHIER_EXCEL = "Liste_Membres.xlsx"
CODE_SECRET = "MBB2025"  # à modifier si besoin
VISUEL = "561812309_122099008227068424_7173387226638749981_n.jpg"

# 🎨 Configuration du site
st.set_page_config(
    page_title="Base de données MBB",
    page_icon="📘",
    layout="wide",
)

# 🌈 Style CSS personnalisé
st.markdown("""
    <style>
        body {
            background-color: #FFFFFF;
        }
        .main {
            background-color: #FFFFFF;
        }
        h1, h2, h3 {
            color: #145A32;
        }
        .stApp {
            background-color: #FFFFFF;
        }
        div[data-testid="stHeader"] {
            background-color: #145A32 !important;
        }
        .stButton>button {
            background-color: #145A32;
            color: white;
            border-radius: 10px;
            font-weight: bold;
        }
        .stButton>button:hover {
            background-color: #F4D03F;
            color: black;
        }
        .stDataFrame {
            border: 2px solid #145A32;
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# 🖼️ En-tête avec le visuel
if os.path.exists(VISUEL):
    st.image(VISUEL, use_container_width=True)
else:
    st.warning("⚠️ Image du visuel non trouvée.")

st.title("📘 Base de données du Mouvement - MBB")
st.markdown(
    "<p style='font-size:18px;'>Bienvenue dans la base de données des membres de <b>Malika Bi Ñu Bëgg</b>.<br>"
    "Une nouvelle ère s’annonce 🌍</p>", unsafe_allow_html=True
)

# 📊 Affichage de la liste des membres
if not os.path.exists(FICHIER_EXCEL):
    st.error(f"Le fichier {FICHIER_EXCEL} est introuvable.")
else:
    df = pd.read_excel(FICHIER_EXCEL, sheet_name="Liste des membres", header=1)

    st.markdown("<h2>👥 Liste actuelle des membres</h2>", unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True)

    st.divider()

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
