# Beijing Air Quality Dashboard

Dashboard interaktif untuk menganalisis kualitas udara di Beijing berdasarkan data dari 12 stasiun pemantauan periode 2013-2017.

## Pertanyaan Analisis

1. Bagaimana pola konsentrasi PM2.5 berubah berdasarkan musim dan jam dalam sehari di seluruh stasiun pemantauan Beijing, dan stasiun mana yang secara konsisten mencatat tingkat polusi tertinggi?
2. Faktor meteorologi mana yang memiliki korelasi paling signifikan terhadap konsentrasi PM2.5, dan apakah pola tersebut konsisten di semua stasiun?

## Struktur Direktori

```
submission/
├── dashboard/
│   ├── main_data.csv
│   └── dashboard.py
├── data/
│   └── PRSA_Data_20130301-20170228/  (12 file CSV per stasiun)
├── notebook.ipynb
├── README.md
├── requirements.txt
└── url.txt
```

## Setup Environment

### Menggunakan virtual environment (direkomendasikan)

```bash
python -m venv venv
source venv/bin/activate        # Linux / Mac
venv\Scripts\activate           # Windows

pip install -r requirements.txt
```

### Menggunakan conda

```bash
conda create --name air-quality python=3.11
conda activate air-quality
pip install -r requirements.txt
```

## Menjalankan Dashboard

Pastikan sudah berada di direktori `submission/`, lalu jalankan:

```bash
streamlit run dashboard/dashboard.py
```

Dashboard akan terbuka otomatis di browser pada `http://localhost:8501`.

## Dataset

Dataset yang digunakan adalah **Beijing Multi-Site Air Quality Data (PRSA)** yang mencakup data per jam dari 12 stasiun pemantauan di Beijing. Kolom utama:

| Kolom | Keterangan |
|-------|-----------|
| PM2.5 | Konsentrasi partikulat halus (ug/m3) |
| PM10  | Konsentrasi partikulat kasar (ug/m3) |
| SO2, NO2, CO, O3 | Polutan gas (ug/m3 atau mg/m3) |
| TEMP  | Suhu udara (C) |
| PRES  | Tekanan udara (hPa) |
| DEWP  | Titik embun (C) |
| RAIN  | Curah hujan (mm) |
| WSPM  | Kecepatan angin (m/s) |
| station | Nama stasiun pemantauan |
