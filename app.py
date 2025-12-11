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
USERS = {
    "admin": "mbb2025",
    "president": "malika2025"
}

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

        [data-testid="stDataFrame"] table tbody tr:hover {
            background:#FCF3CF !important; color:#000 !important;
        }
    </style>
""", unsafe_allow_html=True)

# === SESSION ===
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None

# === BARRE LATÉRALE SI CONNECTÉ ===
if st.session_state.authenticated and st.session_state.username:
    st.sidebar.success(f"Connecté en tant que **{st.session_state.username}**")
    if st.sidebar.button("🔒 Déconnexion"):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()

# === VISUEL ===
if os.path.exists(VISUEL):
    st.image(VISUEL, use_container_width=True)

# === CHARGEMENT EXCEL ===
if not os.path.exists(FICHIER_EXCEL):
    st.error(f"❌ Le fichier {FICHIER_EXCEL} est introuvable.")
    st.stop()

# On lit le fichier d’origine avec les bons en-têtes
df = pd.read_excel(FICHIER_EXCEL, sheet_name="Liste des membres", header=1)
df.columns = df.columns.str.strip()

# Détection robuste de la colonne adresse (ADRESSE, Adresse, adresse…)
col_adresse = [c for c in df.columns if "adresse" in c.lower()]
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
    st.subheader(f"👥 Liste actuelle des membres au {date_du_jour}")

    if st.session_state.authenticated:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("🔐 La liste détaillée des membres est visible uniquement par les administrateurs.")

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
                    st.warning("⚠️ Prénom, Nom, Téléphone et Quartier sont obligatoires.")
                else:
                    # Recharge le fichier brut pour ne pas perdre la structure originale
                    df_write = pd.read_excel(FICHIER_EXCEL, sheet_name="Liste des membres", header=1)

                    # IMPORTANT : utiliser exactement les noms de colonnes de ton Excel
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

                    st.success("✅ Inscription réussie ! Vous êtes membre de BD2027 MBB.")

                    st.markdown("### 🌐 Rejoignez nos réseaux sociaux")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown("[🌍 Facebook](https://facebook.com)")
                    with col2:
                        st.markdown("[📸 Instagram](https://instagram.com)")
                    with col3:
                        st.markdown("[💬 WhatsApp](https://wa.me/221770000000)")

    # === CONNEXION ADMIN ===
    with col_login:
        st.markdown("### 🔐 Connexion administrateur")

        if not st.session_state.authenticated:
            username_input = st.text_input("👤 Identifiant", key="login_user")
            password_input = st.text_input("🔑 Mot de passe", type="password", key="login_pwd")

            if st.button("Se connecter", key="btn_login"):
                if username_input in USERS and USERS[username_input] == password_input:
                    st.session_state.authenticated = True
                    st.session_state.username = username_input
                    st.success("✅ Connexion réussie !")
                    st.rerun()
                else:
                    st.error("❌ Identifiant ou mot de passe incorrect.")
        else:
            st.success(f"Connecté en tant que **{st.session_state.username}**")

# ===========================
# 🏘️ ONGLET PAR QUARTIER
# ===========================
with tabs[1]:
    if not st.session_state.authenticated:
        st.warning("🔐 Cette section est réservée aux administrateurs.")
    else:
        st.markdown("### 🏘️ Membres regroupés par adresse (quartier)")

        if not col_adresse:
            st.error("❌ Colonne 'Adresse' introuvable dans le fichier.")
        else:
            adresse_col = col_adresse[0]

            counts = df[adresse_col].value_counts(dropna=True).reset_index()
            counts.columns = ["Quartier", "Nombre de membres"]

            st.markdown("#### 📊 Répartition des membres par quartier")
            figq = px.bar(
                counts, x="Quartier", y="Nombre de membres", color="Quartier",
                text="Nombre de membres", title="Nombre de membres par quartier"
            )
            figq.update_traces(textposition="outside", cliponaxis=False)
            figq.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white", size=14), title_font=dict(size=18), xaxis_tickangle=-30
            )
            st.plotly_chart(figq, use_container_width=True)

            st.divider()
            quartiers_uniques = df[adresse_col].dropna().unique()
            total_membres = 0
            for quartier in sorted(quartiers_uniques):
                df_q = df[df[adresse_col] == quartier]
                nb = len(df_q)
                total_membres += nb
                st.markdown(f"#### 📍 {quartier} ({nb} membre{'s' if nb>1 else ''})")
                st.dataframe(df_q, use_container_width=True)
                st.divider()
            st.markdown(f"### 🔢 Total général : **{total_membres} membres**")

# ===========================
# 🗳️ ONGLET CARTE ÉLECTORALE
# ===========================
with tabs[2]:
    if not st.session_state.authenticated:
        st.warning("🔐 Cette section est réservée aux administrateurs.")
    else:
        st.markdown("### 🗳️ Carte électorale – Commune de Malika")
        st.info("Source : portail officiel [antifraude.parti-pur.com](https://antifraude.parti-pur.com/commune/SENEGAL-DAKAR-KEUR-MASSAR-MALIKA/carte-eletorale)")

        data_centres = pd.DataFrame({
            "Centre de vote": [
                "École Malika Montagne",
                "École Privée Sanka",
                "École Seydi Anta Gadiaga"
            ],
            "Nombre de bureaux": [14, 20, 18],
            "Latitude": [14.7889, 14.7858, 14.7915],
            "Longitude": [-17.3085, -17.3120, -17.3048]
        })

        st.markdown("#### 📊 Répartition des bureaux de vote par centre")
        fig = px.bar(
            data_centres, x="Centre de vote", y="Nombre de bureaux", color="Centre de vote",
            text="Nombre de bureaux",
            color_discrete_sequence=["#145A32", "#2ECC71", "#F4D03F"],
            title="Nombre de bureaux de vote par centre – Commune de Malika"
        )
        fig.update_traces(textposition="outside", textfont=dict(color="white", size=16), cliponaxis=False)
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white", size=14), title_font=dict(size=18)
        )
        st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.markdown("#### 🗺️ Localisation des centres de vote sur la carte")
        m = folium.Map(location=[14.7889, -17.3090], zoom_start=15, tiles="CartoDB positron")
        for _, row in data_centres.iterrows():
            folium.Marker(
                location=[row["Latitude"], row["Longitude"]],
                popup=f"<b>{row['Centre de vote']}</b><br>Bureaux de vote : {row['Nombre de bureaux']}",
                tooltip=row["Centre de vote"],
                icon=folium.Icon(color="green", icon="info-sign")
            ).add_to(m)
        st_folium(m, width=800, height=500)

# ===========================
# 📝 ONGLET COMPTE RENDU
# ===========================
with tabs[3]:
    if not st.session_state.authenticated:
        st.warning("🔐 Cette section est réservée aux administrateurs.")
    else:
        st.markdown("### 📝 Compte Rendu des Réunions")
        st.info("Cette section affichera prochainement les comptes rendus officiels des réunions du mouvement MBB.")

# ===========================
# 🚫 ONGLET MEMBRES NON INSCRITS
# ===========================
with tabs[4]:
    if not st.session_state.authenticated:
        st.warning("🔐 Cette section est réservée aux administrateurs.")
    else:
        st.markdown("### 🚫 Membres Non Inscrits")
        st.info("Aucune donnée à afficher pour le moment.")
