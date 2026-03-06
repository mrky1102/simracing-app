import streamlit as st
import pandas as pd
from datetime import datetime
import json
import requests
import base64

# --- 1. ALAPÉRTELMEZETT PÁLYALISTA ---
NEVEK_DEFAULT = ["mrky", "Radnom", "Nova"]

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


# --- 2. FELHŐ KEZELÉS (GITHUB) ---
def load_from_github():
    try:
        token = st.secrets["GITHUB_TOKEN"]
        repo = st.secrets["REPO_NAME"]
        url = f"https://api.github.com/repos/{repo}/contents/data.json"
        headers = {"Authorization": f"token {token}"}
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            content = base64.b64decode(r.json()["content"]).decode("utf-8")
            return json.loads(content)
    except:
        pass
    return None

def save_to_github(data):
    try:
        token = st.secrets["GITHUB_TOKEN"]
        repo = st.secrets["REPO_NAME"]
        url = f"https://api.github.com/repos/{repo}/contents/data.json"
        headers = {"Authorization": f"token {token}"}
        r = requests.get(url, headers=headers)
        sha = r.json()["sha"] if r.status_code == 200 else None
        content_bytes = json.dumps(data, indent=4, ensure_ascii=False).encode("utf-8")
        content_base64 = base64.b64encode(content_bytes).decode("utf-8")
        payload = {"message": "SimRacing update", "content": content_base64}
        if sha: payload["sha"] = sha
        res = requests.put(url, headers=headers, json=payload)
        return res.status_code in [200, 201]
    except:
        return False

# --- 3. SESSION STATE INICIALIZÁLÁS ---
if 'app_data' not in st.session_state:
    loaded = load_from_github()
    if loaded and "config" in loaded:
        st.session_state.app_data = loaded
    else:
        st.session_state.app_data = {
            "results": [],
            "config": {"nevek": NEVEK_DEFAULT, "jatekok": {"Gran Turismo 7": GT7_FULL, "Dirt Rally 2.0": DIRT_FULL}}
        }

st.set_page_config(page_title="SimRacing Arena v41", layout="wide")

# --- 4. JAVÍTOTT CSS (Középre igazítás fix) ---
st.markdown("""
<style>
    /* Alap kártya stílus fix színekkel a láthatóságért */
    .card { 
        padding: 20px; 
        border-radius: 15px; 
        margin-bottom: 10px; 
        border: 2px solid #555; 
        text-align: center; 
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background-color: #222222; /* Fix sötét háttér */
        color: #ffffff !important;   /* Fix fehér szöveg */
        box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
    }
    
    /* Érmek színei - kicsit élénkebbek a kontraszt miatt */
    .gold { border: 4px solid #FFD700 !important; background-color: #332d00 !important; }
    .silver { border: 4px solid #C0C0C0 !important; background-color: #2b2b2b !important; }
    .bronze { border: 4px solid #CD7F32 !important; background-color: #301e00 !important; }
    
    .medal-icon { font-size: 45px; margin-bottom: 5px; display: block; }
    
    /* Feliratok színeinek kényszerítése */
    .player-name { 
        font-weight: bold; 
        font-size: 20px; 
        margin-top: 5px; 
        color: #ffffff !important; 
    }
    .points { 
        font-size: 16px; 
        color: #FFD700 !important; /* Arany színű pontok a jobb láthatóságért */
        font-weight: bold;
    }
    
    .track-row { 
        background: #1e1e1e; 
        color: white !important;
        padding: 10px; 
        border-radius: 8px; 
        margin-top: 5px; 
        border: 1px solid #444; 
    }
</style>
""", unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["🏁 ÚJ IDŐ", "🏆 TABELLA", "⚙️ ADMIN"])

# --- ÚJ IDŐ ---
with t1:
    conf = st.session_state.app_data["config"]
    sel_jatek = st.selectbox("Játék", list(conf["jatekok"].keys()))
    kat_dict = conf["jatekok"][sel_jatek]
    if kat_dict:
        sel_kat = st.selectbox("Kategória", sorted(list(kat_dict.keys())))
        sel_palya = st.selectbox("Pálya", sorted(kat_dict[sel_kat]))
        with st.form("entry", clear_on_submit=True):
            auto = st.text_input("Autó")
            nev = st.selectbox("Versenyző", conf["nevek"])
            ido = st.text_input("Idő (p:mp.ezred)")
            if st.form_submit_button("💾 MENTÉS"):
                try:
                    p, mp = ido.split(":")
                    total = int(p) * 60 + float(mp)
                    new_row = {"Dátum": datetime.now().strftime("%Y-%m-%d %H:%M"), "Játék": sel_jatek, "Kategória": sel_kat, "Pálya": sel_palya, "Autó": auto, "Versenyző": nev, "Másodperc": total, "Idő": ido}
                    st.session_state.app_data["results"].append(new_row)
                    save_to_github(st.session_state.app_data)
                    st.success("Mentve!")
                    st.rerun()
                except: st.error("Formátum: p:mp.ezred")

