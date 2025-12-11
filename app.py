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

# === IDENTIFIANTS ADMIN UNIQUES ===
ADMIN_USER = "admin"
ADMIN_PASS = "mbb2025"

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
            box-shadow:1px 1px 4px rgba(0,0,0,0.3);
        }

        .stButton>button:hover {
            background: linear-gradient(45deg, var(--jaune-mbb), var(--vert-fonce)); color:black;
        }

        header[data-testid="stHeader"], #MainMenu, footer { display:none !important; }
    </style>
""", unsafe_allow_html=True)

# === SESSION D’AUTHENTIFICATION ADMIN ===
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# === ACCUEIL : VISUEL + BOUTONS ===
st.markdown("<div class='banner'>MALIKA BI ÑU BËGG – Une nouvelle ère s’annonce 🌍</div>", unsafe_allow_html=True)
st.title("📘 Base de données du Mouvement - MBB")

if os.path.exists(VISUEL):
    st.image(VISUEL, use_container_width=True)

colA, colB = st.columns(2)
with colA:
    bouton_inscription = st.button("📝 S'inscrire comme membre")
with colB:
    bouton_admin = st.button("🔐 Connexion Administrateur")


# ======================================
# 📝 FORMULAIRE PUBLIC D’INSCRIPTION
# ======================================
if bouton_inscription:
    st.markdown("## 📝 Formulaire d'inscription")

    with st.form("form_inscription"):
        prenom = st.text_input("Prénom")
        nom = st.text_input("Nom")
        telephone = st.text_input("Numéro de téléphone")
        quartier = st.text_input("Quartier (Adresse)")

        valider = st.form_submit_button("Soumettre")

        if valider:
            if not (prenom and nom and telephone and quartier):
                st.warning("⚠️ Tous les champs doivent être remplis.")
            else:
                # Charger Excel
                df_existing = pd.read_excel(FICHIER_EXCEL, sheet_name="Liste des membres", header=1)

                nouvelle_ligne = {
                    "Prénom": prenom,
                    "Nom": nom,
                    "Téléphone": telephone,
                    "Adresse": quartier
                }

                df_existing = pd.concat([df_existing, pd.DataFrame([nouvelle_ligne])], ignore_index=True)

                with pd.ExcelWriter(FICHIER_EXCEL, engine="openpyxl") as writer:
                    df_existing.to_excel(writer, index=False, sheet_name="Liste des membres")

                st.success("🎉 Inscription réussie ! Vous êtes désormais membre de BD2027 – MBB.")

                st.markdown("### 🌐 Rejoignez nos réseaux sociaux")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown("[🌍 Facebook](https://facebook.com)")
                with col2:
                    st.markdown("[📸 Instagram](https://instagram.com)")
                with col3:
                    st.markdown("[💬 WhatsApp](https://wa.me/221770000000)")


# ======================================
# 🔐 FORMULAIRE DE CONNEXION ADMIN
# ======================================
if bouton_admin and not st.session_state.authenticated:
    st.markdown("## 🔐 Espace Administrateur")

    username = st.text_input("Identifiant administrateur")
    pwd = st.text_input("Mot de passe", type="password")

    if st.button("Connexion"):
        if username == ADMIN_USER and pwd == ADMIN_PASS:
            st.session_state.authenticated = True
            st.success("Connexion réussie ✔️")
            st.rerun()
        else:
            st.error("❌ Identifiants incorrects")


# ======================================
# 🛡️ CONTENU RÉSERVÉ UNIQUEMENT À L'ADMIN
# ======================================
if st.session_state.authenticated:

    # Barre latérale admin
    st.sidebar.title("🔐 Espace Administrateur")
    st.sidebar.success("Connecté en tant qu'administrateur")

    if st.sidebar.button("Déconnexion"):
        st.session_state.authenticated = False
        st.rerun()

    # === CHARGEMENT DES DONNÉES ===
    df = pd.read_excel(FICHIER_EXCEL, sheet_name="Liste des membres", header=1)
    df.columns = df.columns.str.strip()

    # Onglets Admin
    tabs = st.tabs([
        "👥 Liste complète",
        "🏘️ Par Quartier",
        "🗳️ Carte électorale",
        "📝 Compte Rendu"
    ])

    # ===== LISTE COMPLÈTE =====
    with tabs[0]:
        st.markdown("## 👥 Liste des membres")
        st.dataframe(df, use_container_width=True)

    # ===== PAR QUARTIER =====
    with tabs[1]:
        if "Adresse" not in df.columns:
            st.error("Colonne Adresse manquante.")
        else:
            quartiers = df["Adresse"].value_counts().reset_index()
            quartiers.columns = ["Quartier", "Nombre"]

            st.markdown("### Répartition par quartier")
            figq = px.bar(quartiers, x="Quartier", y="Nombre", text="Nombre")
            st.plotly_chart(figq)

            for q in quartiers["Quartier"]:
                st.markdown(f"#### 📍 {q}")
                st.dataframe(df[df["Adresse"] == q])

    # ===== CARTE ÉLECTORALE =====
    with tabs[2]:
        st.write("Carte électorale ici… (inchangée)")

    # ===== COMPTE RENDU =====
    with tabs[3]:
        st.info("Section réservée aux rapports internes.")
