import streamlit as st
import pandas as pd
import os

FICHIER_EXCEL = "Liste_Membres.xlsx"
CODE_SECRET = "MBB2025"  # à changer

st.set_page_config(page_title="Base de données MBB", layout="wide")

st.title("📘 Base de données du Mouvement - MBB")
st.markdown("Bienvenue dans la base de données des membres de **Malika Bi Ñu Bëgg**.")

# Vérifier que le fichier existe
if not os.path.exists(FICHIER_EXCEL):
    st.error(f"Le fichier {FICHIER_EXCEL} est introuvable.")
else:
    # Charger les membres existants (ligne 0 comme en-tête)
    df = pd.read_excel(FICHIER_EXCEL, sheet_name="Liste des membres", header=1)

    st.subheader("👥 Liste actuelle des membres")
    st.dataframe(df, use_container_width=True)

    st.divider()

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
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    df.to_excel(FICHIER_EXCEL, index=False, sheet_name="Liste des membres")
                    st.success(f"✅ {prenom} {nom} ajouté avec succès !")
                else:
                    st.warning("⚠️ Merci de renseigner au minimum le prénom et le nom.")
    elif code:
        st.error("❌ Code d'accès incorrect.")

