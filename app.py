import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Konfigurasi Halaman Website Tema Princess
st.set_page_config(page_title="Dashboard Penerimaan", page_icon="🎀", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFF0F5; }
    h1, h2, h3, p, div { color: #C71585 !important; font-family: 'Georgia', serif; }
    .stButton>button { background-color: #FFB6C1; color: #C71585; border-radius: 10px; border: 1px solid #FF1493; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎀 Dashboard Realisasi RK Harian (Google Sheets) 👑")
st.markdown("✨ **Terhubung langsung secara real-time dengan Google Sheets kantor!** ✨")
st.write("---")

# Tombol Refresh untuk membersihkan cache memori data lama
col_btn1, col_btn2 = st.columns([1, 4])
with col_btn1:
    if st.button("🔄 Segarkan Data"):
        st.cache_data.clear()
        st.rerun()

# Pilihan Jenis Pajak
jenis_pajak = st.selectbox(
    "💖 Silakan Pilih Jenis Pajak:",
    ("Pajak Air Tanah", "PBB")
)

# Fungsi Ambil Data Murni dari Google Sheets & Pembersih Format Angka Indonesia
@st.cache_data(ttl=10)
def load_google_sheet(sheet_name):
    if sheet_name == "Pajak Air Tanah":
        url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQv4f0nx-O0qpFrfhCAG4Si4QdZMVEzE0ne1FIKgKN-LBs9O80vAQ1ZLZ0KrTOWPX8GXk7LK6H-t2Ed/pub?gid=0&single=true&output=csv"
    else:
        url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQv4f0nx-O0qpFrfhCAG4Si4QdZMVEzE0ne1FIKgKN-LBs9O80vAQ1ZLZ0KrTOWPX8GXk7LK6H-t2Ed/pub?gid=1312799199&single=true&output=csv"
    
    df = pd.read_csv(url)
    
    # Membersihkan format titik ribuan dan koma desimal khas Indonesia (contoh: "13.403.634,00")
    for col in ['Agustus_2026', 'September_2026']:
        if col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    return df

# Memuat data sesuai pilihan pajak
df = load_google_sheet(jenis_pajak)

# Membuat Grafik Interaktif Plotly
fig = go.Figure()
x_tanggal = df['Tanggal'].astype(str).str[:10]

# Bar Agustus
fig.add_trace(go.Bar(
    x=x_tanggal, y=df['Agustus_2026'], name='Agustus 2026',
    marker_color='#FFB6C1', marker_line_color='#FF1493', marker_line_width=1.5,
    hovertemplate="<b>Agustus:</b> Rp %{y:,.0f}<extra></extra>"
))

# Bar September (Hanya tampil jika ada isinya)
fig.add_trace(go.Bar(
    x=x_tanggal, y=df['September_2026'], name='September 2026',
    marker_color='#FF69B4', marker_line_color='#C71585', marker_line_width=1.5,
    hovertemplate="<b>September:</b> Rp %{y:,.0f}<extra></extra>"
))

# Logika Emoji Ceria / Sedih
kenaikan_text = []
for index, row in df.iterrows():
    if row['September_2026'] > 0:
        if row['September_2026'] > row['Agustus_2026']:
            kenaikan_text.append('🥳💖 Naik!')
        elif row['September_2026'] < row['Agustus_2026']:
            kenaikan_text.append('😭☔ Turun')
        else:
            kenaikan_text.append('😶 Tetap')
    else:
        kenaikan_text.append('')

max_val = max(df['Agustus_2026'].max(), df['September_2026'].max())
fig.add_trace(go.Scatter(
    x=x_tanggal, y=df['September_2026'] + (max_val * 0.05 if max_val > 0 else 10),
    text=kenaikan_text, mode='text', textfont=dict(size=14, color='#C71585'),
    showlegend=False, hoverinfo='skip'
))

fig.update_layout(
    barmode='group', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(255,255,255,0.5)',
    title=dict(text=f"Grafik Realisasi: {jenis_pajak}", font=dict(size=20, color='#C71585')),
    xaxis=dict(title='Tanggal', tickfont=dict(color='#C71585')),
    yaxis=dict(title='Jumlah Realisasi (Rp)', tickfont=dict(color='#C71585')),
    legend=dict(bgcolor='#FFF0F5', bordercolor='#FF1493', borderwidth=1),
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

# Kotak Rangkuman Total Akumulasi Sebulan
total_agus = df['Agustus_2026'].sum()
total_sept = df['September_2026'].sum()

col1, col2 = st.columns(2)
col1.metric("🎀 Total Realisasi Agustus", f"Rp {total_agus:,.0f}".replace(',', '.'))
col2.metric("👑 Total Realisasi September", f"Rp {total_sept:,.0f}".replace(',', '.'))

st.write("---")
st.write("### 📝 Tabel Rincian Data (Live dari Google Sheets)")
st.dataframe(df.style.format({
    'Agustus_2026': 'Rp {:,.0f}',
    'September_2026': 'Rp {:,.0f}'
}))
