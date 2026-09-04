import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Konfigurasi Halaman Website Tema Princess
st.set_page_config(page_title="Dashboard Analisis Insentif Fiskal", page_icon="🎀", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFF0F5; }
    h1, h2, h3, p, div { color: #C71585 !important; font-family: 'Georgia', serif; }
    .stButton>button { background-color: #FFB6C1; color: #C71585; border-radius: 10px; border: 1px solid #FF1493; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎀 Dashboard Analisis Dampak Insentif Fiskal 👑")
st.markdown("✨ **Evaluasi Perbandingan Penerimaan & Kepatuhan Wajib Pajak (Agustus vs September 2026)** ✨")
st.write("---")

# Tombol Refresh Cache
col_btn1, col_btn2 = st.columns([1, 4])
with col_btn1:
    if st.button("🔄 Segarkan Data"):
        st.cache_data.clear()
        st.rerun()

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

@st.cache_data(ttl=10)
def load_all_data():
    url_rekap = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQv4f0nx-O0qpFrfhCAG4Si4QdZMVEzE0ne1FIKgKN-LBs9O80vAQ1ZLZ0KrTOWPX8GXk7LK6H-t2Ed/pub?gid=0&single=true&output=csv"
    url_air = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQv4f0nx-O0qpFrfhCAG4Si4QdZMVEzE0ne1FIKgKN-LBs9O80vAQ1ZLZ0KrTOWPX8GXk7LK6H-t2Ed/pub?gid=589514798&single=true&output=csv"
    url_pbb = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQv4f0nx-O0qpFrfhCAG4Si4QdZMVEzE0ne1FIKgKN-LBs9O80vAQ1ZLZ0KrTOWPX8GXk7LK6H-t2Ed/pub?gid=1312799199&single=true&output=csv"
    url_seg_air = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQv4f0nx-O0qpFrfhCAG4Si4QdZMVEzE0ne1FIKgKN-LBs9O80vAQ1ZLZ0KrTOWPX8GXk7LK6H-t2Ed/pub?gid=1692042397&single=true&output=csv"
    url_seg_pbb = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQv4f0nx-O0qpFrfhCAG4Si4QdZMVEzE0ne1FIKgKN-LBs9O80vAQ1ZLZ0KrTOWPX8GXk7LK6H-t2Ed/pub?gid=349029387&single=true&output=csv"
    
    nama_hari = {
        'Monday': 'Senin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu',
        'Thursday': 'Kamis', 'Friday': 'Jumat', 'Saturday': 'Sabtu', 'Sunday': 'Minggu'
    }

    def process_daily_df(url):
        try:
            df = pd.read_csv(url)
            df = clean_numeric_columns(df, ['Agustus_2026', 'September_2026'])
            
            if 'Tanggal' in df.columns:
                dt_agus = pd.to_datetime(df['Tanggal'].astype(str) + '-08-2026', format='%d-%m-%Y', errors='coerce')
                dt_sept = pd.to_datetime(df['Tanggal'].astype(str) + '-09-2026', format='%d-%m-%Y', errors='coerce')
                
                df['Hari_Agustus'] = dt_agus.dt.day_name().map(nama_hari).fillna('')
                df['Hari_September'] = dt_sept.dt.day_name().map(nama_hari).fillna('')
                
                cols = ['Tanggal', 'Hari_Agustus', 'Agustus_2026', 'Hari_September', 'September_2026']
                other_cols = [c for c in df.columns if c not in cols]
                df = df[cols + other_cols]
            return df
        except:
            return pd.DataFrame(columns=['Tanggal', 'Hari_Agustus', 'Agustus_2026', 'Hari_September', 'September_2026'])

    try:
        df_rekap = pd.read_csv(url_rekap)
        df_rekap = clean_numeric_columns(df_rekap, ['Agustus_2026', 'September_2026'])
    except:
        df_rekap = pd.DataFrame({
            'Jenis Pajak': ['Pajak Air Tanah', 'PBB'],
            'Agustus_2026': [268866606, 420000000],
            'September_2026': [835178310, 198040000]
        })
        
    df_air = process_daily_df(url_air)
    df_pbb = process_daily_df(url_pbb)
    df_seg_air = process_daily_df(url_seg_air)
    df_seg_pbb = process_daily_df(url_seg_pbb)
        
    return df_rekap, df_air, df_pbb, df_seg_air, df_seg_pbb

df_rekap, df_air, df_pbb, df_seg_air, df_seg_pbb = load_all_data()

# ==========================================
# 1. KARTU KINERJA UTAMA (KPI)
# ==========================================
total_agus = df_rekap['Agustus_2026'].sum()
total_sept = df_rekap['September_2026'].sum()
selisih_total = total_sept - total_agus
persen_tumbuh = (selisih_total / total_agus * 100) if total_agus > 0 else 0

st.subheader("📈 Ringkasan Eksekutif Dampak Kebijakan")
col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
col_kpi1.metric("🎀 Total Agustus (Tanpa Insentif)", f"Rp {total_agus:,.0f}".replace(',', '.'))
col_kpi2.metric("👑 Total September (Dengan Insentif)", f"Rp {total_sept:,.0f}".replace(',', '.'), f"{persen_tumbuh:+.1f}% dari Agustus")
col_kpi3.metric("⚖️ Selisih Pertumbuhan Absolut", f"Rp {selisih_total:,.0f}".replace(',', '.'))

# ==========================================
# 1.5 ANALISIS APPLE-TO-APPLE (HARI KERJA / WORKDAYS)
# ==========================================
st.subheader("🏛️ Analisis Apple-to-Apple: Normalisasi Hari Kerja")
hari_kerja_agus = 21 
hari_kerja_sept = 22

avg_workday_agus = total_agus / hari_kerja_agus
avg_workday_sept = total_sept / hari_kerja_sept
growth_workday = ((avg_workday_sept - avg_workday_agus) / avg_workday_agus * 100) if avg_workday_agus > 0 else 0

col_w1, col_w2, col_w3 = st.columns(3)
col_w1.metric("📅 Rata-rata/Hari Kerja Agustus", f"Rp {avg_workday_agus:,.0f}".replace(',', '.'))
col_w2.metric("📅 Rata-rata/Hari Kerja September", f"Rp {avg_workday_sept:,.0f}".replace(',', '.'), f"{growth_workday:+.1f}% per Hari Kerja")
col_w3.metric("💡 Indikator Perbandingan", "Apple-to-Apple (Normalisasi Workday)")
st.write("---")

# ==========================================
# 2. DIAGRAM BATANG REKAP & SELISIH
# ==========================================
st.subheader("📊 Grafik Perbandingan Total Penerimaan per Jenis Pajak")

fig = go.Figure()
x_jenis = df_rekap['Jenis Pajak']

fig.add_trace(go.Bar(
    x=x_jenis, y=df_rekap['Agustus_2026'], name='Agustus 2026 (Tanpa Insentif)',
    marker_color='#FFB6C1', marker_line_color='#FF1493', marker_line_width=1.5,
    hovertemplate="<b>Agustus:</b> Rp %{y:,.0f}<extra></extra>"
))

fig.add_trace(go.Bar(
    x=x_jenis, y=df_rekap['September_2026'], name='September 2026 (Berjalan Insentif)',
    marker_color='#FF69B4', marker_line_color='#C71585', marker_line_width=1.5,
    hovertemplate="<b>September:</b> Rp %{y:,.0f}<extra></extra>"
))

selisih_text = []
for index, row in df_rekap.iterrows():
    agus = row['Agustus_2026']
    sept = row['September_2026']
    selisih = sept - agus
    p_tumbuh = (selisih / agus * 100) if agus > 0 else 0
    
    if sept > 0:
        format_selisih = f"Rp {abs(selisih):,.0f}".replace(',', '.')
        if selisih > 0:
            selisih_text.append(f"🥳💖 Naik ({p_tumbuh:+.1f}%)\n+{format_selisih}")
        elif selisih < 0:
            selisih_text.append(f"😭☔ Turun ({p_tumbuh:+.1f}%)\n-{format_selisih}")
        else:
            selisih_text.append("😶 Tetap (0%)")
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
    title=dict(text="Dampak Kebijakan Insentif Fiskal terhadap Pendapatan Daerah", font=dict(size=18, color='#C71585')),
    xaxis=dict(title='Jenis Pajak', tickfont=dict(color='#C71585'), type='category'),
    yaxis=dict(title='Jumlah Total (Rp)', tickfont=dict(color='#C71585')),
    legend=dict(bgcolor='#FFF0F5', bordercolor='#FF1493', borderwidth=1),
    hovermode="x unified",
    margin=dict(t=60, b=40)
)

st.plotly_chart(fig, use_container_width=True)

st.write("---")

# ==========================================
# 3. BAGIAN BAWAH: ANALISIS HARIAN & KUMULATIF
# ==========================================
st.subheader("📋 Rincian Harian, Grafik Kumulatif & Segmentasi Wajib Pajak")

tab1, tab2 = st.tabs(["💧 Pajak Air Tanah", "🏡 PBB"])

with tab1:
    st.write("#### 📈 Grafik Tren Kumulatif Harian (Pajak Air Tanah)")
    if not df_air.empty:
        df_air_cum = df_air.copy()
        df_air_cum['Agustus_Cum'] = df_air_cum['Agustus_2026'].cumsum()
        df_air_cum['September_Cum'] = df_air_cum['September_2026'].cumsum()
        x_tgl = df_air_cum['Tanggal'].astype(str) + " (Agu: " + df_air_cum['Hari_Agustus'] + " | Sept: " + df_air_cum['Hari_September'] + ")"

        fig_cum_air = go.Figure()
        fig_cum_air.add_trace(go.Scatter(x=x_tgl, y=df_air_cum['Agustus_Cum'], mode='lines+markers', name='Akumulasi Agustus', line=dict(color='#FFB6C1', width=3)))
        fig_cum_air.add_trace(go.Scatter(x=x_tgl, y=df_air_cum['September_Cum'], mode='lines+markers', name='Akumulasi September', line=dict(color='#C71585', width=3)))
        fig_cum_air.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(255,255,255,0.5)',
            title=dict(text="Kurva Pertumbuhan Akumulasi Penerimaan Air Tanah", font=dict(size=16, color='#C71585')),
            xaxis=dict(title='Tanggal & Hari', type='category', tickfont=dict(color='#C71585')),
            yaxis=dict(title='Total Kumulatif (Rp)', tickfont=dict(color='#C71585')),
            legend=dict(bgcolor='#FFF0F5', bordercolor='#FF1493', borderwidth=1),
            hovermode="x unified"
        )
        st.plotly_chart(fig_cum_air, use_container_width=True)

    st.write("#### 💰 Rincian Nominal Harian Pajak Air Tanah")
    if not df_air.empty:
        st.dataframe(df_air.style.format({
            'Agustus_2026': 'Rp {:,.0f}',
            'September_2026': 'Rp {:,.0f}'
        }), use_container_width=True)
    else:
        st.info("Belum ada data harian untuk Pajak Air Tanah.")

    st.write("#### 👥 Segmentasi: Jumlah Wajib Pajak yang Membayar (Air Tanah)")
    if not df_seg_air.empty:
        st.dataframe(df_seg_air.style.format({
            'Agustus_2026': '{:,.0f} WP',
            'September_2026': '{:,.0f} WP'
        }), use_container_width=True)
    else:
        st.info("Belum ada data segmentasi WP Air Tanah.")

