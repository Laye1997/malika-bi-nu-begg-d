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

# === IDENTIFIANTS DE CONNEXION ===
USERS = {"admin": "mbb2025", "president": "malika2025"}

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
            font-weight:bold; font-size:20px; margin-bottom:15px;
            box-shadow:2px 2px 10px rgba(0,0,0,0.3);
        }

        .stButton>button {
            background: linear-gradient(45deg, var(--vert-fonce), var(--jaune-mbb));
            color:white; border-radius:10px; font-weight:bold; border:none; width:100%;
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

# === VISUEL ===
if os.path.exists(VISUEL):
    st.image(VISUEL, use_container_width=True)

# === CHARGEMENT EXCEL ===
if not os.path.exists(FICHIER_EXCEL):
    st.error(f"❌ Fichier {FICHIER_EXCEL} introuvable.")
    st.stop()

df = pd.read_excel(FICHIER_EXCEL, sheet_name="Liste des membres", header=1)

# --- NORMALISATION COLONNES ---
df.columns = df.columns.str.strip()
col_adresse = [c for c in df.columns if "Adresse" in c or "adresse" in c]
nb_quartiers = len(df[col_adresse[0]].dropna().unique()) if col_adresse else 0

# === ONGLET NAVIGATION ===
tabs = st.tabs([
    "🏠 Accueil",
    f"🏘️ Par Quartier ({nb_quartiers})",
    "🗳️ Carte électorale de Malika",
    "📝 Compte Rendu",
    "🚫 Membres Non Inscrits"
])

# ===========================
# 🏠 ONGLET ACCUEIL
# ===========================
with tabs[0]:

    st.markdown("<div class='banner'>MALIKA BI ÑU BËGG – Une nouvelle ère s’annonce 🌍</div>", unsafe_allow_html=True)
    st.title("📘 Base de données du Mouvement - MBB")

    date_du_jour = datetime.now().strftime("%d %B %Y")
    st.subheader(f"👥 Nombre actuel de membres au {date_du_jour}")

    if st.session_state.authenticated:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("🔐 La liste des membres est réservée aux administrateurs.")

    st.divider()

    st.subheader("Espace membres")

    col_inscription, col_login = st.columns(2)

    # === FORMULAIRE PUBLIC D’INSCRIPTION ===
    with col_inscription:
        st.markdown("### 📝 Inscription comme membre")
        with st.form("form_inscription_public"):
            prenom_new = st.text_input("Prénom")
            nom_new = st.text_input("Nom")
            tel_new = st.text_input("Numéro de téléphone")
            quartier_new = st.text_input("Quartier (Adresse)")
            cni_new = st.text_input("Numéro de CNI (optionnel)")

            submitted = st.form_submit_button("Valider mon inscription")

            if submitted:
                if not (prenom_new and nom_new and tel_new and quartier_new):
                    st.warning("⚠️ Tous les champs obligatoires doivent être remplis.")
                else:
                    df_write = pd.read_excel(FICHIER_EXCEL, sheet_name="Liste des membres", header=1)

                    # 🚨 IMPORTANT : Les noms de colonnes doivent correspondre EXACTEMENT au fichier Excel
                    new_row = {
                        "Prenom": prenom_new,
                        "Nom": nom_new,
                        "Numéro de téléphone": tel_new,
                        "Adresse": quartier_new,
                        "CNI": cni_new
                    }

                    df_write = pd.concat([df_write, pd.DataFrame([new_row])], ignore_index=True)

                    with pd.ExcelWriter(FICHIER_EXCEL, engine="openpyxl") as writer:
                        df_write.to_excel(writer, index=False, sheet_name="Liste des membres")

                    st.success("🎉 Inscription réussie ! Vous êtes maintenant membre de BD2027 – MBB.")

                    st.markdown("### 🌐 Rejoignez nos réseaux sociaux")
                    col1, col2, col3 = st.columns(3)
                    col1.markdown("[🌍 Facebook](https://facebook.com)")
                    col2.markdown("[📸 Instagram](https://instagram.com)")
                    col3.markdown("[💬 WhatsApp](https://wa.me/221770000000)")

    # === CONNEXION ADMIN ===
    with col_login:
        st.markdown("### 🔐 Connexion administrateur")

        if not st.session_state.authenticated:
            user = st.text_input("Identifiant")
            pwd = st.text_input("Mot de passe", type="password")

            if st.button("Se connecter"):
                if user in USERS and USERS[user] == pwd:
                    st.session_state.authenticated = True
                    st.session_state.username = user
                    st.success("Connexion réussie ✔️")
                    st.rerun()
                else:
                    st.error("❌ Identifiants incorrects")
        else:
            st.success(f"Connecté en tant que **{st.session_state.username}**")
            if st.button("Déconnexion"):
                st.session_state.authenticated = False
                st.rerun()

# ===========================
# 🏘️ ONGLET PAR QUARTIER
# ===========================
with tabs[1]:
    if not st.session_state.authenticated:
        st.warning("🔐 Section réservée aux administrateurs.")
    else:
        st.markdown("### 🏘️ Membres par quartier")

        adresse_col = col_adresse[0]
        counts = df[adresse_col].value_counts().reset_index()
        counts.columns = ["Quartier", "Nombre"]

        fig = px.bar(counts, x="Quartier", y="Nombre", text="Nombre")
        st.plotly_chart(fig)

        for q in sorted(df[adresse_col].dropna().unique()):
            st.markdown(f"#### 📍 {q}")
            st.dataframe(df[df[adresse_col] == q])

# ===========================
# 🗳️ ONGLET CARTE ÉLECTORALE
# ===========================
with tabs[2]:
    if not st.session_state.authenticated:
        st.warning("🔐 Section réservée aux administrateurs.")
    else:
        st.info("Carte électorale…")

# ===========================
# 📝 ONGLET COMPTE RENDU
# ===========================
with tabs[3]:
    if not st.session_state.authenticated:
        st.warning("🔐 Section réservée aux administrateurs.")
    else:
        st.info("Compte rendu…")

# ===========================
# 🚫 ONGLET MEMBRES NON INSCRITS
# ===========================
with tabs[4]:
    if not st.session_state.authenticated:
        st.warning("🔐 Section réservée aux administrateurs.")
    else:
        st.info("Aucune donnée pour le moment.")
