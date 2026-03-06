import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import json

# --- 1. ALAPADATOK (HA ÜRES A TÁBLÁZAT) ---
NEVEK_DEFAULT = ["mrky", "Radnom", "Nova"]

# (Itt a teljes GT7_FULL és DIRT_FULL adatbázisod, amit korábban használtunk)
# ... [A 300+ pálya listája változatlanul marad a kódban] ...

# --- 2. FELHŐ KAPCSOLÓDÁS ---
st.set_page_config(page_title="SimRacing Arena CLOUD v37", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

def load_all_data():
    try:
        res = conn.read(worksheet="results", ttl="0s")
        # Megpróbáljuk beolvasni a mentett konfigot (nevek, egyedi pályák)
        conf = conn.read(worksheet="config", ttl="0s")
        return res, conf
    except:
        return pd.DataFrame(columns=["Dátum", "Játék", "Kategória", "Pálya", "Autó", "Versenyző", "Másodperc", "Idő"]), None

# Adatok betöltése
if 'results' not in st.session_state:
    res_df, conf_df = load_all_data()
    st.session_state.results = res_df
    
    # Ha van mentett konfig a Google-ben, azt használjuk, ha nincs, az alapértelmezettet
    if conf_df is not None and not conf_df.empty:
        st.session_state.config = json.loads(conf_df.iloc[0,0])
    else:
        st.session_state.config = {"nevek": NEVEK_DEFAULT, "jatekok": {"Gran Turismo 7": GT7_FULL, "Dirt Rally 2.0": DIRT_FULL}}

def sync_config():
    # Elmentjük a teljes beállítást (nevek, játékok, pályák) a Google 'config' fülére
    conf_json = json.dumps(st.session_state.config, ensure_ascii=False)
    df_conf = pd.DataFrame([{"data": conf_json}])
    conn.update(worksheet="config", data=df_conf)

def sync_results():
    conn.update(worksheet="results", data=st.session_state.results)

# --- 3. MEGJELENÉS (CSS ÉS TABOK) ---
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

# --- ÚJ IDŐ (Változatlan logika, de felhőbe ment) ---
with t1:
    # ... [Idő rögzítő felület] ...
    if st.form_submit_button("💾 MENTÉS A FELHŐBE"):
        # ... [Adat hozzáadása] ...
        sync_results()
        st.success("Idő szinkronizálva a Google Drive-val!")

# --- TABELLA (Érmekkel és Rangsorral) ---
with t2:
    # ... [Ranglista és medálok megjelenítése] ...

# --- BŐVÍTETT ADMIN (Módosítások mentésével) ---
with t3:
    st.header("⚙️ Rendszerkezelés")
    
    # VERSENYZŐK KEZELÉSE
    st.subheader("👥 Versenyzők")
    v1, v2, v3 = st.columns(3)
    with v1:
        new_v = st.text_input("Új versenyző")
        if st.button("Hozzáadás"):
            if new_v:
                st.session_state.config["nevek"].append(new_v)
                sync_config() # MENTÉS A FELHŐBE
                st.rerun()
    with v2:
        mod_v_old = st.selectbox("Név módosítása", st.session_state.config["nevek"])
        mod_v_new = st.text_input("Új név erre")
        if st.button("Átnevezés"):
            idx = st.session_state.config["nevek"].index(mod_v_old)
            st.session_state.config["nevek"][idx] = mod_v_new
            sync_config() # MENTÉS A FELHŐBE
            st.rerun()
    with v3:
        del_v = st.selectbox("Törlés", st.session_state.config["nevek"])
        if st.button("Törlés", type="primary"):
            st.session_state.config["nevek"].remove(del_v)
            sync_config() # MENTÉS A FELHŐBE
            st.rerun()

    st.divider()

    # JÁTÉKOK ÉS PÁLYÁK KEZELÉSE
    st.subheader("🎮 Játékok és Pályák")
    j1, j2, j3 = st.columns(3)
    # ... [Itt a korábbi játék hozzáadó/törlő/módosító kód] ...
    # FONTOS: Minden gomb után ott van a sync_config() hívás!

    if st.button("⚠️ GYÁRI PÁLYALISTA VISSZAÁLLÍTÁSA"):
        st.session_state.config = {"nevek": st.session_state.config["nevek"], "jatekok": {"Gran Turismo 7": GT7_FULL, "Dirt Rally 2.0": DIRT_FULL}}
        sync_config()
        st.rerun()
