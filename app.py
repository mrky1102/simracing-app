import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. ADATBÁZISOK ---
NEVEK = ["mrky", "Radnom", "Nova"]

GT7_FULL = {
    "GT7 - World Circuits (Europe)": [
        "24 Heures du Mans (13.62 km)", "24 Heures du Mans - No Chicane (13.62 km)", "Autodromo Nazionale Monza (5.79 km)", "Autodromo Nazionale Monza - No Chicane (5.79 km)", "Brands Hatch GP (3.91 km)", "Brands Hatch Indy (1.94 km)", "Circuit de Barcelona-Catalunya GP (4.67 km)", "Circuit de Barcelona-Catalunya No Chicane (4.65 km)", "Circuit de Barcelona-Catalunya National (2.97 km)", "Circuit de Barcelona-Catalunya Rallycross (1.13 km)", "Circuit de Spa-Francorchamps (7.00 km)", "Spa 24h Layout (7.00 km)", "Nürburgring 24h (25.37 km)", "Nürburgring Endurance (24.37 km)", "Nürburgring GP (5.14 km)", "Nürburgring Nordschleife (20.83 km)", "Nürburgring Nordschleife Tourist (19.10 km)", "Nürburgring Sprint (3.62 km)", "Red Bull Ring (4.31 km)", "Red Bull Ring Short (2.33 km)", "Sardegna Road A (5.11 km)", "Sardegna Road A Rev (5.11 km)", "Sardegna Road B (3.89 km)", "Sardegna Road B Rev (3.89 km)", "Sardegna Road C (2.66 km)", "Sardegna Road C Rev (2.66 km)", "Sainte-Croix A (9.47 km)", "Sainte-Croix A Rev (9.47 km)", "Sainte-Croix B (7.06 km)", "Sainte-Croix B Rev (7.06 km)", "Sainte-Croix C (10.82 km)", "Sainte-Croix C Rev (10.82 km)", "Alsace Village (5.42 km)", "Alsace Village Rev (5.42 km)", "Alsace Test Course (1.99 km)", "Dragon Trail Seaside (5.20 km)", "Dragon Trail Seaside Rev (5.20 km)", "Dragon Trail Gardens (4.35 km)", "Dragon Trail Gardens Rev (4.35 km)", "Lago Maggiore Full (5.80 km)", "Lago Maggiore Full Rev (5.80 km)", "Lago Maggiore Centre (1.70 km)", "Lago Maggiore East (3.64 km)", "Lago Maggiore West (4.16 km)"
    ],
    "GT7 - World Circuits (Americas)": [
        "Daytona Road Course (5.73 km)", "Daytona Tri-Oval (4.02 km)", "Interlagos (4.30 km)", "Laguna Seca (3.60 km)", "Road Atlanta (4.08 km)", "Watkins Glen Long (5.55 km)", "Watkins Glen Short (3.95 km)", "Willow Springs Big Willow (3.95 km)", "Willow Springs Streets (2.67 km)", "Willow Springs Horse Thief (1.63 km)", "Grand Valley Highway 1 (5.10 km)", "Grand Valley Highway 1 Rev (5.10 km)", "Grand Valley South (2.00 km)", "Trial Mountain (3.98 km)", "Trial Mountain Rev (3.98 km)", "Deep Forest (3.51 km)", "Deep Forest Rev (3.51 km)", "Blue Moon Bay (3.20 km)", "Blue Moon Bay Rev (3.20 km)", "Blue Moon Bay Infield A (3.35 km)", "Blue Moon Bay Infield B (2.86 km)", "Colorado Springs Lake (2.99 km)", "Fishermans Ranch (6.89 km)", "Special Stage Route X (30.28 km)"
    ],
    "GT7 - World Circuits (Asia-Oceania)": [
        "Autopolis Full (4.67 km)", "Autopolis Short (3.02 km)", "Fuji Speedway (4.56 km)", "Fuji Speedway Short (4.52 km)", "Mount Panorama (6.21 km)", "Suzuka Full (5.80 km)", "Suzuka East (2.24 km)", "Tsukuba (2.04 km)", "Kyoto Yamagiwa (4.91 km)", "Kyoto Miyabi (2.38 km)", "Kyoto Yamagiwa+Miyabi (6.84 km)", "High Speed Ring (4.00 km)", "High Speed Ring Rev (4.00 km)", "Tokyo Central Clockwise (4.40 km)", "Tokyo East Clockwise (7.30 km)", "Tokyo South Clockwise (5.20 km)"
    ]
}