# --- TABELLA (Javított dizájn) ---
with t2:
    results_list = st.session_state.app_data["results"]
    df = pd.DataFrame(results_list)
    if not df.empty:
        j_sel = st.selectbox("Bajnokság választása", list(conf["jatekok"].keys()))
        df_f = df[df["Játék"] == j_sel]
        
        # Pontok és érmek kiszámítása
        pts = {n: 0 for n in conf["nevek"]}
        medals = {n: {"arany": 0, "ezüst": 0, "bronz": 0} for n in conf["nevek"]}
        
        if not df_f.empty:
            best_times = df_f.loc[df_f.groupby(["Pálya", "Versenyző"])["Másodperc"].idxmin()]
            for track in best_times["Pálya"].unique():
                tr_res = best_times[best_times["Pálya"] == track].sort_values("Másodperc").head(3)
                for i, (_, row) in enumerate(tr_res.iterrows()):
                    v = row["Versenyző"]
                    if v in pts:
                        pts[v] += (3 if i == 0 else 2 if i == 1 else 1)
                        if i == 0: medals[v]["arany"] += 1
                        elif i == 1: medals[v]["ezüst"] += 1
                        elif i == 2: medals[v]["bronz"] += 1

        # 1. Pontszám kártyák
        sorted_pts = sorted(pts.items(), key=lambda x: x[1], reverse=True)
        cols = st.columns(len(sorted_pts))
        for idx, (name, score) in enumerate(sorted_pts):
            style = "gold" if idx == 0 else "silver" if idx == 1 else "bronze" if idx == 2 else ""
            m_icon = "🥇" if idx == 0 else "🥈" if idx == 1 else "🥉" if idx == 2 else f"#{idx+1}"
            with cols[idx]:
                st.markdown(f'<div class="card {style}"><span class="medal-icon">{m_icon}</span><div class="player-name">{name.upper()}</div><div class="points">{score} pont</div></div>', unsafe_allow_html=True)

        # 2. Összesített éremtáblázat
        st.divider()
        st.subheader("🏅 Összesített Éremtáblázat")
        m_data = []
        for name in conf["nevek"]:
            m_data.append({"Név": name, "🥇": medals[name]["arany"], "🥈": medals[name]["ezüst"], "🥉": medals[name]["bronz"], "Össz": sum(medals[name].values())})
        m_df = pd.DataFrame(m_data).sort_values(["🥇", "🥈", "🥉"], ascending=False)
        
        # HTML táblázat a biztos láthatóságért
        medal_html = "<table class='medal-table'><tr><th>Pilóta</th><th>🥇</th><th>🥈</th><th>🥉</th><th>Össz</th></tr>"
        for _, r in m_df.iterrows():
            medal_html += f"<tr><td><b>{r['Név']}</b></td><td>{r['🥇']}</td><td>{r['🥈']}</td><td>{r['🥉']}</td><td>{r['Össz']}</td></tr>"
        medal_html += "</table>"
        st.markdown(medal_html, unsafe_allow_html=True)

        # 3. Pálya rangsorok
        st.divider()
        st.subheader("📍 Pálya Rangsorok")
        all_tr = sorted(df_f["Pálya"].unique())
        if all_tr:
            p_sel = st.selectbox("Válassz pályát", all_tr)
            t_df = df_f[df_f["Pálya"] == p_sel].loc[df_f[df_f["Pálya"] == p_sel].groupby("Versenyző")["Másodperc"].idxmin()].sort_values("Másodperc")
            for i, (_, r) in enumerate(t_df.iterrows(), 1):
                st.markdown(f'<div class="track-row">{i}. <b>{r["Versenyző"]}</b>: {r["Idő"]} <small>({r["Autó"]})</small></div>', unsafe_allow_html=True)
    else: st.info("Még nincsenek adatok a bajnokságban.")

