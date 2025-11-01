import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

# === CONFIGURATION ===
FICHIER_EXCEL = "Liste_Membres.xlsx"
CODE_SECRET = "MBB2025"
VISUEL = "561812309_122099008227068424_7173387226638749981_n.jpg"

# === IDENTIFIANTS ===
USERNAME = "admin"
PASSWORD = "mbb2025"

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
        h1, h2, h3 { color: #FFFFFF !important; }
        .banner {
            background: linear-gradient(90deg, var(--vert-fonce), var(--jaune-mbb));
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

# === PAGE DE CONNEXION ===
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<div class='banner'>🔐 Connexion sécurisée - MBB</div>", unsafe_allow_html=True)
    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        if username == USERNAME and password == PASSWORD:
            st.session_state.authenticated = True
            st.success("Connexion réussie ✅")
            st.rerun()
        else:
            st.error("Nom d'utilisateur ou mot de passe incorrect ❌")
    st.stop()

# === SI CONNECTÉ ===
st.sidebar.success(f"Connecté en tant que **{USERNAME}**")

# === VISUEL ===
if os.path.exists(VISUEL):
    st.image(VISUEL, use_container_width=True)
else:
    st.warning("⚠️ Image du visuel non trouvée.")

# === CHARGEMENT DES DONNÉES ===
if not os.path.exists(FICHIER_EXCEL):
    st.error(f"Le fichier {FICHIER_EXCEL} est introuvable.")
    st.stop()

df = pd.read_excel(FICHIER_EXCEL, sheet_name="Liste des membres", header=1)
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
col_adresse = [c for c in df.columns if "adres" in c]
nb_quartiers = len(df[col_adresse[0]].dropna().unique()) if col_adresse else 0

# === ONGLET DE NAVIGATION ===
tabs = st.tabs([
    "🏠 Accueil",
    f"🏘️ Par Quartier ({nb_quartiers})",
    "🗳️ Carte électorale de Malika",
    "📝 Compte Rendu",
    "🚫 Membres Non Inscrits"
])

# === ONGLET ACCUEIL ===
with tabs[0]:
    st.markdown("<div class='banner'>MALIKA BI ÑU BËGG – Une nouvelle ère s’annonce 🌍</div>", unsafe_allow_html=True)
    st.title("📘 Base de données du Mouvement - MBB")
    st.markdown("<p>Bienvenue dans la base de données des membres de <b>Malika Bi Ñu Bëgg</b>.</p>", unsafe_allow_html=True)

    date_du_jour = datetime.now().strftime("%d %B %Y")
    st.subheader(f"👥 Liste actuelle des membres à la date du {date_du_jour}")
    st.dataframe(df, use_container_width=True)

    st.divider()
    st.subheader("📊 Répartition des membres par quartier")
    if col_adresse:
        membres_par_quartier = df[col_adresse[0]].value_counts().reset_index()
        membres_par_quartier.columns = ["Quartier", "Nombre de membres"]
        fig = px.bar(membres_par_quartier, x="Quartier", y="Nombre de membres",
                     color="Quartier", title="Répartition des membres par quartier")
        st.plotly_chart(fig, use_container_width=True)

# === ONGLET PAR QUARTIER ===
with tabs[1]:
    st.markdown("### 🏘️ Membres regroupés par adresse (quartier)")
    adresse_col = col_adresse[0]
    quartiers_uniques = df[adresse_col].dropna().unique()
    total_membres = 0

    for quartier in sorted(quartiers_uniques):
        membres_quartier = df[df[adresse_col] == quartier]
        nb_membres = len(membres_quartier)
        total_membres += nb_membres
        st.markdown(f"#### 📍 {quartier} ({nb_membres} membre{'s' if nb_membres > 1 else ''})")
        st.dataframe(membres_quartier, use_container_width=True)
        st.divider()
    st.markdown(f"### 🔢 Total général : **{total_membres} membres**")

# === ONGLET CARTE ÉLECTORALE ===
with tabs[2]:
    st.markdown("### 🗳️ Carte électorale – Commune de Malika")
    st.info("Ces informations proviennent du portail officiel : [antifraude.parti-pur.com](https://antifraude.parti-pur.com/commune/SENEGAL-DAKAR-KEUR-MASSAR-MALIKA/carte-eletorale)")

    # --- Tableau général des centres ---
    data_commune = {
        "Commune": ["Malika", "Malika", "Malika"],
        "Centre de vote": [
            "École Malika Montagne",
            "École Privée Sanka",
            "École Seydi Anta Gadiaga"
        ]
    }
    st.dataframe(pd.DataFrame(data_commune), use_container_width=True)

    st.divider()

    # --- École Malika Montagne ---
    st.markdown("#### 🏫 École Malika Montagne")
    st.markdown("**Bureaux de vote :** 14")
    st.write(", ".join([f"Bureau n°{i}" for i in range(1, 15)]))

    # --- École Privée Sanka ---
    st.divider()
    st.markdown("#### 🏫 École Privée Sanka")
    st.markdown("**Bureaux de vote :** 20")
    st.write(", ".join([f"Bureau n°{i}" for i in range(1, 21)]))

    # --- École Seydi Anta Gadiaga ---
    st.divider()
    st.markdown("#### 🏫 École Seydi Anta Gadiaga")
    st.markdown("**Bureaux de vote :** 18")
    st.write(", ".join([f"Bureau n°{i}" for i in range(1, 19)]))

    st.success("🗳️ Page d'information sur la carte électorale de la commune de Malika mise à jour.")

# === ONGLET COMPTE RENDU ===
with tabs[3]:
    st.markdown("### 📝 Compte Rendu des réunions")
    st.info("Cette page présentera prochainement les comptes rendus officiels des réunions du mouvement MBB.")

# === ONGLET MEMBRES NON INSCRITS ===
with tabs[4]:
    st.markdown("### 🚫 Membres non inscrits")
    st.warning("Aucune donnée pour le moment. Cette section affichera les membres non encore enregistrés.")