with tab2:
    st.write("#### 📈 Grafik Tren Kumulatif Harian (PBB)")
    if not df_pbb.empty:
        df_pbb_cum = df_pbb.copy()
        df_pbb_cum['Agustus_Cum'] = df_pbb_cum['Agustus_2026'].cumsum()
        df_pbb_cum['September_Cum'] = df_pbb_cum['September_2026'].cumsum()
        x_tgl_pbb = df_pbb_cum['Tanggal'].astype(str) + " (Agu: " + df_pbb_cum['Hari_Agustus'] + " | Sept: " + df_pbb_cum['Hari_September'] + ")"

        fig_cum_pbb = go.Figure()
        fig_cum_pbb.add_trace(go.Scatter(x=x_tgl_pbb, y=df_pbb_cum['Agustus_Cum'], mode='lines+markers', name='Akumulasi Agustus', line=dict(color='#FFB6C1', width=3)))
        fig_cum_pbb.add_trace(go.Scatter(x=x_tgl_pbb, y=df_pbb_cum['September_Cum'], mode='lines+markers', name='Akumulasi September', line=dict(color='#C71585', width=3)))
        fig_cum_pbb.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(255,255,255,0.5)',
            title=dict(text="Kurva Pertumbuhan Akumulasi Penerimaan PBB", font=dict(size=16, color='#C71585')),
            xaxis=dict(title='Tanggal & Hari', type='category', tickfont=dict(color='#C71585')),
            yaxis=dict(title='Total Kumulatif (Rp)', tickfont=dict(color='#C71585')),
            legend=dict(bgcolor='#FFF0F5', bordercolor='#FF1493', borderwidth=1),
            hovermode="x unified"
        )
        st.plotly_chart(fig_cum_pbb, use_container_width=True)

    st.write("#### 💰 Rincian Nominal Harian PBB")
    if not df_pbb.empty:
        st.dataframe(df_pbb.style.format({
            'Agustus_2026': 'Rp {:,.0f}',
            'September_2026': 'Rp {:,.0f}'
        }), use_container_width=True)
    else:
        st.info("Belum ada data harian untuk PBB.")

    st.write("#### 👥 Segmentasi: Jumlah NOP / Wajib Pajak yang Membayar (PBB)")
    if not df_seg_pbb.empty:
        st.dataframe(df_seg_pbb.style.format({
            'Agustus_2026': '{:,.0f} NOP',
            'September_2026': '{:,.0f} NOP'
        }), use_container_width=True)
    else:
        st.info("Belum ada data segmentasi NOP PBB.")
