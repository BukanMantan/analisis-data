import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Muat data
day_df = pd.read_csv("day.csv")
hour_df = pd.read_csv("hour.csv")

# Konversi 'dteday' ke datetime
day_df['dteday'] = pd.to_datetime(day_df['dteday'])
hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])

# Hitung statistik yang diperlukan
day_max = day_df['cnt'].max()
day_min = day_df['cnt'].min()
day_mean = day_df['cnt'].mean()

hour_max = hour_df['cnt'].max()
hour_min = hour_df['cnt'].min()
hour_mean = hour_df['cnt'].mean()

# Hitung rata-rata penyewaan per bulan
monthly_avg_rentals = day_df.groupby(day_df['dteday'].dt.month)['cnt'].mean().reset_index()
monthly_avg_rentals.columns = ['bulan', 'cnt']

# Hitung rata-rata penyewaan per jam
hourly_avg_rentals = hour_df.groupby('hr')['cnt'].mean().reset_index()

# Hitung rata-rata penyewaan untuk hari kerja vs akhir pekan
day_df['is_weekend'] = day_df['dteday'].dt.dayofweek.isin([5, 6]) # 5 dan 6 adalah Sabtu dan Minggu
avg_rentals_weekday_weekend = day_df.groupby('is_weekend')['cnt'].mean().reset_index()
avg_rentals_weekday_weekend['tipe_hari'] = avg_rentals_weekday_weekend['is_weekend'].map({False: 'Hari Kerja (Senin-Jumat)', True: 'Akhir Pekan (Sabtu-Minggu)'})

# Hitung rata-rata penyewaan berdasarkan cuaca
avg_rentals_by_weather = hour_df.groupby('weathersit')['cnt'].mean().reset_index()
weather_sit_mapping = {1: 'Jernih', 2: 'Kabut', 3: 'Salju/Hujan Ringan', 4: 'Hujan Salju Berat'}
avg_rentals_by_weather['weathersit'] = avg_rentals_by_weather['weathersit'].map(weather_sit_mapping)

# Hitung persentase pengguna kasual vs terdaftar per jam
hour_df['persentase_kasual'] = hour_df['casual'] / hour_df['cnt'] * 100
hour_df['persentase_terdaftar'] = hour_df['registered'] / hour_df['cnt'] * 100
casual_registered_df = hour_df.groupby('hr')[['persentase_kasual', 'persentase_terdaftar']].mean().reset_index()

# Hitung total penyewaan dari waktu ke waktu
total_rentals_df = day_df.groupby('dteday')['cnt'].sum().reset_index()

# Analisis RFM
# Di sini, kita akan menggunakan 'dteday' sebagai tanggal, 'cnt' untuk penyewaan, dan anggap ada 'bike_id' atau identifikasi serupa.
rfm_df = day_df.groupby('instant').agg({
'dteday': lambda x: (day_df['dteday'].max() - x.max()).days, # Recency
'instant': 'count',# Frequency
'cnt': 'sum' # Monetary (menggunakan total penyewaan sebagai proksi)
}).rename(columns={
 'dteday': 'Recency',
 'instant': 'Frequency',
 'cnt': 'Monetary'
}).reset_index()

# Setel konfigurasi halaman
st.set_page_config(layout="wide")

# Judul utama
st.title('Dasbor Analisis Penyewaan Sepeda')

# Buat dua kolom untuk baris atas
col1, col2 = st.columns(2)

with col1:
  st.header("Statistik Penyewaan")
  
  # Statistik dasar
  st.subheader("Data Harian (day.csv):")
  st.metric("Penyewaan Tertinggi", f"{day_max}")
  st.metric("Penyewaan Terendah", f"{day_min}")
  st.metric("Rata-rata Penyewaan", f"{day_mean:.2f}")

  st.subheader("Data Per Jam (hour.csv):")
  st.metric("Penyewaan Tertinggi", f"{hour_max}")
  st.metric("Penyewaan Terendah", f"{hour_min}")
  st.metric("Rata-rata Penyewaan", f"{hour_mean:.2f}")

with col2:
  st.header("Polarisasi Musiman dan Harian")
  st.write("Data Harian:")
  st.info("Penyewaan tertinggi biasanya terjadi pada bulan Juni (musim panas).")
  st.info("Penyewaan terendah biasanya terjadi pada bulan Januari (musim dingin).")

  st.write("Data Per Jam:")
  st.info("Puncak penyewaan pada pukul 8 pagi dan 5 sore, mendukung pola komuter harian.")
  st.info("Penyewaan terendah pada jam-jam awal pagi (sekitar pukul 3 pagi).")

# Buat tiga kolom untuk baris tengah
col3, col4, col5 = st.columns(3)

with col3:
  st.subheader('Rata-rata Penyewaan per Bulan')
  st.line_chart(monthly_avg_rentals.set_index('bulan'))
  st.info("""
  Grafik ini menunjukkan rata-rata jumlah penyewaan sepeda untuk setiap bulan.
  - Puncak yang lebih tinggi menunjukkan bulan-bulan dengan lebih banyak penyewaan.
  - Titik yang lebih rendah mewakili bulan-bulan dengan lebih sedikit penyewaan.
  - Ini dapat membantu mengidentifikasi tren musiman dalam pola penyewaan sepeda.
  """)

with col4:
  st.subheader('Rata-rata Penyewaan per Jam')
  st.line_chart(hourly_avg_rentals.set_index('hr'))
  st.info("""
  Grafik ini menampilkan rata-rata jumlah penyewaan sepeda untuk setiap jam dalam sehari.
  - Puncak sering terjadi pada jam-jam komuter (pagi dan sore).
  - Titik-titik rendah biasanya mewakili jam-jam malam.
  - Ini membantu mengidentifikasi pola harian dalam penggunaan sepeda.
  """)

