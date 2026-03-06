import streamlit as st
import pandas as pd
from datetime import datetime
import json
import requests
import base64

# --- 1. ALAPÉRTELMEZETT PÁLYALISTA (GYÁRI ADATOK) ---
NEVEK_DEFAULT = ["mrky", "Radnom", "Nova"]

GT7_FULL = {
    "GT7 - World Circuits (Europe)": [
        "24 Heures du Mans (13.62 km)", "Autodromo Nazionale Monza (5.79 km)", "Brands Hatch GP (3.91 km)", 
        "Circuit de Barcelona-Catalunya GP (4.67 km)", "Circuit de Spa-Francorchamps (7.00 km)", 
        "Nürburgring 24h (25.37 km)", "Nürburgring Nordschleife (20.83 km)", "Red Bull Ring (4.31 km)",
        "Alsace Village (5.42 km)", "Dragon Trail Seaside (5.20 km)", "Lago Maggiore Full (5.80 km)"
    ],
    "GT7 - World Circuits (Americas)": [
        "Daytona Road Course (5.73 km)", "Interlagos (4.30 km)", "Laguna Seca (3.60 km)", 
        "Road Atlanta (4.08 km)", "Watkins Glen Long (5.55 km)", "Willow Springs (3.95 km)", 
        "Trial Mountain (3.98 km)", "Deep Forest (3.51 km)", "Grand Valley Highway 1 (5.10 km)"
    ],
    "GT7 - World Circuits (Asia-Oceania)": [
        "Fuji Speedway (4.56 km)", "Mount Panorama (6.21 km)", "Suzuka Full (5.80 km)", 
        "Tsukuba (2.04 km)", "High Speed Ring (4.00 km)", "Tokyo Central (4.40 km)", "Autopolis Full (4.67 km)"
    ]
}

DIRT_FULL = {
    "Argentina": ["Las Juntas (8.25 km)", "Valle de los puentes (7.98 km)", "El Condor (5.21 km)"],
    "Australia": ["Mount Kaye Pass (12.50 km)", "Chandlers Creek (12.34 km)"],
    "Finland": ["Kakaristo (15.04 km)", "Kotajärvi (12.42 km)", "Hamelahti (15.04 km)"],
    "Germany": ["Oberstein (11.67 km)", "Waldabstieg (5.39 km)"],
    "Greece": ["Anodou Farmakas (9.61 km)", "Koryfi Dafni (9.50 km)"],
    "Monaco": ["Col de Turini (9.84 km)", "Pra d’Alart (9.84 km)"],
    "New Zealand": ["Waimarama Point (16.08 km)", "Ocean Beach (11.48 km)"],
    "Scotland": ["Old Butterstone Muir (5.97 km)", "Glencastle Farm (5.25 km)"],
    "Spain": ["Centenera (10.57 km)", "Viñedos Dardenya (6.55 km)"],
    "USA": ["North Fork Pass (12.86 km)", "Hancock Creek (12.84 km)"],
    "Wales": ["Sweet Lamb (9.90 km)", "Bidno Moorland (4.81 km)"],
    "Sweden": ["Hamra (12.34 km)", "Älgsjön (7.35 km)"]
}

# --- 2. FELHŐ KEZELÉS (GITHUB API) ---
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

# Biztonsági háló az AttributeError ellen
if "config" not in st.session_state.app_data:
    st.session_state.app_data["config"] = {"nevek": NEVEK_DEFAULT, "jatekok": {"Gran Turismo 7": GT7_FULL, "Dirt Rally 2.0": DIRT_FULL}}

st.set_page_config(page_title="SimRacing Arena ULTIMATE", layout="wide")

# --- CSS STÍLUSOK ---
st.markdown("""
<style>
    .card { padding: 15px; border-radius: 12px; margin-bottom: 10px; border: 4px solid #555; text-align: center; }
    .gold { border-color: #FFD700 !important; background-color: #3d3500; }
    .silver { border-color: #C0C0C0 !important; background-color: #2e2e2e; }
    .bronze { border-color: #CD7F32 !important; background-color: #331a00; }
    .track-row { background: #1e1e1e; padding: 10px; border-radius: 8px; margin-top: 5px; border: 1px solid #333; }
</style>
""", unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["🏁 ÚJ IDŐ", "🏆 TABELLA", "⚙️ ADMIN"])

