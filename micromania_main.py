import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- THÈME CUSTOM POUR LA SIDEBAR ---
st.markdown("""
<style>
    [data-testid=stSidebar] {
        background-color: #1f1f2e;
        color: white;
    }
    .css-10trblm {
        color: #1f1f2e;
    }
</style>
""", unsafe_allow_html=True)

# --- CHARGEMENT DONNÉES ---
df = pd.read_excel("./excel/micromania_donnees_fictives.xlsx", engine="openpyxl")

# Transformation CA pour score de performance
df["Score Performance"] = (df["Chiffre d'Affaires Annuel (€)"] - df["Chiffre d'Affaires Annuel (€)"].min()) / (
    df["Chiffre d'Affaires Annuel (€)"].max() - df["Chiffre d'Affaires Annuel (€)"].min()
)

# Taille magasin
categories = []
for surface in df["Surface (m²)"]:
    if surface < 250:
        categories.append("Format XS")
    elif surface < 350:
        categories.append("Format M")
    else:
        categories.append("Format XL")
df["Format Boutique"] = categories

# --- BARRE LATÉRALE ---
st.sidebar.header("Filtrage intelligent")

formats = df["Format Boutique"].unique().tolist()
choix_formats = st.sidebar.multiselect("Format", formats, default=formats)

df1 = df[df["Format Boutique"].isin(choix_formats)]

villes = df1["Ville"].unique().tolist()
choix_villes = st.sidebar.multiselect("Localisation", villes, default=villes)

df2 = df1[df1["Ville"].isin(choix_villes)]

magasins = df2["Nom Magasin"].unique().tolist()
choix_magasins = st.sidebar.multiselect("Point de vente", magasins, default=magasins)

df_final = df2[df2["Nom Magasin"].isin(choix_magasins)]

# --- TABLEAU DE BORD ---
st.title("🌙 Panorama Commercial - Micromania")

if not df_final.empty:
    st.subheader("Classement des points de vente")

    bar_fig = px.bar(
        df_final,
        x="Nom Magasin",
        y="Score Performance",
        color="Format Boutique",
        color_discrete_map={"Format XS": "#f94144", "Format M": "#f3722c", "Format XL": "#277da1"},
        title="Indice global de performance commerciale",
        labels={"Nom Magasin": "Magasin", "Score Performance": "Score"}
    )
    st.plotly_chart(bar_fig)

    st.subheader("Répartition stratégique")
    choix_regroupement = st.radio("Catégorie :", ["Ville", "Format Boutique"], horizontal=True)
    pie_fig = px.pie(
        df_final,
        names=choix_regroupement,
        title=f"Répartition selon {choix_regroupement.lower()}",
        color_discrete_sequence=["#577590", "#f9c74f", "#f9844a", "#90be6d"]
    )
    st.plotly_chart(pie_fig)

    st.subheader("Vision radar : profil magasin")

    magasin_cible = st.selectbox("Sélectionne un point de vente :", df_final["Nom Magasin"])
    ligne = df_final[df_final["Nom Magasin"] == magasin_cible].iloc[0]

    radar_fig = go.Figure()
    radar_fig.add_trace(go.Scatterpolar(
        r=[ligne["Nombre d'Employés"], ligne["Nombre de Transactions"], ligne["Chiffre d'Affaires Annuel (€)"]],
        theta=["Effectif", "Transactions", "CA"],
        fill='toself',
        name=magasin_cible,
        line=dict(color="#43aa8b")
    ))
    radar_fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, max(
            df["Nombre d'Employés"].max(),
            df["Nombre de Transactions"].max(),
            df["Chiffre d'Affaires Annuel (€)"].max()
        )])),
        showlegend=False,
        title="Profil radar - Indicateurs clés"
    )
    st.plotly_chart(radar_fig)

else:
    st.warning("Aucun résultat ne correspond à votre sélection actuelle.")