with col5:
  st.subheader('Rata-rata Penyewaan: Hari Kerja vs Akhir Pekan')
  
  fig, ax = plt.subplots(figsize=(10, 6))
  bars = ax.bar(avg_rentals_weekday_weekend['tipe_hari'], avg_rentals_weekday_weekend['cnt'])
  ax.set_xlabel('Tipe Hari')
  ax.set_ylabel('Rata-rata Penyewaan')
  ax.set_title('Rata-rata Penyewaan: Hari Kerja (Senin-Jumat) vs Akhir Pekan (Sabtu-Minggu)')
  
  # Tambahkan label nilai di atas setiap bar
  for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
        f'{height:.0f}',
        ha='center', va='bottom')
  
  st.pyplot(fig)
  
  st.info("""
  Grafik ini membandingkan rata-rata jumlah penyewaan sepeda pada hari kerja versus akhir pekan.
  - Hari Kerja: Senin hingga Jumat
  - Akhir Pekan: Sabtu dan Minggu
  - Ini membantu memahami bagaimana pola penyewaan berbeda antara hari kerja dan hari libur.
  """)

# Buat dua kolom untuk baris bawah
col6, col7 = st.columns(2)

with col6:
  st.subheader('Rata-rata Penyewaan Berdasarkan Cuaca')
  fig, ax = plt.subplots(figsize=(8, 5))
  bars2 = ax.bar(avg_rentals_by_weather['weathersit'], avg_rentals_by_weather['cnt'])
  ax.set_xlabel('Situasi Cuaca')
  ax.set_ylabel('Rata-rata Penyewaan')
  ax.set_title('Rata-rata Penyewaan Berdasarkan Cuaca')

  # Anotasi bar
  for bar in bars2:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
        f'{height:.0f}',
        ha='center', va='bottom') 

  st.pyplot(fig)
  st.info("""
  Grafik ini menunjukkan bagaimana kondisi cuaca yang berbeda memengaruhi penyewaan sepeda.
  - Setiap bar mewakili situasi cuaca yang berbeda.
  - Bar yang lebih tinggi menunjukkan kondisi cuaca yang lebih mendukung penyewaan sepeda.
  - Ini membantu memahami dampak cuaca pada pola penyewaan.
  """)

with col7:
  st.subheader('Pengguna Kasual vs Terdaftar per Jam')
  fig, ax = plt.subplots(figsize=(10, 6))
  ax.plot(casual_registered_df['hr'], casual_registered_df['persentase_kasual'], label='Kasual', marker='o')
  ax.plot(casual_registered_df['hr'], casual_registered_df['persentase_terdaftar'], label='Terdaftar', marker='x')
  ax.set_xlabel('Jam')
  ax.set_ylabel('Persentase')
  ax.set_title('Pengguna Kasual vs Terdaftar per Jam')
  ax.legend()
  ax.grid(True)
  st.pyplot(fig)
  st.info("""
  Grafik ini membandingkan persentase pengguna kasual vs terdaftar untuk setiap jam dalam sehari.
  - Pengguna kasual: Mereka yang menggunakan layanan tanpa langganan jangka panjang.
  - Pengguna terdaftar: Mereka dengan langganan jangka panjang.
  - Ini membantu memahami pola penggunaan antara berbagai jenis pengguna sepanjang hari.
  """)

# Grafik lebar penuh di bagian bawah
st.subheader('Total Penyewaan dari Waktu ke Waktu')
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(total_rentals_df['dteday'], total_rentals_df['cnt'], marker='o', linestyle='-')
ax.set_xlabel('Tanggal')
ax.set_ylabel('Total Penyewaan')
ax.set_title('Total Penyewaan dari Waktu ke Waktu')
ax.grid(True)
st.pyplot(fig)
st.info("""
Grafik ini menunjukkan total jumlah penyewaan sepeda selama periode waktu dataset.
- Setiap titik mewakili total penyewaan untuk tanggal tertentu.
- Ini membantu memvisualisasikan tren keseluruhan, musiman, dan peristiwa atau anomali signifikan dalam data penyewaan dari waktu ke waktu.
- Tren naik menunjukkan popularitas yang meningkat, sementara penurunan mungkin mewakili musim off atau faktor lain yang memengaruhi penyewaan.
""")

# Bagian Analisis RFM
st.subheader('Analisis RFM Penyewaan Sepeda')
st.write("Bagian ini menganalisis pola penyewaan menggunakan metrik Recency, Frequency, dan Monetary (RFM).")

# Tampilkan tabel RFM
st.write("Tabel RFM:")
st.write(rfm_df.head())

# Visualisasikan skor RFM
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
sns.histplot(rfm_df['Recency'], kde=True, ax=axes[0])
axes[0].set_title('Distribusi Recency')

sns.histplot(rfm_df['Frequency'], kde=True, ax=axes[1])
axes[1].set_title('Distribusi Frequency')

sns.histplot(rfm_df['Monetary'], kde=True, ax=axes[2])
axes[2].set_title('Distribusi Monetary')

st.pyplot(fig)
st.info("""
Analisis RFM membantu memahami pola penyewaan di berbagai sepeda:
- **Recency** mengukur seberapa baru sebuah sepeda disewa.
- **Frequency** mengukur seberapa sering sebuah sepeda disewa.
- **Monetary** mengukur total jumlah penyewaan (digunakan sebagai proksi untuk nilai).
- Metrik ini membantu mengidentifikasi berbagai jenis sepeda (misalnya, yang sering digunakan vs. yang jarang digunakan).
""")