# --- TAB 1: ÚJ IDŐ ---
with t1:
    conf = st.session_state.app_data["config"]
    sel_jatek = st.selectbox("Játék", list(conf["jatekok"].keys()))
    kat_dict = conf["jatekok"][sel_jatek]
    
    if kat_dict:
        sel_kat = st.selectbox("Kategória / Ország", sorted(list(kat_dict.keys())))
        sel_palya = st.selectbox("Pálya / Szakasz", sorted(kat_dict[sel_kat]))

        with st.form("entry", clear_on_submit=True):
            auto = st.text_input("Használt autó")
            nev = st.selectbox("Versenyző", conf["nevek"])
            ido = st.text_input("Idő (p:mp.ezred)", placeholder="pl. 1:24.500")
            if st.form_submit_button("💾 MENTÉS A FELHŐBE"):
                try:
                    p, mp = ido.split(":")
                    total = int(p) * 60 + float(mp)
                    new_row = {
                        "Dátum": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Játék": sel_jatek, "Kategória": sel_kat, "Pálya": sel_palya,
                        "Autó": auto, "Versenyző": nev, "Másodperc": total, "Idő": ido
                    }
                    st.session_state.app_data["results"].append(new_row)
                    if save_to_github(st.session_state.app_data):
                        st.success("Sikeres mentés a GitHub-ra!")
                        st.rerun()
                    else: st.error("Hiba a mentés során!")
                except: st.error("Hibás formátum! (p:mp.ezred)")
    else:
        st.warning("Nincsenek kategóriák ehhez a játékhoz. Add meg őket az Adminban!")

# --- TAB 2: TABELLA ---
with t2:
    results_list = st.session_state.app_data["results"]
    df = pd.DataFrame(results_list)
    
    if not df.empty:
        j_sel = st.selectbox("Játék választása", list(conf["jatekok"].keys()), key="tab_j")
        st.subheader(f"🥇 {j_sel} Ranglista")
        df_f = df[df["Játék"] == j_sel]
        
        pts = {n: 0 for n in conf["nevek"]}
        if not df_f.empty:
            best_times = df_f.loc[df_f.groupby(["Pálya", "Versenyző"])["Másodperc"].idxmin()]
            for track in best_times["Pálya"].unique():
                track_res = best_times[best_times["Pálya"] == track].sort_values("Másodperc").head(3)
                for i, (_, row) in enumerate(track_res.iterrows()):
                    if row["Versenyző"] in pts: pts[row["Versenyző"]] += (3 if i == 0 else 2 if i == 1 else 1)
        
        sorted_pts = sorted(pts.items(), key=lambda x: x[1], reverse=True)
        cols = st.columns(len(sorted_pts) if len(sorted_pts) > 0 else 1)
        for idx, (name, score) in enumerate(sorted_pts):
            style = "gold" if idx == 0 else "silver" if idx == 1 else "bronze" if idx == 2 else ""
            with cols[idx]:
                st.markdown(f'<div class="card {style}"><h2>{"🥇" if idx==0 else "🥈" if idx==1 else "🥉" if idx==2 else "#"+str(idx+1)}</h2><b>{name.upper()}</b><br>{score} pont</div>', unsafe_allow_html=True)
        
        st.divider()
        st.subheader("📍 Pálya Rangsorok")
        all_tr = sorted(df_f["Pálya"].unique())
        if all_tr:
            p_sel = st.selectbox("Válassz pályát", all_tr)
            t_df = df_f[df_f["Pálya"] == p_sel].sort_values("Másodperc")
            t_df = t_df.loc[t_df.groupby("Versenyző")["Másodperc"].idxmin()].sort_values("Másodperc")
            for i, (_, r) in enumerate(t_df.iterrows(), 1):
                st.markdown(f'<div class="track-row">{i}. <b>{r["Versenyző"]}</b>: {r["Idő"]} <small>({r["Autó"]})</small></div>', unsafe_allow_html=True)
    else:
        st.info("Még nincs rögzített adat.")

