import streamlit as st
import pandas as pd
from datetime import datetime
import json
import requests
import base64

# --- 1. ALAPÉRTELMEZETT PÁLYALISTA ---
NEVEK_DEFAULT = ["mrky", "Radnom", "Nova"]

GT7_FULL = {
    "GT7 - World Circuits (Europe)": ["24 Heures du Mans (13.62 km)", "Autodromo Nazionale Monza (5.79 km)", "Circuit de Spa-Francorchamps (7.00 km)", "Nürburgring 24h (25.37 km)", "Red Bull Ring (4.31 km)"],
    "GT7 - World Circuits (Americas)": ["Daytona Road Course (5.73 km)", "Interlagos (4.30 km)", "Laguna Seca (3.60 km)", "Watkins Glen Long (5.55 km)"],
    "GT7 - World Circuits (Asia-Oceania)": ["Mount Panorama (6.21 km)", "Suzuka Full (5.80 km)", "Tsukuba (2.04 km)"]
}

DIRT_FULL = {
    "Argentina": ["Las Juntas (8.25 km)", "El Condor (5.21 km)"],
    "Finland": ["Kakaristo (15.04 km)", "Kotajärvi (12.42 km)"],
    "Wales": ["Sweet Lamb (9.90 km)", "Bidno Moorland (4.81 km)"]
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
    st.header("⚙️ Adminisztráció")
    if st.button("🔄 ADATOK FRISSÍTÉSE GITHUBRÓL"):
        st.session_state.app_data = load_from_github()
        st.rerun()

    st.subheader("👤 Versenyzők")
    c1, c2, c3 = st.columns(3)
    with c1:
        new_v = st.text_input("Új versenyző")
        if st.button("Hozzáadás"):
            st.session_state.app_data["config"]["nevek"].append(new_v)
            save_to_github(st.session_state.app_data); st.rerun()
    with c2:
        mod_old = st.selectbox("Módosítandó név", st.session_state.app_data["config"]["nevek"])
        mod_new = st.text_input("Új név")
        if st.button("Átnevezés"):
            idx = st.session_state.app_data["config"]["nevek"].index(mod_old)
            st.session_state.app_data["config"]["nevek"][idx] = mod_new
            save_to_github(st.session_state.app_data); st.rerun()
    with c3:
        del_v = st.selectbox("Törlendő név", st.session_state.app_data["config"]["nevek"])
        if st.button("Törlés", type="primary"):
            st.session_state.app_data["config"]["nevek"].remove(del_v)
            save_to_github(st.session_state.app_data); st.rerun()

    st.divider()
    st.subheader("🎮 Játékok és Pályák")
    sel_j = st.selectbox("Szerkesztett játék", list(st.session_state.app_data["config"]["jatekok"].keys()))
    
    col_j1, col_j2 = st.columns(2)
    with col_j1:
        new_k = st.text_input("Új kategória")
        if st.button("Kategória mentése"):
            st.session_state.app_data["config"]["jatekok"][sel_j][new_k] = []
            save_to_github(st.session_state.app_data); st.rerun()
    with col_j2:
        kat_list = list(st.session_state.app_data["config"]["jatekok"][sel_j].keys())
        if kat_list:
            sel_k_p = st.selectbox("Válassz kategóriát pályához", kat_list)
            new_p = st.text_input("Új pálya neve")
            if st.button("Pálya mentése"):
                st.session_state.app_data["config"]["jatekok"][sel_j][sel_k_p].append(new_p)
                save_to_github(st.session_state.app_data); st.rerun()

    if st.button("🚨 ÖSSZES EREDMÉNY TÖRLÉSE", type="primary"):
        st.session_state.app_data["results"] = []
        save_to_github(st.session_state.app_data); st.rerun()

