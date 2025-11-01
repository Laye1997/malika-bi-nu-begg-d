import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
import folium
from streamlit_folium import st_folium

# === CONFIGURATION ===
FICHIER_EXCEL = "Liste_Membres.xlsx"
CODE_SECRET = "MBB2025"  # code d'accès pour ajouter un membre
VISUEL = "561812309_122099008227068424_7173387226638749981_n.jpg"

# === IDENTIFIANTS DE CONNEXION (à adapter au besoin) ===
USERS = {
    "admin": "mbb2025",
    "president": "malika2025"
}

# === PARAMÈTRES DE LA PAGE ===
st.set_page_config(page_title="Base de données MBB", page_icon="📘", layout="wide")

# === STYLE GLOBAL (responsive + mobile friendly) ===
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
        /* Dataframe hover */
        [data-testid="stDataFrame"] table tbody tr:hover { background:#FCF3CF !important; color:#000 !important; }
    </style>
""", unsafe_allow_html=True)

# === CONNEXION ===
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None

if not st.session_state.authenticated:
    st.markdown("<div class='banner'>🔐 Accès sécurisé – Base de données MBB</div>", unsafe_allow_html=True)
    st.title("Connexion requise")

    username_input = st.text_input("👤 Identifiant")
    password_input = st.text_input("🔑 Mot de passe", type="password")

    if st.button("Se connecter"):
        if username_input in USERS and USERS[username_input] == password_input:
            st.session_state.authenticated = True
            st.session_state.username = username_input
            st.success("✅ Connexion réussie !")
            st.rerun()
        else:
            st.error("❌ Identifiant ou mot de passe incorrect.")
    st.stop()

# === BARRE LATÉRALE ===
st.sidebar.success(f"Connecté en tant que **{st.session_state.username}**")
if st.sidebar.button("🔒 Déconnexion"):
    st.session_state.authenticated = False
    st.session_state.username = None
    st.rerun()

# === VISUEL ===
if os.path.exists(VISUEL):
    st.image(VISUEL, use_container_width=True)

# === CHARGEMENT DU FICHIER EXCEL ===
if not os.path.exists(FICHIER_EXCEL):
    st.error(f"❌ Le fichier {FICHIER_EXCEL} est introuvable.")
    st.stop()

# Ligne 0 de l’Excel = en-tête → header=1 si ta 1ère ligne est une légende au-dessus
df = pd.read_excel(FICHIER_EXCEL, sheet_name="Liste des membres", header=1)

# Normalisation colonnes + suppression doublons de colonnes
df.columns = (df.columns.str.strip().str.lower()
              .str.replace("é","e").str.replace("è","e").str.replace("ê","e")
              .str.replace("à","a").str.replace("ç","c"))
df = df.loc[:, ~df.columns.duplicated()]

# Localiser la colonne adresse
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

# ===========================
# 🏠 ONGLET ACCUEIL
# ===========================
with tabs[0]:
    st.markdown("<div class='banner'>MALIKA BI ÑU BËGG – Une nouvelle ère s’annonce 🌍</div>", unsafe_allow_html=True)
    st.title("📘 Base de données du Mouvement - MBB")

    date_du_jour = datetime.now().strftime("%d %B %Y")
    st.subheader(f"👥 Liste actuelle des membres à la date du {date_du_jour}")
    st.dataframe(df, use_container_width=True)

    st.divider()
    st.subheader("➕ Ajouter un nouveau membre (protégé)")

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
                    # Contrôle doublon téléphone
                    tel_col = [c for c in df.columns if "tel" in c]
                    tel_new = str(telephone).replace(" ", "").strip()
                    if tel_col:
                        tel_exist = df[tel_col[0]].astype(str).str.replace(" ", "").str.strip()
                    else:
                        tel_exist = pd.Series([], dtype=str)

                    if tel_new in tel_exist.values:
                        st.error("❌ Ce numéro de téléphone existe déjà.")
                    else:
                        new_row = {
                            "Prénom": prenom, "Nom": nom, "Adresse": adresse, "Téléphone": telephone,
                            "Profession": profession, "Commission": commission, "Notes": notes
                        }
                        # Sauvegarde
                        df_to_write = pd.read_excel(FICHIER_EXCEL, sheet_name="Liste des membres", header=1)
                        df_to_write = pd.concat([df_to_write, pd.DataFrame([new_row])], ignore_index=True)
                        # Réécriture : garder même structure (en-tête à la même ligne)
                        with pd.ExcelWriter(FICHIER_EXCEL, engine="openpyxl") as writer:
                            df_to_write.to_excel(writer, index=False, sheet_name="Liste des membres")
                        st.success(f"✅ {prenom} {nom} ajouté avec succès !")
                        st.rerun()
                else:
                    st.warning("⚠️ Merci de renseigner au minimum Prénom, Nom et Téléphone.")
    elif code:  # code saisi mais incorrect
        st.error("❌ Code d'accès incorrect.")

# ===========================
# 🏘️ ONGLET PAR QUARTIER
# ===========================
with tabs[1]:
    st.markdown("### 🏘️ Membres regroupés par adresse (quartier)")
    if not col_adresse:
        st.error("❌ Colonne 'Adresse' introuvable dans le fichier.")
    else:
        adresse_col = col_adresse[0]

        # Graphique de répartition (tous les quartiers)
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
        # Tables par quartier
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

    # Graphique barres (texte visible au-dessus des barres)
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

    # Carte folium interactive
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

    st.divider()
    # Cartes visuelles
    st.markdown("#### 🏫 Détails des centres de vote")
    col1, col2, col3 = st.columns(3)
    for i, (titre, nb, c1, c2, max_bv) in enumerate([
        ("École Malika Montagne", 14, "#145A32", "#1E8449", 14),
        ("École Privée Sanka", 20, "#27AE60", "#F1C40F", 20),
        ("École Seydi Anta Gadiaga", 18, "#F4D03F", "#145A32", 18)
    ]):
        with [col1, col2, col3][i]:
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,{c1},{c2});
                        padding:15px;border-radius:15px;color:white;text-align:center;
                        box-shadow:2px 2px 8px rgba(0,0,0,0.3);'>
                <h4>🏫 {titre}</h4>
                <p><b>{nb}</b> bureaux de vote</p>
                <p>Bureaux : 1 → {max_bv}</p>
            </div>
            """, unsafe_allow_html=True)

# ===========================
# 📝 ONGLET COMPTE RENDU
# ===========================
with tabs[3]:
    st.markdown("### 📝 Compte Rendu des Réunions")
    st.info("Cette section affichera prochainement les comptes rendus officiels des réunions du mouvement MBB.")

# ===========================
# 🚫 ONGLET MEMBRES NON INSCRITS
# ===========================
with tabs[4]:
    st.markdown("### 🚫 Membres Non Inscrits")
    st.info("Aucune donnée à afficher pour le moment.")
