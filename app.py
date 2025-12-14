import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
import folium
from streamlit_folium import st_folium
from urllib.parse import urlencode
import requests

# ============================================================
# ✅ CONFIGURATION
# ============================================================

# 1) Google Form (PAS Google Sheet)
# Mets ici le lien "viewform" de TON Google Form, ex:
# https://docs.google.com/forms/d/e/XXXXXXXXXXXX/viewform
FORM_BASE_URL = "https://docs.google.com/forms/d/e/XXXXXXXXXXXX/viewform"

# 2) IDs des champs (tes entry.xxxxx)
ENTRY_PRENOM = "entry.1181294215"
ENTRY_NOM = "entry.2048123513"
ENTRY_TEL = "entry.915975688"
ENTRY_ADRESSE = "entry.1503668516"
ENTRY_CNI = "entry.732417991"

# Excel local optionnel (si tu veux aussi garder une copie locale)
FICHIER_EXCEL = "Liste_Membres.xlsx"
VISUEL = "561812309_122099008227068424_7173387226638749981_n.jpg"

# Identifiants de connexion admin
USERS = {
    "admin": "mbb2025",
    "president": "malika2025",
}

# ============================================================
# 🎛️ PAGE
# ============================================================

st.set_page_config(page_title="Base de données MBB", page_icon="📘", layout="wide")

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
        font-weight:bold; font-size:20px; margin-bottom:15px; box-shadow:2px 2px 10px rgba(0,0,0,0.3);
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
    @media (max-width:768px){ .stApp{ font-size:15px !important; } }
    [data-testid="stDataFrame"] table tbody tr:hover { background:#FCF3CF !important; color:#000 !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 🔐 SESSION
# ============================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None

# Sidebar déconnexion
if st.session_state.authenticated and st.session_state.username:
    st.sidebar.success(f"Connecté en tant que **{st.session_state.username}**")
    if st.sidebar.button("🔒 Déconnexion"):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()

# ============================================================
# 🖼️ VISUEL
# ============================================================

if os.path.exists(VISUEL):
    st.image(VISUEL, use_container_width=True)

# ============================================================
# ✅ FONCTIONS
# ============================================================

def post_to_google_form(prenom: str, nom: str, tel: str, adresse: str, cni: str) -> bool:
    """
    Envoie une réponse au Google Form via POST "formResponse".
    Aucun secret. Aucune clé.
    """
    if "docs.google.com/forms" not in FORM_BASE_URL:
        st.error("⚠️ FORM_BASE_URL n’est pas configuré. Mets le lien viewform de ton Google Form.")
        return False

    form_response_url = FORM_BASE_URL.replace("/viewform", "/formResponse")

    payload = {
        ENTRY_PRENOM: prenom,
        ENTRY_NOM: nom,
        ENTRY_TEL: tel,
        ENTRY_ADRESSE: adresse,
        ENTRY_CNI: cni,
    }

    # Google Forms accepte souvent un POST sans authentification.
    # On met un user-agent pour éviter certains blocages.
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.post(form_response_url, data=payload, headers=headers, timeout=15)
        # Google Forms renvoie souvent 200 ou 302. On accepte les deux.
        return r.status_code in (200, 302)
    except Exception:
        return False


def safe_normalize_columns(cols):
    """Normalise colonnes sans planter si certaines ne sont pas des strings."""
    cols = ["" if c is None else str(c) for c in cols]
    s = pd.Index(cols)
    s = (s.str.strip().str.lower()
         .str.replace("é", "e").str.replace("è", "e").str.replace("ê", "e")
         .str.replace("à", "a").str.replace("ç", "c"))
    return s


def load_local_excel():
    """Charge l'excel local (optionnel). Si absent, renvoie df vide."""
    if not os.path.exists(FICHIER_EXCEL):
        return pd.DataFrame()

    try:
        df0 = pd.read_excel(FICHIER_EXCEL, sheet_name="Liste des membres", header=1)
    except Exception:
        # Si la feuille n'existe pas / header diff
        df0 = pd.read_excel(FICHIER_EXCEL)

    df0.columns = safe_normalize_columns(df0.columns)
    df0 = df0.loc[:, ~df0.columns.duplicated()]
    return df0


def append_local_excel(prenom, nom, tel, adresse, cni):
    """Optionnel: garde aussi une copie locale dans l'Excel, si présent."""
    if not os.path.exists(FICHIER_EXCEL):
        return

    try:
        df_to_write = pd.read_excel(FICHIER_EXCEL, sheet_name="Liste des membres", header=1)
    except Exception:
        df_to_write = pd.read_excel(FICHIER_EXCEL)

    new_row = {
        "Prénom": prenom,
        "Nom": nom,
        "Adresse": adresse,
        "Téléphone": tel,
        "CNI": cni
    }
    df_to_write = pd.concat([df_to_write, pd.DataFrame([new_row])], ignore_index=True)

    with pd.ExcelWriter(FICHIER_EXCEL, engine="openpyxl") as writer:
        df_to_write.to_excel(writer, index=False, sheet_name="Liste des membres")


# ============================================================
# 🧭 NAVIGATION
# ============================================================

df = load_local_excel()

col_adresse = [c for c in df.columns if "adres" in c]
nb_quartiers = len(df[col_adresse[0]].dropna().unique()) if (len(df) and col_adresse) else 0

tabs = st.tabs([
    "🏠 Accueil",
    f"🏘️ Par Quartier ({nb_quartiers})",
    "🗳️ Carte électorale de Malika",
    "📝 Compte Rendu",
    "🚫 Membres Non Inscrits"
])

# ============================================================
# 🏠 ONGLET ACCUEIL
# ============================================================

with tabs[0]:
    st.markdown("<div class='banner'>MALIKA BI ÑU BËGG – Une nouvelle ère s’annonce 🌍</div>", unsafe_allow_html=True)
    st.title("📘 Base de données du Mouvement - MBB")

    date_du_jour = datetime.now().strftime("%d %B %Y")
    st.subheader(f"👥 Liste actuelle des membres à la date du {date_du_jour}")

    if st.session_state.authenticated:
        if len(df):
            st.dataframe(df, use_container_width=True)
        else:
            st.info("ℹ️ Aucune donnée locale à afficher (Excel). Les inscriptions partent vers Google Form.")
    else:
        st.info("🔐 La liste détaillée des membres est réservée aux administrateurs.")

    st.divider()
    st.subheader("Espace membres")

    col_form, col_login = st.columns(2)

    # ✅ FORMULAIRE DIRECTEMENT SUR LA PAGE
    with col_form:
        st.markdown("#### 📝 Inscription comme membre")

        with st.form("form_inscription_public"):
            prenom_new = st.text_input("Prénom")
            nom_new = st.text_input("Nom")
            tel_new = st.text_input("Numéro de téléphone")
            quartier_new = st.text_input("Quartier (Adresse)")
            cni_new = st.text_input("Numéro de CNI (optionnel)")

            submitted_inscription = st.form_submit_button("Valider mon inscription")

            if submitted_inscription:
                if not (prenom_new and nom_new and tel_new and quartier_new):
                    st.warning("⚠️ Merci de renseigner au minimum Prénom, Nom, Téléphone et Quartier.")
                else:
                    ok = post_to_google_form(
                        prenom=prenom_new.strip(),
                        nom=nom_new.strip(),
                        tel=tel_new.strip(),
                        adresse=quartier_new.strip(),
                        cni=cni_new.strip()
                    )

                    if ok:
                        # Optionnel: copie locale
                        append_local_excel(prenom_new, nom_new, tel_new, quartier_new, cni_new)

                        st.success("✅ Inscription réussie ! Vous êtes membre de BD2027 MBB.")
                        st.markdown("### 🌐 Rejoignez nos réseaux sociaux")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.markdown("[🌍 Facebook](https://facebook.com)")
                        with col2:
                            st.markdown("[📸 Instagram](https://instagram.com)")
                        with col3:
                            st.markdown("[💬 WhatsApp](https://wa.me/221770000000)")
                    else:
                        st.error("❌ Envoi impossible. Vérifie le lien du Google Form (FORM_BASE_URL) et réessaie.")

    # 🔐 CONNEXION ADMIN
    with col_login:
        st.markdown("#### 🔐 Connexion administrateur")

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
            st.success(f"✅ Connecté en tant que **{st.session_state.username}**")

# ============================================================
# 🏘️ ONGLET PAR QUARTIER (ADMIN)
# ============================================================

with tabs[1]:
    if not st.session_state.authenticated:
        st.warning("🔐 Cette section est réservée aux administrateurs.")
    else:
        st.markdown("### 🏘️ Membres regroupés par adresse (quartier)")

        if not len(df):
            st.info("ℹ️ Pas de données Excel locales. Les inscriptions partent vers Google Form.")
        elif not col_adresse:
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

# ============================================================
# 🗳️ ONGLET CARTE ÉLECTORALE (ADMIN)
# ============================================================

with tabs[2]:
    if not st.session_state.authenticated:
        st.warning("🔐 Cette section est réservée aux administrateurs.")
    else:
        st.markdown("### 🗳️ Carte électorale – Commune de Malika")
        st.info("Source : portail officiel antifraude.parti-pur.com (lien indicatif).")

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
            data_centres, x="Centre de vote", y="Nombre de bureaux",
            color="Centre de vote", text="Nombre de bureaux",
            title="Nombre de bureaux de vote par centre – Commune de Malika"
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
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

# ============================================================
# 📝 ONGLET COMPTE RENDU (ADMIN)
# ============================================================

with tabs[3]:
    if not st.session_state.authenticated:
        st.warning("🔐 Cette section est réservée aux administrateurs.")
    else:
        st.markdown("### 📝 Compte Rendu des Réunions")
        st.info("Cette section affichera prochainement les comptes rendus officiels des réunions du mouvement MBB.")

# ============================================================
# 🚫 ONGLET MEMBRES NON INSCRITS (ADMIN)
# ============================================================

with tabs[4]:
    if not st.session_state.authenticated:
        st.warning("🔐 Cette section est réservée aux administrateurs.")
    else:
        st.markdown("### 🚫 Membres Non Inscrits")
        st.info("Aucune donnée à afficher pour le moment.")

