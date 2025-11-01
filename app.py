import streamlit as st
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt

# === CONFIGURATION ===
FICHIER_EXCEL = "Liste_Membres.xlsx"
CODE_SECRET = "MBB2025"
VISUEL = "561812309_122099008227068424_7173387226638749981_n.jpg"

# === PARAMÈTRES DE LA PAGE ===
st.set_page_config(page_title="Base de données MBB", page_icon="📘", layout="wide")

# === STYLE PERSONNALISÉ ===
st.markdown("""
    <style>
        :root {
            --vert-fonce: #145A32;
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
            cursor: pointer;
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

        header[data-testid="stHeader"], #MainMenu, footer {
            display: none !important;
            visibility: hidden !important;
        }
    </style>
""", unsafe_allow_html=True)

# === VISUEL DU MOUVEMENT ===
if os.path.exists(VISUEL):
    st.image(VISUEL, use_container_width=True)
else:
    st.warning("⚠️ Image du visuel non trouvée.")

# === CHARGEMENT DU FICHIER ===
if not os.path.exists(FICHIER_EXCEL):
    st.error(f"❌ Le fichier {FICHIER_EXCEL} est introuvable.")
    st.stop()

df = pd.read_excel(FICHIER_EXCEL, sheet_name="Liste des membres", header=1)

# === NORMALISER LES NOMS DE COLONNES ===
df.columns = (
    df.columns.str.strip()
              .str.lower()
              .str.replace("é", "e")
              .str.replace("è", "e")
              .str.replace("ê", "e")
              .str.replace("à", "a")
              .str.replace("ç", "c")
)
df = df.loc[:, ~df.columns.duplicated()]  # supprime les colonnes en double

col_adresse = [c for c in df.columns if "adres" in c]
nb_quartiers = len(df[col_adresse[0]].dropna().unique()) if col_adresse else 0

# === ONGLET DE NAVIGATION ===
tabs = st.tabs(["🏠 Accueil", f"🏘️ Afficher par Quartier ({nb_quartiers})", "🚫 Membres Non Inscrits"])

# ------------------------- 🏠 ONGLET ACCUEIL -------------------------
with tabs[0]:
    st.markdown("<div class='banner'>MALIKA BI ÑU BËGG – Une nouvelle ère s’annonce 🌍</div>", unsafe_allow_html=True)
    st.title("📘 Base de données du Mouvement - MBB")
    st.markdown("<p>Bienvenue dans la base de données des membres de <b>Malika Bi Ñu Bëgg</b>.</p>", unsafe_allow_html=True)

    date_du_jour = datetime.now().strftime("%d %B %Y")
    st.subheader(f"👥 Liste actuelle des membres à la date du {date_du_jour}")
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
                if prenom and nom and telephone:
                    telephone_sans_espaces = str(telephone).replace(" ", "").strip()
                    col_tel = [c for c in df.columns if "tel" in c]
                    if col_tel:
                        numeros_existants = df[col_tel[0]].astype(str).str.replace(" ", "").str.strip()
                    else:
                        numeros_existants = pd.Series([])

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

# ------------------------- 🏘️ ONGLET AFFICHER PAR QUARTIER -------------------------
with tabs[1]:
    st.markdown("### 🏘️ Membres regroupés par adresse (quartier)")
    if not col_adresse:
        st.error("❌ La colonne 'Adresse' est introuvable dans le fichier Excel.")
    else:
        adresse_col = col_adresse[0]
        quartiers_uniques = df[adresse_col].dropna().unique()
        total_membres = 0

        # --- Calcul des membres par quartier pour le graphique ---
        membres_par_quartier = df[adresse_col].value_counts().sort_index()

        # --- Afficher le graphique ---
        st.markdown("#### 📊 Répartition des membres par quartier")
        fig, ax = plt.subplots()
        colors = plt.cm.YlGn([i / len(membres_par_quartier) for i in range(len(membres_par_quartier))])
        ax.pie(membres_par_quartier, labels=membres_par_quartier.index, autopct='%1.1f%%', startangle=90, colors=colors)
        ax.axis('equal')
        st.pyplot(fig)

        st.divider()

        # --- Tableau par quartier ---
        for quartier in sorted(quartiers_uniques):
            membres_quartier = df[df[adresse_col] == quartier]
            nb_membres = len(membres_quartier)
            total_membres += nb_membres

            st.markdown(f"#### 📍 {quartier} ({nb_membres} membre{'s' if nb_membres > 1 else ''})")
            colonnes_afficher = [c for c in df.columns if c not in ["notes"]]
            st.dataframe(membres_quartier[colonnes_afficher], use_container_width=True)
            st.divider()

        st.markdown(f"### 🔢 Total général : **{total_membres} membres**")

# ------------------------- 🚫 ONGLET MEMBRES NON INSCRITS -------------------------
with tabs[2]:
    st.markdown("### 🚫 Membres Non Inscrits")
    st.info("Aucune donnée à afficher pour le moment. Cette section sera développée ultérieurement.")