DIRT_FULL = {
    "Argentina": ["Las Juntas (8.25 km)", "Valle de los puentes (7.98 km)", "Camino a La Puerta (8.25 km)", "San Isidro (4.48 km)", "El Condor (5.21 km)", "Miraflores (3.35 km)", "Capilla del Monte (4.48 km)", "La Merced (2.84 km)", "Camino a Coneta (4.48 km)", "Huillaprima (3.35 km)", "El Rodeo (2.84 km)", "Valle de los puentes reverse (7.98 km)"],
    "Australia": ["Mount Kaye Pass (12.50 km)", "Chandlers Creek (12.34 km)", "Bondi Forest (7.01 km)", "Rockton Plains (6.89 km)", "Noorinbee Ridge Ascent (5.28 km)", "Noorinbee Ridge Descent (5.28 km)", "Taylor Farm (5.28 km)", "Yambulla Mountain Ascent (6.64 km)", "Old South Road (6.64 km)", "Mount Kaye Pass Reverse (12.50 km)", "Chandlers Creek Reverse (12.34 km)", "Bondi Forest Reverse (7.01 km)"],
    "Finland": ["Kotajärvi (12.42 km)", "Isojärvi (15.04 km)", "Kakaristo (15.04 km)", "Pitäjävesi (12.42 km)", "Ouninpohja (15.04 km)", "Hamelahti (15.04 km)", "Kailajärvi (7.51 km)", "Naajärvi (7.51 km)", "Kontinjärvi (15.04 km)", "Paskuri (12.42 km)", "Isojärvi Reverse (15.04 km)", "Kakaristo Reverse (15.04 km)"],
    "Germany": ["Oberstein (11.67 km)", "Frauenberg (11.67 km)", "Waldabstieg (5.39 km)", "Kreuzungsring (6.28 km)", "Verbundsring (5.85 km)", "Innerer Feld-Sprint (5.85 km)", "Ruschberg (11.67 km)", "Hammerstein (11.67 km)", "Kreuzungsring reverse (6.28 km)", "Innerer Feld-Sprint umgekehrt (5.85 km)", "Verbundsring reverse (5.85 km)", "Waldabstieg reverse (5.39 km)"],
    "Greece": ["Anodou Farmakas (9.61 km)", "Koryfi Dafni (9.50 km)", "Abies Koilada (9.61 km)", "Ourea Psila (9.50 km)", "Fourkéta Kourva (4.81 km)", "Kathodo Leonti (4.81 km)", "Tsiristra (4.69 km)", "Perasma Platani (4.69 km)", "Ourea Spevsi (9.50 km)", "Fourkéta Kourva Reverse (4.81 km)", "Anodou Farmakas Reverse (9.61 km)", "Koryfi Dafni Reverse (9.50 km)"],
    "Monaco": ["Col de Turini - Départ (9.84 km)", "Pra d’Alart (9.84 km)", "Route de Turini (10.85 km)", "Col de Turini - Départ en descente (6.84 km)", "Col de Turini - Descente (5.17 km)", "Gordolon - Courte montée (5.17 km)", "Col de Turini - Sprint en montée (4.72 km)", "Col de Turini - Sprint en descente (4.72 km)", "Approche du Col de Turini - Montée (3.95 km)", "Route de Turini - Descente (3.95 km)", "Pra d’Alart Reverse (9.84 km)", "Vallée descendante (5.17 km)"],
    "New Zealand": ["Waimarama Point (16.08 km)", "Te Awanga Forward (11.48 km)", "Ocean Beach (11.48 km)", "Elsthorpe Sprint Forward (7.42 km)", "Waimarama Sprint Forward (7.42 km)", "Maungaturoto (16.08 km)", "Te Awanga Reverse (11.48 km)", "Ocean Beach Reverse (11.48 km)", "Elsthorpe Sprint Reverse (7.42 km)", "Waimarama Point Reverse (16.08 km)", "Te Awanga Sprint Forward (11.48 km)", "Waimarama Sprint Reverse (7.42 km)"],
    "Poland": ["Czarny Las (14.59 km)", "Jezioro Rotcze (13.42 km)", "Zagórze (14.59 km)", "Leśna Dzicz (13.42 km)", "Marynka (7.74 km)", "Borysik (7.74 km)", "Jagodno (14.59 km)", "Lejno (13.42 km)", "Kopina (14.59 km)", "Zieńki (13.42 km)", "Uściwierz (7.74 km)", "Borysik Reverse (7.74 km)"],
    "Scotland": ["Old Butterstone Muir (5.97 km)", "Glencastle Farm (5.25 km)", "Rosebank Farm (5.97 km)", "Newhouse Bridge (5.25 km)", "South Morningside (5.25 km)", "Annbank Station (5.97 km)", "Old Butterstone Muir Reverse (5.97 km)", "Glencastle Farm Reverse (5.25 km)", "Annbank Station Reverse (5.97 km)", "Rosebank Farm Reverse (5.97 km)", "Old Butterstone Loch (5.97 km)", "Annbank Station Forward (5.97 km)"],
    "Spain": ["Comienzo en Bellriu (14.34 km)", "Final en Bellriu (14.34 km)", "Camino a Centenera (10.57 km)", "Centenera (10.57 km)", "Ascenso bosque Montverd (6.81 km)", "Salida desde Montverd (7.01 km)", "Ascenso por valle el Gualet (7.01 km)", "Viñedos Dardenya (6.55 km)", "Viñedos Dardenya inversa (6.55 km)", "Viñedos belül valle Parra (6.81 km)", "Subida por carretera (4.58 km)", "Descenso por carretera (4.58 km)"],
    "USA": ["North Fork Pass (12.86 km)", "Hancock Creek (12.84 km)", "Tolt Valley Sprint (6.43 km)", "Beaver Creek Trail (6.43 km)", "Oak Canyon Run (6.41 km)", "Mountain Knolls (6.41 km)", "North Fork Pass Reverse (12.86 km)", "Hancock Creek Reverse (12.84 km)", "Tolt Valley Sprint Reverse (6.43 km)", "Beaver Creek Trail Reverse (6.43 km)", "Oak Canyon Run Reverse (6.41 km)", "Mountain Knolls Reverse (6.41 km)"],
    "Wales": ["Bidno Moorland (4.81 km)", "Sweet Lamb (9.90 km)", "Pant Mawr (4.81 km)", "Dyffryn Afon (9.90 km)", "River Severn Valley (9.90 km)", "Geufron Forest (10.00 km)", "Manod (4.81 km)", "Bronfelen (11.40 km)", "Fferm Wynt Reverse (5.69 km)", "Bidno Moorland Reverse (4.81 km)", "Pant Mawr Reverse (4.81 km)", "Sweet Lamb Reverse (9.90 km)"],
    "Sweden": ["Hamra (12.34 km)", "Älgsjön (7.35 km)", "Lysvik (12.67 km)", "Ransbysäter (11.98 km)", "Norraskoga (11.98 km)", "Skogsrallyt (5.25 km)", "Älgsjön Sprint (5.25 km)", "Björklangen (5.19 km)", "Östra Hinnsjön (5.19 km)", "Stor-Jangen Sprint (6.68 km)", "Stor-Jangen Sprint Reverse (6.68 km)", "Älgsjön Reverse (7.35 km)"]
}

