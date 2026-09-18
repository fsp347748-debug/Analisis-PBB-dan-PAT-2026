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

# Tombol Refresh Manual
col_btn1, col_btn2 = st.columns([1, 4])
with col_btn1:
    if st.button("🔄 Segarkan Data"):
        st.cache_data.clear()
        st.rerun()

def clean_nominal(df, cols):
    for col in cols:
        if col in df.columns:
            df[col] = (
                df[col].astype(str)
                .str.replace('Rp', '', regex=False)
                .str.replace('.', '', regex=False)
                .str.replace(',', '.', regex=False)
            )
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

def clean_segmentasi(df, cols):
    for col in cols:
        if col in df.columns:
            df[col] = (
                df[col].astype(str)
                .str.replace('WP/NOP', '', regex=False)
                .str.replace('WP', '', regex=False)
                .str.replace('NOP', '', regex=False)
                .str.strip()
            )
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

@st.cache_data(ttl=300)
def load_all_data():
    url_rekap = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQv4f0nx-O0qpFrfhCAG4Si4QdZMVEzE0ne1FIKgKN-LBs9O80vAQ1ZLZ0KrTOWPX8GXk7LK6H-t2Ed/pub?gid=0&single=true&output=csv"
    url_air = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQv4f0nx-O0qpFrfhCAG4Si4QdZMVEzE0ne1FIKgKN-LBs9O80vAQ1ZLZ0KrTOWPX8GXk7LK6H-t2Ed/pub?gid=589514798&single=true&output=csv"
    url_pbb = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQv4f0nx-O0qpFrfhCAG4Si4QdZMVEzE0ne1FIKgKN-LBs9O80vAQ1ZLZ0KrTOWPX8GXk7LK6H-t2Ed/pub?gid=1312799199&single=true&output=csv"
    url_seg_air = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQv4f0nx-O0qpFrfhCAG4Si4QdZMVEzE0ne1FIKgKN-LBs9O80vAQ1ZLZ0KrTOWPX8GXk7LK6H-t2Ed/pub?gid=1692042397&single=true&output=csv"
    url_seg_pbb = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQv4f0nx-O0qpFrfhCAG4Si4QdZMVEzE0ne1FIKgKN-LBs9O80vAQ1ZLZ0KrTOWPX8GXk7LK6H-t2Ed/pub?gid=349029387&single=true&output=csv"
    
    url_piutang_pbb = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQv4f0nx-O0qpFrfhCAG4Si4QdZMVEzE0ne1FIKgKN-LBs9O80vAQ1ZLZ0KrTOWPX8GXk7LK6H-t2Ed/pub?gid=1078894258&single=true&output=csv"
    url_seg_piutang_pbb = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQv4f0nx-O0qpFrfhCAG4Si4QdZMVEzE0ne1FIKgKN-LBs9O80vAQ1ZLZ0KrTOWPX8GXk7LK6H-t2Ed/pub?gid=658954115&single=true&output=csv"

    def process_df(url, bulan_str, is_seg=False):
        try:
            df = pd.read_csv(url)
            if is_seg:
                df = clean_segmentasi(df, ['Agustus_2026', 'September_2026'])
            else:
                df = clean_nominal(df, ['Agustus_2026', 'September_2026'])
            
            if 'Tanggal' in df.columns:
                dt_parsed = pd.to_datetime(df['Tanggal'].astype(str) + '-' + bulan_str + '-2026', format='%d-%m-%Y', errors='coerce')
                df['Week_Num'] = ((dt_parsed.dt.day - 1) // 7) + 1
                df['DateTime_Sort'] = dt_parsed
                df = df.sort_values('DateTime_Sort').reset_index(drop=True)
            return df
        except:
            return pd.DataFrame(columns=['Tanggal', 'Agustus_2026', 'September_2026'])

    try:
        df_rekap = pd.read_csv(url_rekap)
        df_rekap = clean_nominal(df_rekap, ['Agustus_2026', 'September_2026'])
    except:
        df_rekap = pd.DataFrame({
            'Jenis Pajak': ['Pajak Air Tanah', 'PBB'],
            'Agustus_2026': [268866606, 420000000],
            'September_2026': [835178310, 198040000]
        })
        
    df_air = process_df(url_air, '08', is_seg=False)
    df_pbb = process_df(url_pbb, '08', is_seg=False)
    df_seg_air = process_df(url_seg_air, '08', is_seg=True)
    df_seg_pbb = process_df(url_seg_pbb, '08', is_seg=True)
    df_piutang_pbb = process_df(url_piutang_pbb, '08', is_seg=False)
    df_seg_piutang_pbb = process_df(url_seg_piutang_pbb, '08', is_seg=True)
        
    return df_rekap, df_air, df_pbb, df_seg_air, df_seg_pbb, df_piutang_pbb, df_seg_piutang_pbb

df_rekap, df_air, df_pbb, df_seg_air, df_seg_pbb, df_piutang_pbb, df_seg_piutang_pbb = load_all_data()

# ==========================================
# 1. KARTU KINERJA UTAMA (KPI) REKAP TOTAL & PER JENIS PAJAK
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

# Tambahan: Rekap Detail Per Jenis Pajak (Air Tanah, PBB, Piutang PBB)
st.write("")
st.write("#### 🔍 Rincian Total Penerimaan per Jenis Pajak")
col_rp1, col_rp2, col_rp3 = st.columns(3)

# 1. Pajak Air Tanah dari Rekap / df_air
tot_air_ag = df_air['Agustus_2026'].sum() if not df_air.empty else 0
tot_air_sep = df_air['September_2026'].sum() if not df_air.empty else 0
diff_air = tot_air_sep - tot_air_ag
pct_air = (diff_air / tot_air_ag * 100) if tot_air_ag > 0 else 0
col_rp1.metric("💧 Pajak Air Tanah", f"Sep: Rp {tot_air_sep:,.0f}".replace(',', '.'), f"{pct_air:+.1f}% (Agus: Rp {tot_air_ag:,.0f})".replace(',', '.'))

# 2. PBB dari df_pbb
tot_pbb_ag = df_pbb['Agustus_2026'].sum() if not df_pbb.empty else 0
tot_pbb_sep = df_pbb['September_2026'].sum() if not df_pbb.empty else 0
diff_pbb = tot_pbb_sep - tot_pbb_ag
pct_pbb = (diff_pbb / tot_pbb_ag * 100) if tot_pbb_ag > 0 else 0
col_rp2.metric("🏡 Pajak PBB", f"Sep: Rp {tot_pbb_sep:,.0f}".replace(',', '.'), f"{pct_pbb:+.1f}% (Agus: Rp {tot_pbb_ag:,.0f})".replace(',', '.'))

# 3. Piutang PBB dari df_piutang_pbb
tot_piut_ag = df_piutang_pbb['Agustus_2026'].sum() if not df_piutang_pbb.empty else 0
tot_piut_sep = df_piutang_pbb['September_2026'].sum() if not df_piutang_pbb.empty else 0
diff_piut = tot_piut_sep - tot_piut_ag
pct_piut = (diff_piut / tot_piut_ag * 100) if tot_piut_ag > 0 else 0
col_rp3.metric("🏷️ Piutang PBB", f"Sep: Rp {tot_piut_sep:,.0f}".replace(',', '.'), f"{pct_piut:+.1f}% (Agus: Rp {tot_piut_ag:,.0f})".replace(',', '.'))

st.write("---")

# ==========================================
# 2. DIAGRAM BATANG REKAP & SELISIH
# ==========================================
st.subheader("📊 Grafik Perbandingan Total Penerimaan per Jenis Pajak")

fig = go.Figure()
x_jenis = df_rekap['Jenis Pajak']

fig.add_trace(go.Bar(
    x=x_jenis, y=df_rekap['Agustus_2026'], name='Agustus 2026 (Tanpa Insentif)',
    marker_color=['#FFB6C1', '#D8BFD8'], marker_line_color=['#FF1493', '#8A2BE2'], marker_line_width=1.5,
    hovertemplate="<b>Agustus:</b> Rp %{y:,.0f}<extra></extra>"
))

fig.add_trace(go.Bar(
    x=x_jenis, y=df_rekap['September_2026'], name='September 2026 (Berjalan Insentif)',
    marker_color=['#FF69B4', '#9370DB'], marker_line_color=['#C71585', '#4B0082'], marker_line_width=1.5,
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
# 3. BAGIAN BAWAH: ANALISIS HARIAN & KUMULATIF MINGGUAN (DIPISAH PER TAB)
# ==========================================
st.subheader("📋 Rincian Harian, Kurva Kumulatif Mingguan & Analisis Apple-to-Apple")

tab1, tab2 = st.tabs(["💧 Pajak Air Tanah", "🏡 PBB"])

hari_kerja_agus = 21 

with tab1:
    total_air_agus = df_rekap.loc[df_rekap['Jenis Pajak'].str.contains('Air', case=False, na=False), 'Agustus_2026'].values[0] if not df_rekap.empty else 0
    total_air_sept = df_rekap.loc[df_rekap['Jenis Pajak'].str.contains('Air', case=False, na=False), 'September_2026'].values[0] if not df_rekap.empty else 0
    
    valid_sept_days_air = df_air[df_air['September_2026'] > 0]['DateTime_Sort'].dropna() if not df_air.empty else pd.Series()
    hari_kerja_sept_air = valid_sept_days_air.nunique() if not valid_sept_days_air.empty else 1

    avg_workday_agus_air = total_air_agus / hari_kerja_agus
    avg_workday_sept_air = total_air_sept / hari_kerja_sept_air if hari_kerja_sept_air > 0 else 0
    growth_workday_air = ((avg_workday_sept_air - avg_workday_agus_air) / avg_workday_agus_air * 100) if avg_workday_agus_air > 0 else 0

    st.write("#### 🏛️ Analisis Apple-to-Apple (Normalisasi Hari Kerja - Air Tanah)")
    col_wa1, col_wa2, col_wa3 = st.columns(3)
    col_wa1.metric("📅 Rata-rata/Hari Agustus (Air)", f"Rp {avg_workday_agus_air:,.0f}".replace(',', '.'))
    col_wa2.metric(f"📅 Rata-rata/Hari September (s/d {hari_kerja_sept_air} hari)", f"Rp {avg_workday_sept_air:,.0f}".replace(',', '.'), f"{growth_workday_air:+.1f}% per Hari")
    col_wa3.metric("💡 Status Air Tanah", "Normalisasi Sesuai Data Masuk")
    st.write("")

    st.write("#### 📈 Kurva Kumulatif Berbasis Pekan (Weekly Cumulative - Air Tanah)")
    if not df_air.empty and 'Week_Num' in df_air.columns:
        df_air_weekly = df_air.groupby('Week_Num')[['Agustus_2026', 'September_2026']].sum().reset_index()
        df_air_weekly['Agustus_Cum'] = df_air_weekly['Agustus_2026'].cumsum()
        df_air_weekly['September_Cum'] = df_air_weekly['September_2026'].cumsum()
        df_air_weekly['Week_Label'] = "Week " + df_air_weekly['Week_Num'].astype(str)

        fig_cum_air = go.Figure()
        fig_cum_air.add_trace(go.Scatter(
            x=df_air_weekly['Week_Label'], y=df_air_weekly['Agustus_Cum'], 
            mode='lines+markers', name='Akumulasi Agustus',
            hovertemplate="<b>%{x}</b><br>Akumulasi: Rp %{y:,.0f}<extra></extra>",
            line=dict(color='#FFB6C1', width=4)
        ))
        fig_cum_air.add_trace(go.Scatter(
            x=df_air_weekly['Week_Label'], y=df_air_weekly['September_Cum'], 
            mode='lines+markers', name='Akumulasi September',
            hovertemplate="<b>%{x}</b><br>Akumulasi: Rp %{y:,.0f}<extra></extra>",
            line=dict(color='#C71585', width=4)
        ))
        fig_cum_air.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(255,255,255,0.5)',
            title=dict(text="Kurva Akumulasi Mingguan (Air Tanah)", font=dict(size=16, color='#C71585')),
            xaxis=dict(title='Periode Pekan (Weekly)', type='category', tickfont=dict(color='#C71585')),
            yaxis=dict(title='Total Kumulatif (Rp)', tickfont=dict(color='#C71585')),
            legend=dict(bgcolor='#FFF0F5', bordercolor='#FF1493', borderwidth=1),
            hovermode="x unified"
        )
        st.plotly_chart(fig_cum_air, use_container_width=True)

    st.write("#### 💰 Rincian Nominal Harian Pajak Air Tanah")
    if not df_air.empty:
        df_air_tabel = df_air[['Tanggal', 'Agustus_2026', 'September_2026']].copy()
        st.dataframe(df_air_tabel.style.format({
            'Agustus_2026': 'Rp {:,.0f}',
            'September_2026': 'Rp {:,.0f}'
        }), use_container_width=True)
    else:
        st.info("Belum ada data harian untuk Pajak Air Tanah.")

    st.write("#### 👥 Kurva Kumulatif Mingguan Jumlah Wajib Pajak (Air Tanah)")
    if not df_seg_air.empty and 'Week_Num' in df_seg_air.columns:
        df_seg_air_weekly = df_seg_air.groupby('Week_Num')[['Agustus_2026', 'September_2026']].sum().reset_index()
        df_seg_air_weekly['Agustus_Cum'] = df_seg_air_weekly['Agustus_2026'].cumsum()
        df_seg_air_weekly['September_Cum'] = df_seg_air_weekly['September_2026'].cumsum()
        df_seg_air_weekly['Week_Label'] = "Week " + df_seg_air_weekly['Week_Num'].astype(str)

        fig_seg_cum_air = go.Figure()
        fig_seg_cum_air.add_trace(go.Scatter(
            x=df_seg_air_weekly['Week_Label'], y=df_seg_air_weekly['Agustus_Cum'], 
            mode='lines+markers', name='Akumulasi WP Agustus',
            hovertemplate="<b>%{x}</b><br>Akumulasi WP: %{y:,.0f} WP<extra></extra>",
            line=dict(color='#FFB6C1', width=4, shape='spline')
        ))
        fig_seg_cum_air.add_trace(go.Scatter(
            x=df_seg_air_weekly['Week_Label'], y=df_seg_air_weekly['September_Cum'], 
            mode='lines+markers', name='Akumulasi WP September',
            hovertemplate="<b>%{x}</b><br>Akumulasi WP: %{y:,.0f} WP<extra></extra>",
            line=dict(color='#C71585', width=4, shape='spline')
        ))
        fig_seg_cum_air.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(255,255,255,0.5)',
            title=dict(text="Kurva Kumulatif Jumlah Wajib Pajak Mingguan (Air Tanah)", font=dict(size=16, color='#C71585')),
            xaxis=dict(title='Periode Pekan (Weekly)', type='category', tickfont=dict(color='#C71585')),
            yaxis=dict(title='Kumulatif Jumlah WP', tickfont=dict(color='#C71585')),
            legend=dict(bgcolor='#FFF0F5', bordercolor='#FF1493', borderwidth=1),
            hovermode="x unified"
        )
        st.plotly_chart(fig_seg_cum_air, use_container_width=True)

        df_seg_air_tabel = df_seg_air[['Tanggal', 'Agustus_2026', 'September_2026']].copy()
        st.dataframe(df_seg_air_tabel.style.format({
            'Agustus_2026': '{:,.0f} WP',
            'September_2026': '{:,.0f} WP'
        }), use_container_width=True)
    else:
        st.info("Belum ada data segmentasi WP Air Tanah.")

with tab2:
    total_pbb_agus = df_rekap.loc[df_rekap['Jenis Pajak'].str.contains('PBB', case=False, na=False), 'Agustus_2026'].values[0] if not df_rekap.empty else 0
    total_pbb_sept = df_rekap.loc[df_rekap['Jenis Pajak'].str.contains('PBB', case=False, na=False), 'September_2026'].values[0] if not df_rekap.empty else 0
    
    valid_sept_days_pbb = df_pbb[df_pbb['September_2026'] > 0]['DateTime_Sort'].dropna() if not df_pbb.empty else pd.Series()
    hari_kerja_sept_pbb = valid_sept_days_pbb.nunique() if not valid_sept_days_pbb.empty else 1

    avg_workday_agus_pbb = total_pbb_agus / hari_kerja_agus
    avg_workday_sept_pbb = total_pbb_sept / hari_kerja_sept_pbb if hari_kerja_sept_pbb > 0 else 0
    growth_workday_pbb = ((avg_workday_sept_pbb - avg_workday_agus_pbb) / avg_workday_agus_pbb * 100) if avg_workday_agus_pbb > 0 else 0

    st.write("#### 🏛️ Analisis Apple-to-Apple (Normalisasi Hari Kerja - PBB)")
    col_wp1, col_wp2, col_wp3 = st.columns(3)
    col_wp1.metric("📅 Rata-rata/Hari Agustus (PBB)", f"Rp {avg_workday_agus_pbb:,.0f}".replace(',', '.'))
    col_wp2.metric(f"📅 Rata-rata/Hari September (s/d {hari_kerja_sept_pbb} hari)", f"Rp {avg_workday_sept_pbb:,.0f}".replace(',', '.'), f"{growth_workday_pbb:+.1f}% per Hari")
    col_wp3.metric("💡 Status PBB", "Normalisasi Sesuai Data Masuk")
    st.write("")

    st.write("#### 📈 Kurva Kumulatif Berbasis Pekan (Weekly Cumulative - PBB)")
    if not df_pbb.empty and 'Week_Num' in df_pbb.columns:
        df_pbb_weekly = df_pbb.groupby('Week_Num')[['Agustus_2026', 'September_2026']].sum().reset_index()
        df_pbb_weekly['Agustus_Cum'] = df_pbb_weekly['Agustus_2026'].cumsum()
        df_pbb_weekly['September_Cum'] = df_pbb_weekly['September_2026'].cumsum()
        df_pbb_weekly['Week_Label'] = "Week " + df_pbb_weekly['Week_Num'].astype(str)

        fig_cum_pbb = go.Figure()
        fig_cum_pbb.add_trace(go.Scatter(
            x=df_pbb_weekly['Week_Label'], y=df_pbb_weekly['Agustus_Cum'], 
            mode='lines+markers', name='Akumulasi Agustus',
            hovertemplate="<b>%{x}</b><br>Akumulasi: Rp %{y:,.0f}<extra></extra>",
            line=dict(color='#D8BFD8', width=4)
        ))
        fig_cum_pbb.add_trace(go.Scatter(
            x=df_pbb_weekly['Week_Label'], y=df_pbb_weekly['September_Cum'], 
            mode='lines+markers', name='Akumulasi September',
            hovertemplate="<b>%{x}</b><br>Akumulasi: Rp %{y:,.0f}<extra></extra>",
            line=dict(color='#9370DB', width=4)
        ))
        fig_cum_pbb.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(255,255,255,0.5)',
            title=dict(text="Kurva Akumulasi Mingguan (PBB)", font=dict(size=16, color='#800080')),
            xaxis=dict(title='Periode Pekan (Weekly)', type='category', tickfont=dict(color='#800080')),
            yaxis=dict(title='Total Kumulatif (Rp)', tickfont=dict(color='#800080')),
            legend=dict(bgcolor='#FFF0F5', bordercolor='#9370DB', borderwidth=1),
            hovermode="x unified"
        )
        st.plotly_chart(fig_cum_pbb, use_container_width=True)

    st.write("#### 💰 Rincian Nominal Harian PBB")
    if not df_pbb.empty:
        df_pbb_tabel = df_pbb[['Tanggal', 'Agustus_2026', 'September_2026']].copy()
        st.dataframe(df_pbb_tabel.style.format({
            'Agustus_2026': 'Rp {:,.0f}',
            'September_2026': 'Rp {:,.0f}'
        }), use_container_width=True)
    else:
        st.info("Belum ada data harian untuk PBB.")

    st.write("#### 👥 Kurva Kumulatif Mingguan Jumlah NOP Wajib Pajak (PBB)")
    if not df_seg_pbb.empty and 'Week_Num' in df_seg_pbb.columns:
        df_seg_pbb_weekly = df_seg_pbb.groupby('Week_Num')[['Agustus_2026', 'September_2026']].sum().reset_index()
        df_seg_pbb_weekly['Agustus_Cum'] = df_seg_pbb_weekly['Agustus_2026'].cumsum()
        df_seg_pbb_weekly['September_Cum'] = df_seg_pbb_weekly['September_2026'].cumsum()
        df_seg_pbb_weekly['Week_Label'] = "Week " + df_seg_pbb_weekly['Week_Num'].astype(str)

        fig_seg_cum_pbb = go.Figure()
        fig_seg_cum_pbb.add_trace(go.Scatter(
            x=df_seg_pbb_weekly['Week_Label'], y=df_seg_pbb_weekly['Agustus_Cum'], 
            mode='lines+markers', name='Akumulasi NOP Agustus',
            hovertemplate="<b>%{x}</b><br>Akumulasi NOP: %{y:,.0f} NOP<extra></extra>",
            line=dict(color='#D8BFD8', width=4, shape='spline')
        ))
        fig_seg_cum_pbb.add_trace(go.Scatter(
            x=df_seg_pbb_weekly['Week_Label'], y=df_seg_pbb_weekly['September_Cum'], 
            mode='lines+markers', name='Akumulasi NOP September',
            hovertemplate="<b>%{x}</b><br>Akumulasi NOP: %{y:,.0f} NOP<extra></extra>",
            line=dict(color='#9370DB', width=4, shape='spline')
        ))
        fig_seg_cum_pbb.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(255,255,255,0.5)',
            title=dict(text="Kurva Kumulatif Jumlah NOP Mingguan (PBB)", font=dict(size=16, color='#800080')),
            xaxis=dict(title='Periode Pekan (Weekly)', type='category', tickfont=dict(color='#800080')),
            yaxis=dict(title='Kumulatif Jumlah NOP', tickfont=dict(color='#800080')),
            legend=dict(bgcolor='#FFF0F5', bordercolor='#9370DB', borderwidth=1),
            hovermode="x unified"
        )
        st.plotly_chart(fig_seg_cum_pbb, use_container_width=True)

        df_seg_pbb_tabel = df_seg_pbb[['Tanggal', 'Agustus_2026', 'September_2026']].copy()
        st.dataframe(df_seg_pbb_tabel.style.format({
            'Agustus_2026': '{:,.0f} NOP',
            'September_2026': '{:,.0f} NOP'
        }), use_container_width=True)
    else:
        st.info("Belum ada data segmentasi NOP PBB.")

    # ==========================================
    # 5. TAMBAHAN: BAGIAN PIUTANG PBB & SEGMENTASI PIUTANG PBB DI BAWAH PBB
    # ==========================================
    st.write("---")
    st.markdown("### 🏷️ Analisis Tambahan: Piutang PBB & Segmentasi Piutang PBB")

    # A. Kurva Kumulatif Mingguan & Harian Piutang PBB (Penerimaan Nominal)
    st.write("#### 📈 Kurva Kumulatif Berbasis Pekan (Weekly Cumulative - Piutang PBB)")
    if not df_piutang_pbb.empty and 'Week_Num' in df_piutang_pbb.columns:
        df_piutang_weekly = df_piutang_pbb.groupby('Week_Num')[['Agustus_2026', 'September_2026']].sum().reset_index()
        df_piutang_weekly['Agustus_Cum'] = df_piutang_weekly['Agustus_2026'].cumsum()
        df_piutang_weekly['September_Cum'] = df_piutang_weekly['September_2026'].cumsum()
        df_piutang_weekly['Week_Label'] = "Week " + df_piutang_weekly['Week_Num'].astype(str)

        fig_cum_piutang = go.Figure()
        fig_cum_piutang.add_trace(go.Scatter(
            x=df_piutang_weekly['Week_Label'], y=df_piutang_weekly['Agustus_Cum'], 
            mode='lines+markers', name='Akumulasi Piutang Agustus',
            hovertemplate="<b>%{x}</b><br>Akumulasi Piutang: Rp %{y:,.0f}<extra></extra>",
            line=dict(color='#D8BFD8', width=4)
        ))
        fig_cum_piutang.add_trace(go.Scatter(
            x=df_piutang_weekly['Week_Label'], y=df_piutang_weekly['September_Cum'], 
            mode='lines+markers', name='Akumulasi Piutang September',
            hovertemplate="<b>%{x}</b><br>Akumulasi Piutang: Rp %{y:,.0f}<extra></extra>",
            line=dict(color='#9370DB', width=4)
        ))
        fig_cum_piutang.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(255,255,255,0.5)',
            title=dict(text="Kurva Akumulasi Mingguan (Piutang PBB)", font=dict(size=16, color='#800080')),
            xaxis=dict(title='Periode Pekan (Weekly)', type='category', tickfont=dict(color='#800080')),
            yaxis=dict(title='Total Kumulatif Piutang (Rp)', tickfont=dict(color='#800080')),
            legend=dict(bgcolor='#FFF0F5', bordercolor='#9370DB', borderwidth=1),
            hovermode="x unified"
        )
        st.plotly_chart(fig_cum_piutang, use_container_width=True)

    st.write("#### 💰 Rincian Nominal Harian Piutang PBB")
    if not df_piutang_pbb.empty:
        df_piutang_tabel = df_piutang_pbb[['Tanggal', 'Agustus_2026', 'September_2026']].copy()
        st.dataframe(df_piutang_tabel.style.format({
            'Agustus_2026': 'Rp {:,.0f}',
            'September_2026': 'Rp {:,.0f}'
        }), use_container_width=True)
    else:
        st.info("Belum ada data harian untuk Piutang PBB.")

    # B. Kurva Kumulatif Mingguan Segmentasi Piutang PBB (Jumlah WP / NOP yang Memanfaatkan)
    st.write("#### 👥 Kurva Kumulatif Mingguan Segmentasi Piutang PBB (Jumlah WP / NOP)")
    if not df_seg_piutang_pbb.empty and 'Week_Num' in df_seg_piutang_pbb.columns:
        df_seg_piutang_weekly = df_seg_piutang_pbb.groupby('Week_Num')[['Agustus_2026', 'September_2026']].sum().reset_index()
        df_seg_piutang_weekly['Agustus_Cum'] = df_seg_piutang_weekly['Agustus_2026'].cumsum()
        df_seg_piutang_weekly['September_Cum'] = df_seg_piutang_weekly['September_2026'].cumsum()
        df_seg_piutang_weekly['Week_Label'] = "Week " + df_seg_piutang_weekly['Week_Num'].astype(str)

        fig_seg_cum_piutang = go.Figure()
        fig_seg_cum_piutang.add_trace(go.Scatter(
            x=df_seg_piutang_weekly['Week_Label'], y=df_seg_piutang_weekly['Agustus_Cum'], 
            mode='lines+markers', name='Akumulasi WP Piutang Agustus',
            hovertemplate="<b>%{x}</b><br>Akumulasi WP Piutang: %{y:,.0f} WP<extra></extra>",
            line=dict(color='#D8BFD8', width=4, shape='spline')
        ))
        fig_seg_cum_piutang.add_trace(go.Scatter(
            x=df_seg_piutang_weekly['Week_Label'], y=df_seg_piutang_weekly['September_Cum'], 
            mode='lines+markers', name='Akumulasi WP Piutang September',
            hovertemplate="<b>%{x}</b><br>Akumulasi WP Piutang: %{y:,.0f} WP<extra></extra>",
            line=dict(color='#9370DB', width=4, shape='spline')
        ))
        fig_seg_cum_piutang.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(255,255,255,0.5)',
            title=dict(text="Kurva Kumulatif Mingguan Jumlah WP Segmentasi Piutang PBB", font=dict(size=16, color='#800080')),
            xaxis=dict(title='Periode Pekan (Weekly)', type='category', tickfont=dict(color='#800080')),
            yaxis=dict(title='Kumulatif Jumlah WP / NOP', tickfont=dict(color='#800080')),
            legend=dict(bgcolor='#FFF0F5', bordercolor='#9370DB', borderwidth=1),
            hovermode="x unified"
        )
        st.plotly_chart(fig_seg_cum_piutang, use_container_width=True)

        df_seg_piutang_tabel = df_seg_piutang_pbb[['Tanggal', 'Agustus_2026', 'September_2026']].copy()
        st.dataframe(df_seg_piutang_tabel.style.format({
            'Agustus_2026': '{:,.0f} WP/NOP',
            'September_2026': '{:,.0f} WP/NOP'
        }), use_container_width=True)
    else:
        st.info("Belum ada data segmentasi Piutang PBB.")
