import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import folium
from streamlit_folium import st_folium

# =====================================================
# 🔧 CONFIGURATION (SANS SECRETS)
# =====================================================

CSV_URL = "COLLE_ICI_LE_LIEN_CSV_PUBLIE"
FORM_URL = "COLLE_ICI_LE_LIEN_GOOGLE_FORM_EMBED"

VISUEL = "561812309_122099008227068424_7173387226638749981_n.jpg"

USERS = {
    "admin": "mbb2025",
    "president": "malika2025"
}

# =====================================================
# ⚙️ PAGE
# =====================================================

st.set_page_config(
    page_title="Base de données MBB",
    page_icon="📘",
    layout="wide"
)

# =====================================================
# 🎨 STYLE
# =====================================================

st.markdown("""
<style>
:root { --vert:#145A32; --jaune:#F4D03F; }
.stApp {
    background: linear-gradient(120deg, var(--vert), var(--jaune));
    color: white;
    font-family: "Segoe UI", sans-serif;
}
h1,h2,h3,h4 { color:white !important; }
.banner {
    background: linear-gradient(90deg, var(--vert), var(--jaune));
    padding:14px;
    border-radius:12px;
    text-align:center;
    font-size:22px;
    font-weight:bold;
    margin-bottom:20px;
}
.stButton>button {
    background: linear-gradient(45deg, var(--vert), var(--jaune));
    color:white;
    border-radius:10px;
    font-weight:bold;
    border:none;
}
header, footer, #MainMenu { display:none !important; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# 🔐 SESSION
# =====================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None

# =====================================================
# 📥 CHARGEMENT DONNÉES (CSV PUBLIC)
# =====================================================

@st.cache_data(show_spinner=False)
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = [str(c).strip() for c in df.columns]
    return df

# =====================================================
# 🖼️ VISUEL
# =====================================================

try:
    st.image(VISUEL, use_container_width=True)
except:
    pass

# =====================================================
# 🧭 ONGLET
# =====================================================

tabs = st.tabs([
    "🏠 Inscription",
    "📊 Statistiques",
    "🗳️ Carte électorale",
    "🔐 Administration"
])

# =====================================================
# 🏠 ONGLET INSCRIPTION (FORM DIRECT)
# =====================================================

with tabs[0]:
    st.markdown("<div class='banner'>MALIKA BI ÑU BËGG – Une nouvelle ère s’annonce 🌍</div>", unsafe_allow_html=True)
    st.title("📘 Mouvement BD2027 – MBB")
    st.subheader("📝 Inscription comme membre")

    st.markdown(
        f"""
        <iframe src="{FORM_URL}"
        width="100%"
        height="900"
        frameborder="0"
        style="background:white; border-radius:12px;">
        </iframe>
        """,
        unsafe_allow_html=True
    )

    st.success("✅ Inscription simple, rapide et sécurisée.")

# =====================================================
# 📊 ONGLET STATISTIQUES
# =====================================================

with tabs[1]:
    try:
        df = load_data()
        st.subheader("📊 Statistiques générales")

        # Trouver colonne quartier/adresse
        col_adresse = None
        for c in df.columns:
            if "adress" in c.lower() or "quartier" in c.lower():
                col_adresse = c
                break

        if col_adresse:
            counts = df[col_adresse].value_counts().reset_index()
            counts.columns = ["Quartier", "Nombre"]

            fig = px.bar(
                counts,
                x="Quartier",
                y="Nombre",
                color="Quartier",
                text="Nombre"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Colonne Quartier / Adresse non trouvée.")

    except Exception as e:
        st.error("❌ Impossible de charger les statistiques.")
        st.code(str(e))

# =====================================================
# 🗳️ ONGLET CARTE
# =====================================================

with tabs[2]:
    st.subheader("🗳️ Carte électorale – Commune de Malika")

    centres = pd.DataFrame({
        "Centre": ["École Malika Montagne", "École Privée Sanka", "École Seydi Anta Gadiaga"],
        "Bureaux": [14, 20, 18],
        "Lat": [14.7889, 14.7858, 14.7915],
        "Lon": [-17.3085, -17.3120, -17.3048]
    })

    fig = px.bar(centres, x="Centre", y="Bureaux", color="Centre", text="Bureaux")
    st.plotly_chart(fig, use_container_width=True)

    m = folium.Map(location=[14.789, -17.309], zoom_start=15)
    for _, r in centres.iterrows():
        folium.Marker([r.Lat, r.Lon], popup=r.Centre).add_to(m)
    st_folium(m, height=450)

# =====================================================
# 🔐 ONGLET ADMIN
# =====================================================

with tabs[3]:
    if not st.session_state.authenticated:
        user = st.text_input("Identifiant")
        pwd = st.text_input("Mot de passe", type="password")

        if st.button("Se connecter"):
            if user in USERS and USERS[user] == pwd:
                st.session_state.authenticated = True
                st.session_state.username = user
                st.success("Connexion réussie")
                st.rerun()
            else:
                st.error("Identifiants incorrects")
    else:
        st.success(f"Connecté : {st.session_state.username}")

        if st.button("Déconnexion"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.rerun()

        st.divider()
        st.subheader("📘 Base complète des membres")

        try:
            df = load_data()
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error("Erreur chargement base")
            st.code(str(e))
