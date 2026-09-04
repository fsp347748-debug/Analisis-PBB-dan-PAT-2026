import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Konfigurasi Halaman Website Tema Princess
st.set_page_config(page_title="Dashboard Rekap Penerimaan Pajak", page_icon="🎀", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFF0F5; }
    h1, h2, h3, p, div { color: #C71585 !important; font-family: 'Georgia', serif; }
    .stButton>button { background-color: #FFB6C1; color: #C71585; border-radius: 10px; border: 1px solid #FF1493; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎀 Dashboard Rekapitulasi Penerimaan Pajak 👑")
st.markdown("✨ **Analisis Perbandingan Realisasi Agustus vs September 2026** ✨")
st.write("---")

# Tombol Refresh untuk membersihkan cache memori data lama
col_btn1, col_btn2 = st.columns([1, 4])
with col_btn1:
    if st.button("🔄 Segarkan Data"):
        st.cache_data.clear()
        st.rerun()

# Fungsi Pembersih Angka Format Indonesia dari Google Sheets
def clean_numeric_columns(df, cols):
    for col in cols:
        if col in df.columns:
            df[col] = (
                df[col].astype(str)
                .str.replace('.', '', regex=False)
                .str.replace(',', '', regex=False)
            )
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

# URL Publish to Web dari Google Sheets Kamu
# Pastikan spreadsheet kamu memiliki 3 tab: "Rekap Pajak", "Pajak Air Tanah", dan "PBB"
@st.cache_data(ttl=10)
def load_all_data():
    # Ganti link di bawah ini dengan link CSV Publish to Web Google Sheet kamu
    base_id_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQv4f0nx-O0qpFrfhCAG4Si4QdZMVEzE0ne1FIKgKN-LBs9O80vAQ1ZLZ0KrTOWPX8GXk7LK6H-t2Ed/pub?output=csv"
    
    # Sesuaikan GID untuk masing-masing Sheet
    gid_rekap = "0"          # Ganti dengan GID sheet "Rekap Pajak"
    gid_air_tanah = "123456" # Ganti dengan GID sheet "Pajak Air Tanah"
    gid_pbb = "789012"       # Ganti dengan GID sheet "PBB"
    
    try:
        df_rekap = pd.read_csv(base_id_url + gid_rekap)
        df_rekap = clean_numeric_columns(df_rekap, ['Agustus_2026', 'September_2026'])
    except:
        # Data cadangan Rekap jika link belum diatur
        df_rekap = pd.DataFrame({
            'Jenis Pajak': ['Pajak Air Tanah', 'PBB'],
            'Agustus_2026': [268866606, 420000000],
            'September_2026': [835178310, 198040000]
        })
        
    try:
        df_air = pd.read_csv(base_id_url + gid_air_tanah)
        df_air = clean_numeric_columns(df_air, ['Agustus_2026', 'September_2026'])
    except:
        df_air = pd.DataFrame(columns=['Tanggal', 'Agustus_2026', 'September_2026'])
        
    try:
        df_pbb = pd.read_csv(base_id_url + gid_pbb)
        df_pbb = clean_numeric_columns(df_pbb, ['Agustus_2026', 'September_2026'])
    except:
        df_pbb = pd.DataFrame(columns=['Tanggal', 'Agustus_2026', 'September_2026'])
        
    return df_rekap, df_air, df_pbb

df_rekap, df_air, df_pbb = load_all_data()

# ==========================================
# 1. BAGIAN ATAS: DIAGRAM BATANG REKAP PAJAK
# ==========================================
st.subheader("📊 Grafik Rekapitulasi per Jenis Pajak")

fig = go.Figure()
x_jenis = df_rekap['Jenis Pajak']

# Bar Agustus
fig.add_trace(go.Bar(
    x=x_jenis, y=df_rekap['Agustus_2026'], name='Agustus 2026',
    marker_color='#FFB6C1', marker_line_color='#FF1493', marker_line_width=1.5,
    hovertemplate="<b>Agustus:</b> Rp %{y:,.0f}<extra></extra>"
))

# Bar September
fig.add_trace(go.Bar(
    x=x_jenis, y=df_rekap['September_2026'], name='September 2026',
    marker_color='#FF69B4', marker_line_color='#C71585', marker_line_width=1.5,
    hovertemplate="<b>September:</b> Rp %{y:,.0f}<extra></extra>"
))

# Logika Hitung Selisih Naik/Turun & Emoji di atas Bar
selisih_text = []
for index, row in df_rekap.iterrows():
    agus = row['Agustus_2026']
    sept = row['September_2026']
    selisih = sept - agus
    
    if sept > 0:
        format_selisih = f"Rp {abs(selisih):,.0f}".replace(',', '.')
        if selisih > 0:
            selisih_text.append(f"🥳💖 Naik\n+{format_selisih}")
        elif selisih < 0:
            selisih_text.append(f"😭☔ Turun\n-{format_selisih}")
        else:
            selisih_text.append("😶 Tetap")
    else:
        selisih_text.append("")

max_val = max(df_rekap['Agustus_2026'].max(), df_rekap['September_2026'].max())
fig.add_trace(go.Scatter(
    x=x_jenis, y=df_rekap['September_2026'] + (max_val * 0.08 if max_val > 0 else 10),
    text=selisih_text, mode='text', textfont=dict(size=12, color='#C71585'),
    showlegend=False, hoverinfo='skip'
))

fig.update_layout(
    barmode='group', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(255,255,255,0.5)',
    title=dict(text="Total Penerimaan: Agustus vs September 2026", font=dict(size=18, color='#C71585')),
    xaxis=dict(title='Jenis Pajak', tickfont=dict(color='#C71585'), type='category'),
    yaxis=dict(title='Jumlah Total (Rp)', tickfont=dict(color='#C71585')),
    legend=dict(bgcolor='#FFF0F5', bordercolor='#FF1493', borderwidth=1),
    hovermode="x unified",
    margin=dict(t=60, b=40)
)

st.plotly_chart(fig, use_container_width=True)

# Kotak Metrik Total Keseluruhan
total_all_agus = df_rekap['Agustus_2026'].sum()
total_all_sept = df_rekap['September_2026'].sum()

m1, m2 = st.columns(2)
m1.metric("🎀 Total Keseluruhan Agustus", f"Rp {total_all_agus:,.0f}".replace(',', '.'))
m2.metric("👑 Total Keseluruhan September", f"Rp {total_all_sept:,.0f}".replace(',', '.'))

st.write("---")

# ==========================================
# 2. BAGIAN BAWAH: RINCIAN HARIAN PER TAB
# ==========================================
st.subheader("📋 Rincian Harian per Tanggal")

tab1, tab2 = st.tabs(["💧 Pajak Air Tanah", "🏡 PBB"])

with tab1:
    st.write("#### Rincian Harian Pajak Air Tanah")
    if not df_air.empty:
        st.dataframe(df_air.style.format({
            'Agustus_2026': 'Rp {:,.0f}',
            'September_2026': 'Rp {:,.0f}'
        }), use_container_width=True)
    else:
        st.info("Belum ada data harian untuk Pajak Air Tanah.")

with tab2:
    st.write("#### Rincian Harian PBB")
    if not df_pbb.empty:
        st.dataframe(df_pbb.style.format({
            'Agustus_2026': 'Rp {:,.0f}',
            'September_2026': 'Rp {:,.0f}'
        }), use_container_width=True)
    else:
        st.info("Belum ada data harian untuk PBB.")