# --- 2. FELHŐ KAPCSOLÓDÁS ---
st.set_page_config(page_title="SimRacing Arena CLOUD", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # Kiolvassuk a 'results' fület, ttl=0 biztosítja a friss adatot
        return conn.read(worksheet="results", ttl="0s")
    except:
        return pd.DataFrame(columns=["Dátum", "Játék", "Kategória", "Pálya", "Autó", "Versenyző", "Másodperc", "Idő"])

if 'results' not in st.session_state:
    st.session_state.results = load_data()

# --- 3. MEGJELENÉS ---
st.markdown("""
<style>
    .card { padding: 15px; border-radius: 12px; margin-bottom: 10px; border: 2px solid #555; text-align: center; }
    .gold { border: 4px solid #FFD700 !important; background-color: #3d3500; }
    .silver { border: 4px solid #C0C0C0 !important; background-color: #2e2e2e; }
    .bronze { border: 4px solid #CD7F32 !important; background-color: #331a00; }
    .track-row { background: #1e1e1e; padding: 10px; border-radius: 8px; margin-top: 5px; border: 1px solid #333; }
</style>
""", unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["🏁 ÚJ IDŐ", "🏆 TABELLA", "⚙️ ADMIN"])

# --- ÚJ IDŐ ---
with t1:
    st.subheader("Idő rögzítése")
    sel_jatek = st.selectbox("Játék", ["Gran Turismo 7", "Dirt Rally 2.0"], key="main_j")
    kat_dict = GT7_FULL if sel_jatek == "Gran Turismo 7" else DIRT_FULL
    sel_kat = st.selectbox("Kategória / Ország", sorted(list(kat_dict.keys())), key="main_k")
    sel_palya = st.selectbox("Pálya / Szakasz", sorted(kat_dict[sel_kat]), key="main_p")

    with st.form("entry", clear_on_submit=True):
        auto = st.text_input("Használt autó")
        nev = st.selectbox("Versenyző", NEVEK)
        ido = st.text_input("Idő (p:mp.ezred)", placeholder="pl. 1:24.500")
        if st.form_submit_button("💾 MENTÉS A FELHŐBE", use_container_width=True):
            try:
                p_p, mp_p = ido.split(":")
                total = int(p_p) * 60 + float(mp_p)
                new_row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d %H:%M"), sel_jatek, sel_kat, sel_palya, auto, nev, total, ido]], columns=st.session_state.results.columns)
                st.session_state.results = pd.concat([st.session_state.results, new_row], ignore_index=True)
                # FELHŐ FRISSÍTÉS
                conn.update(worksheet="results", data=st.session_state.results)
                st.success("Adatok szinkronizálva a Google Drive-val!")
                st.rerun()
            except: st.error("Hibás formátum! (p:mp.ezred)")

# --- TABELLA ---
with t2:
    b_sel = st.selectbox("Játék választása", ["Gran Turismo 7", "Dirt Rally 2.0"], key="view_j")
    st.subheader("🥇 Bajnoki Összesített")
    df_f = st.session_state.results[st.session_state.results["Játék"] == b_sel]
    
    pts = {n: 0 for n in NEVEK}
    if not df_f.empty:
        best_ones = df_f.loc[df_f.groupby(["Pálya", "Versenyző"])["Másodperc"].idxmin()]
        for p in best_ones["Pálya"].unique():
            r = best_ones[best_ones["Pálya"] == p].sort_values("Másodperc").head(3)
            for i, (_, row) in enumerate(r.iterrows()):
                if row["Versenyző"] in pts: pts[row["Versenyző"]] += (3 if i==0 else 2 if i==1 else 1)
    
    sorted_pts = sorted(pts.items(), key=lambda x: x[1], reverse=True)
    cols = st.columns(len(sorted_pts) if len(sorted_pts) > 0 else 1)
    for idx, (n, p) in enumerate(sorted_pts):
        c = "gold" if idx==0 else "silver" if idx==1 else "bronze" if idx==2 else "normal"
        m = "🥇" if idx==0 else "🥈" if idx==1 else "🥉" if idx==2 else f"#{idx+1}"
        with cols[idx]: 
            st.markdown(f'<div class="card {c}"><div style="font-size:3rem;">{m}</div><b style="font-size:1.5rem;">{n.upper()}</b><br><span style="font-size:1.2rem;">{p} pont</span></div>', unsafe_allow_html=True)

    st.divider()
    st.subheader("📍 Pálya Rangsorok")
    tracks = sorted(df_f["Pálya"].unique()) if not df_f.empty else []
    if tracks:
        s_t = st.selectbox("Pálya választása", tracks)
        t_df = df_f[df_f["Pálya"] == s_t].loc[df_f[df_f["Pálya"] == s_t].groupby("Versenyző")["Másodperc"].idxmin()].sort_values("Másodperc")
        for i, (_, r) in enumerate(t_df.iterrows(), 1):
            st.markdown(f'<div class="track-row">{i}. <b>{r["Versenyző"]}</b>: {r["Idő"]} ({r["Autó"]})</div>', unsafe_allow_html=True)

# --- ADMIN ---
with t3:
    st.header("⚙️ Adminisztráció")
    if st.button("🔄 ADATOK KÉNYSZERÍTETT ÚJRATÖLTÉSE A GOOGLE-BŐL", use_container_width=True):
        st.session_state.results = load_data()
        st.rerun()
    
    if st.button("⚠️ ÖSSZES EREDMÉNY TÖRLÉSE (NULLÁZÁS)", type="primary", use_container_width=True):
        empty_df = pd.DataFrame(columns=["Dátum", "Játék", "Kategória", "Pálya", "Autó", "Versenyző", "Másodperc", "Idő"])
        conn.update(worksheet="results", data=empty_df)
        st.session_state.results = empty_df
        st.rerun()