# --- BŐVÍTETT ADMIN ---
with t3:
    st.header("⚙️ Adminisztrációs Központ")
    
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

    if not st.session_state.admin_authenticated:
        password_input = st.text_input("Admin jelszó", type="password")
        if st.button("Bejelentkezés"):
            if password_input == st.secrets["ADMIN_PASSWORD"]:
                st.session_state.admin_authenticated = True
                st.rerun()
            else: st.error("Hibás jelszó!")
    else:
        if st.button("🔓 KIJELENTKEZÉS"):
            st.session_state.admin_authenticated = False; st.rerun()
        st.divider()
        if st.button("🔄 ADATOK FRISSÍTÉSE GITHUBRÓL"):
            st.session_state.app_data = load_from_github(); st.rerun()

        # 1. VERSENYZŐK
        st.subheader("👤 Versenyzők kezelése")
        v1, v2, v3 = st.columns(3)
        with v1:
            new_v = st.text_input("Új versenyző")
            if st.button("Versenyző Mentése"):
                if new_v: st.session_state.app_data["config"]["nevek"].append(new_v); save_to_github(st.session_state.app_data); st.rerun()
        with v2:
            mod_v_old = st.selectbox("Módosítandó név", st.session_state.app_data["config"]["nevek"])
            mod_v_new = st.text_input("Új név ")
            if st.button("Név Átírása"):
                idx = st.session_state.app_data["config"]["nevek"].index(mod_v_old)
                st.session_state.app_data["config"]["nevek"][idx] = mod_v_new; save_to_github(st.session_state.app_data); st.rerun()
        with v3:
            del_v = st.selectbox("Törlendő név", st.session_state.app_data["config"]["nevek"])
            if st.button("Versenyző Törlése", type="primary"):
                st.session_state.app_data["config"]["nevek"].remove(del_v); save_to_github(st.session_state.app_data); st.rerun()

        st.divider()

        # 2. JÁTÉKOK (ÚJ FUNKCIÓK)
        st.subheader("🎮 Játékok kezelése")
        g1, g2, g3 = st.columns(3)
        with g1:
            new_g = st.text_input("Új játék hozzáadása")
            if st.button("Játék Létrehozása"):
                if new_g: 
                    st.session_state.app_data["config"]["jatekok"][new_g] = {}
                    save_to_github(st.session_state.app_data); st.rerun()
        with g2:
            mod_g_old = st.selectbox("Átnevezendő játék", list(st.session_state.app_data["config"]["jatekok"].keys()))
            mod_g_new = st.text_input("Játék új neve")
            if st.button("Játék Átnevezése"):
                if mod_g_new:
                    st.session_state.app_data["config"]["jatekok"][mod_g_new] = st.session_state.app_data["config"]["jatekok"].pop(mod_g_old)
                    save_to_github(st.session_state.app_data); st.rerun()
        with g3:
            del_g = st.selectbox("Törlendő játék", list(st.session_state.app_data["config"]["jatekok"].keys()))
            if st.button("Játék Törlése ", type="primary"):
                del st.session_state.app_data["config"]["jatekok"][del_g]
                save_to_github(st.session_state.app_data); st.rerun()

        st.divider()

        # 3. KATEGÓRIÁK ÉS PÁLYÁK
        st.subheader("📍 Kategóriák és Pályák")
        sel_j_adm = st.selectbox("Melyik játékban szerkesztesz?", list(st.session_state.app_data["config"]["jatekok"].keys()))
        k1, k2 = st.columns(2)
        with k1:
            new_k = st.text_input("Új kategória (pl. Gr.3)")
            if st.button("Kategória Hozzáadása"):
                st.session_state.app_data["config"]["jatekok"][sel_j_adm][new_k] = []
                save_to_github(st.session_state.app_data); st.rerun()
            kat_l = list(st.session_state.app_data["config"]["jatekok"][sel_j_adm].keys())
            if kat_l:
                del_k = st.selectbox("Kategória törlése", kat_l)
                if st.button("Kategória Törlése", type="primary"):
                    del st.session_state.app_data["config"]["jatekok"][sel_j_adm][del_k]
                    save_to_github(st.session_state.app_data); st.rerun()
        with k2:
            if kat_l:
                sel_k_p = st.selectbox("Válassz kategóriát", kat_l)
                new_p = st.text_input("Új pálya neve")
                if st.button("Pálya Hozzáadása"):
                    st.session_state.app_data["config"]["jatekok"][sel_j_adm][sel_k_p].append(new_p)
                    save_to_github(st.session_state.app_data); st.rerun()
                p_l = st.session_state.app_data["config"]["jatekok"][sel_j_adm][sel_k_p]
                if p_l:
                    del_p = st.selectbox("Pálya törlése", sorted(p_l))
                    if st.button("Pálya Törlése ", type="primary"):
                        st.session_state.app_data["config"]["jatekok"][sel_j_adm][sel_k_p].remove(del_p)
                        save_to_github(st.session_state.app_data); st.rerun()




