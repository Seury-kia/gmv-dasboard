import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mtick
import io

# Konfigurasi halaman
st.set_page_config(page_title="Dashboard GMV TikTok Affiliate", layout="wide")
sns.set(style="whitegrid")

# URL Google Sheet yang sudah dikonversi ke format CSV
sheet_url = "https://docs.google.com/spreadsheets/d/1S4nRG-PHLsqqbvwACp_QLfiW073B-ALuyy_9tx8BZKc/export?format=csv"

@st.cache_data
def load_data_from_gsheet(url):
    df = pd.read_csv(url, parse_dates=["Tanggal"])

try:
    df = load_data_from_gsheet(sheet_url)
    df['GMV'] = df['Order'] * df['Harga per Unit']

    # Sidebar filter
    st.sidebar.title("🎛️ Filter Data")
    min_date, max_date = df['Tanggal'].min(), df['Tanggal'].max()
    selected_date = st.sidebar.date_input("Pilih rentang tanggal:", [min_date, max_date])
    all_products = df['Produk'].unique().tolist()
    selected_products = st.sidebar.multiselect("Pilih produk:", all_products, default=all_products)

    # Filter data berdasarkan input
    if len(selected_date) == 2:
        df = df[(df['Tanggal'] >= pd.to_datetime(selected_date[0])) & (df['Tanggal'] <= pd.to_datetime(selected_date[1]))]
    df = df[df['Produk'].isin(selected_products)]

    # Judul utama
    st.title("📊 Dashboard GMV TikTok Affiliate")

    # GMV Harian
    daily_gmv = df.groupby('Tanggal')['GMV'].sum()
    st.subheader("📈 GMV Harian")
    fig1, ax1 = plt.subplots(figsize=(10, 4))
    ax1.plot(daily_gmv.index, daily_gmv.values, marker='o', color='blue')
    ax1.set_ylabel("GMV (Rp)")
    ax1.yaxis.set_major_formatter(mtick.StrMethodFormatter('Rp{x:,.0f}'))
    plt.xticks(rotation=45)
    st.pyplot(fig1)

    # GMV Harian per Produk
    st.subheader("📊 GMV Harian per Produk")
    gmv_pivot = df.pivot_table(index='Tanggal', columns='Produk', values='GMV', aggfunc='sum').fillna(0)
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    gmv_pivot.plot.area(ax=ax2, cmap='Set2')
    ax2.yaxis.set_major_formatter(mtick.StrMethodFormatter('Rp{x:,.0f}'))
    plt.xticks(rotation=45)
    st.pyplot(fig2)

    # Pie chart kontribusi produk
    produk_gmv = df.groupby('Produk')['GMV'].sum().sort_values(ascending=False)
    st.subheader("🧩 Kontribusi GMV per Produk")
    fig3, ax3 = plt.subplots()
    ax3.pie(produk_gmv, labels=produk_gmv.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette('pastel'))
    ax3.axis('equal')
    st.pyplot(fig3)

    # Bar chart Top Produk
    st.subheader("🥇 Top Produk")
    fig4, ax4 = plt.subplots()
    sns.barplot(x=produk_gmv.index, y=produk_gmv.values, palette='Blues_d', ax=ax4)
    ax4.yaxis.set_major_formatter(mtick.StrMethodFormatter('Rp{x:,.0f}'))
    for i, v in enumerate(produk_gmv.values):
        ax4.text(i, v, f'Rp{v:,.0f}', ha='center', va='bottom', fontsize=9)
    st.pyplot(fig4)

    # Tombol Download Excel
    st.subheader("📥 Download Data GMV")
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='GMV')
        writer.save()

    st.download_button(
        label="📤 Download Data (.xlsx)",
        data=excel_buffer.getvalue(),
        file_name='data_gmv_tiktok.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

except Exception as e:
    st.error(f"Gagal memuat data. Pastikan link Google Sheet publik dan formatnya benar.\n\n{e}")
