import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Konfigurasi Halaman Website Tema Princess
st.set_page_config(page_title="Dashboard Penerimaan", page_icon="🎀", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFF0F5; }
    h1, h2, h3, p, div { color: #C71585 !important; font-family: 'Georgia', serif; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎀 Dashboard Realisasi RK Harian (Google Sheets) 👑")
st.markdown("✨ **Terhubung langsung secara real-time dengan Google Sheets kantor!** ✨")
st.write("---")

# Pilihan Jenis Pajak
jenis_pajak = st.selectbox(
    "💖 Silakan Pilih Jenis Pajak:",
    ("Pajak Air Tanah", "PBB")
)

# Fungsi Ambil Data dari Google Sheets via CSV Link
@st.cache_data(ttl=30) # Data otomatis diperbarui setiap 30 detik
def load_google_sheet(sheet_name):
    # Masukkan link CSV publik Google Sheet kamu di sini
    # Contoh format link publish to web CSV dari Google Sheet:
    # https://docs.google.com/spreadsheets/d/ID_SPREADSHEET_KAMU/export?format=csv&sheet=NamaSheet
    
    base_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQv4f0nx-O0qpFrfhCAG4Si4QdZMVEzE0ne1FIKgKN-LBs9O80vAQ1ZLZ0KrTOWPX8GXk7LK6H-t2Ed/pub?output=csv"
    url = base_url + sheet_name.replace(" ", "%20")
    
    try:
        df = pd.read_csv(url)
        df['Agustus_2026'] = pd.to_numeric(df['Agustus_2026'], errors='coerce').fillna(0)
        df['September_2026'] = pd.to_numeric(df['September_2026'], errors='coerce').fillna(0)
        return df
    except Exception as e:
        # Data cadangan jika link belum diatur agar tidak error
        return pd.DataFrame({
            'Tanggal': ['01', '02', '03'],
            'Agustus_2026': [13403634, 12964578, 242498394],
            'September_2026': [198523106, 0, 0]
        })

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

fig.add_trace(go.Scatter(
    x=x_tanggal, y=df['September_2026'] + (df['September_2026'].max() * 0.05),
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

st.write("### 📝 Tabel Rincian Data (Live dari Google Sheets)")
st.dataframe(df.style.format({
    'Agustus_2026': 'Rp {:,.0f}',
    'September_2026': 'Rp {:,.0f}'
}))