# --- TAB 3: BŐVÍTETT ADMIN ---
with t3:
    st.header("⚙️ Adminisztráció")
    if st.button("🔄 ADATOK FRISSÍTÉSE A GITHUBRÓL"):
        st.session_state.app_data = load_from_github()
        st.rerun()

    # --- VERSENYZŐK ---
    st.subheader("👤 Versenyzők kezelése")
    v1, v2, v3 = st.columns(3)
    with v1:
        new_v = st.text_input("Új versenyző neve")
        if st.button("Hozzáadás"):
            if new_v and new_v not in st.session_state.app_data["config"]["nevek"]:
                st.session_state.app_data["config"]["nevek"].append(new_v)
                save_to_github(st.session_state.app_data)
                st.rerun()
    with v2:
        mod_v_old = st.selectbox("Név módosítása", st.session_state.app_data["config"]["nevek"])
        mod_v_new = st.text_input("Új név")
        if st.button("Átnevezés"):
            idx = st.session_state.app_data["config"]["nevek"].index(mod_v_old)
            st.session_state.app_data["config"]["nevek"][idx] = mod_v_new
            save_to_github(st.session_state.app_data)
            st.rerun()
    with v3:
        del_v = st.selectbox("Versenyző törlése", st.session_state.app_data["config"]["nevek"])
        if st.button("Törlés", type="primary"):
            st.session_state.app_data["config"]["nevek"].remove(del_v)
            save_to_github(st.session_state.app_data)
            st.rerun()

    st.divider()

    # --- JÁTÉKOK ÉS PÁLYÁK ---
    st.subheader("🎮 Játékok és Pályák szerkesztése")
    adm_j_list = list(st.session_state.app_data["config"]["jatekok"].keys())
    sel_j_adm = st.selectbox("Szerkesztett játék", adm_j_list)

    c1, c2 = st.columns(2)
    with c1:
        new_g = st.text_input("Új játék hozzáadása")
        if st.button("Játék mentése"):
            st.session_state.app_data["config"]["jatekok"][new_g] = {}
            save_to_github(st.session_state.app_data)
            st.rerun()
    with c2:
        if st.button("Kijelölt játék TÖRLÉSE", type="primary"):
            del st.session_state.app_data["config"]["jatekok"][sel_j_adm]
            save_to_github(st.session_state.app_data)
            st.rerun()

    st.divider()
    
    # Kategóriák és Pályák
    k1, k2 = st.columns(2)
    with k1:
        st.write(f"**{sel_j_adm}** kategóriái")
        new_k = st.text_input("Új kategória (pl. Ország)")
        if st.button("Kategória hozzáadása"):
            st.session_state.app_data["config"]["jatekok"][sel_j_adm][new_k] = []
            save_to_github(st.session_state.app_data)
            st.rerun()
        
        kat_list = list(st.session_state.app_data["config"]["jatekok"][sel_j_adm].keys())
        if kat_list:
            del_k = st.selectbox("Kategória törlése", kat_list)
            if st.button("Kategória és összes pályájának törlése", type="primary"):
                del st.session_state.app_data["config"]["jatekok"][sel_j_adm][del_k]
                save_to_github(st.session_state.app_data)
                st.rerun()

    with k2:
        if kat_list:
            sel_k_adm = st.selectbox("Válassz kategóriát a pályákhoz", kat_list)
            new_p = st.text_input("Új pálya neve")
            if st.button("Pálya hozzáadása"):
                st.session_state.app_data["config"]["jatekok"][sel_j_adm][sel_k_adm].append(new_p)
                save_to_github(st.session_state.app_data)
                st.rerun()
            
            p_list_adm = st.session_state.app_data["config"]["jatekok"][sel_j_adm][sel_k_adm]
            if p_list_adm:
                del_p = st.selectbox("Pálya törlése", sorted(p_list_adm))
                if st.button("Pálya törlése", type="primary"):
                    st.session_state.app_data["config"]["jatekok"][sel_j_adm][sel_k_adm].remove(del_p)
                    save_to_github(st.session_state.app_data)
                    st.rerun()

    st.divider()
    if st.button("⚠️ GYÁRI BEÁLLÍTÁSOK VISSZAÁLLÍTÁSA (Pályák és nevek alaphelyzet)"):
        st.session_state.app_data["config"] = {"nevek": NEVEK_DEFAULT, "jatekok": {"Gran Turismo 7": GT7_FULL, "Dirt Rally 2.0": DIRT_FULL}}
        save_to_github(st.session_state.app_data)
        st.rerun()
    
    if st.button("🚨 ÖSSZES EREDMÉNY TÖRLÉSE (VÉGLEGES)", type="primary"):
        st.session_state.app_data["results"] = []
        save_to_github(st.session_state.app_data)
        st.rerun()
