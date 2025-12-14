import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import os
import folium
from streamlit_folium import st_folium

# ============================================================
# ✅ CONFIG (SANS SECRETS)
# ============================================================

# 1) URL CSV (depuis "Publier sur le web" -> CSV)
CSV_URL = "COLLE_ICI_TON_LIEN_CSV_PUBLIE"

# 2) URL Google Form EMBED (viewform?embedded=true)
FORM_URL = "COLLE_ICI_TON_LIEN_GOOGLE_FORM_EMBED"

VISUEL = "561812309_122099008227068424_7173387226638749981_n.jpg"

USERS = {
    "admin": "mbb2025",
    "president": "malika2025"
}

st.set_page_config(page_title="Base de données MBB", page_icon="📘", layout="wide")

# ============================================================
# 🎨 STYLE
# ============================================================

st.markdown("""
<style>
:root { --vert:#145A32; --jaune:#F4D03F; --blanc:#FFFFFF; }
.stApp{
    background: linear-gradient(120deg, var(--vert), var(--jaune));
    color: var(--blanc);
    font-family: "Segoe UI", sans-serif;
}
h1,h2,h3,h4 { color:#FFFFFF !important; }
.banner{
    background: linear-gradient(90deg, var(--vert), var(--jaune));
    color:white;
    padding:14px;
    border-radius:12px;
    text-align:center;
    font-weight:bold;
    font-size:22px;
    margin-bottom:16px;
    box-shadow:2px 2px 12px rgba(0,0,0,0.35);
}
.stButton>button{
    background: linear-gradient(45deg, var(--vert), var(--jaune));
    color:white;
    border-radius:12px;
    font-weight:bold;
    border:none;
    width:100%;
}
.stButton>button:hover{
    background: linear-gradient(45deg, var(--jaune), var(--vert));
    color:black;
}
header[data-testid="stHeader"], footer, #MainMenu { display:none !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 🔐 SESSION
# ============================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None

# ============================================================
# 📥 CHARGEMENT CSV (PUBLIC)
# ============================================================

@st.cache_data(show_spinner=False)
def load_data_from_public_csv(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)

    # ✅ nettoyage robuste (corrige ton erreur .str sur colonnes non-string)
    df.columns = [str(c).strip() for c in df.columns]

    # retire colonnes vides éventuelles
    df = df.dropna(axis=1, how="all")
    return df

def normalize_text(s: str) -> str:
    return (str(s).strip().lower()
            .replace("é", "e").replace("è", "e").replace("ê", "e")
            .replace("à", "a").replace("ç", "c"))

# ============================================================
# 🖼️ VISUEL
# ============================================================

if os.path.exists(VISUEL):
    st.image(VISUEL, use_container_width=True)

# ============================================================
# 🧭 NAVIGATION
# ============================================================

tabs = st.tabs([
    "🏠 Accueil (Inscription)",
    "📊 Statistiques",
    "🗳️ Carte électorale",
    "🔐 Administration"
])

# ============================================================
# 🏠 ONGLET 1 — FORMULAIRE DIRECT SUR LA PAGE
# ============================================================

with tabs[0]:
    st.markdown("<div class='banner'>MALIKA BI ÑU BËGG – Une nouvelle ère s’annonce 🌍</div>", unsafe_allow_html=True)
    st.title("📘 Mouvement BD2027 – MBB")
    st.subheader("📝 Inscription comme membre")

    # ✅ Form visible directement — aucun lien vers Sheets
    st.markdown(
        f"""
        <iframe
            src="{FORM_URL}"
            width="100%"
            height="900"
            frameborder="0"
            style="background:white; border-radius:12px;">
        Chargement…
        </iframe>
        """,
        unsafe_allow_html=True
    )

    st.info("✅ Vos informations sont enregistrées automatiquement. Merci 🙏")

# ============================================================
# 📊 ONGLET 2 — STATS (lecture depuis CSV publié)
# ============================================================

with tabs[1]:
    st.subheader("📊 Statistiques")

    try:
        df = load_data_from_public_csv(CSV_URL)
        st.success("✅ Données chargées.")

        # Trouver colonne adresse/quartier
        cols_norm = {c: normalize_text(c) for c in df.columns}
        adresse_col = None
        for c, cn in cols_norm.items():
            if "adresse" in cn or "quartier" in cn:
                adresse_col = c
                break

        st.write("📅 Mise à jour :", datetime.now().strftime("%d/%m/%Y %H:%M"))

        if adresse_col:
            counts = df[adresse_col].fillna("Non renseigné").value_counts().reset_index()
            counts.columns = ["Quartier", "Nombre de membres"]
            fig = px.bar(counts, x="Quartier", y="Nombre de membres", color="Quartier", text="Nombre de membres")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Colonne 'Adresse/Quartier' introuvable dans le CSV.")

    except Exception as e:
        st.error("❌ Impossible de charger les données.")
        st.code(str(e))

# ============================================================
# 🗳️ ONGLET 3 — CARTE
# ============================================================

with tabs[2]:
    st.subheader("🗳️ Carte électorale – Commune de Malika")

    data_centres = pd.DataFrame({
        "Centre": ["École Malika Montagne", "École Privée Sanka", "École Seydi Anta Gadiaga"],
        "Bureaux": [14, 20, 18],
        "Lat": [14.7889, 14.7858, 14.7915],
        "Lon": [-17.3085, -17.3120, -17.3048],
    })

    fig = px.bar(data_centres, x="Centre", y="Bureaux", color="Centre", text="Bureaux")
    st.plotly_chart(fig, use_container_width=True)

    m = folium.Map(location=[14.7889, -17.3090], zoom_start=15, tiles="CartoDB positron")
    for _, r in data_centres.iterrows():
        folium.Marker([r["Lat"], r["Lon"]], popup=r["Centre"], tooltip=r["Centre"]).add_to(m)
    st_folium(m, height=450)

# ============================================================
# 🔐 ONGLET 4 — ADMIN (liste complète + stats)
# ============================================================

with tabs[3]:
    st.subheader("🔐 Connexion administrateur")

    if not st.session_state.authenticated:
        user = st.text_input("Identifiant")
        pwd = st.text_input("Mot de passe", type="password")

        if st.button("Se connecter"):
            if user in USERS and USERS[user] == pwd:
                st.session_state.authenticated = True
                st.session_state.username = user
                st.success("✅ Connexion réussie")
                st.rerun()
            else:
                st.error("❌ Identifiants incorrects")
    else:
        st.success(f"Connecté en tant que **{st.session_state.username}**")
        if st.button("Déconnexion"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.rerun()

        st.divider()
        st.subheader("📘 Liste complète des membres (lecture CSV)")

        try:
            df = load_data_from_public_csv(CSV_URL)
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error("Impossible de charger la base.")
            st.code(str(e))
