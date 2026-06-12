# SYSTEM DEVELOPMENT BRIEF: AI-DRIVEN INFLATION PREDICTION SYSTEM (V3)

## 1. PROJECT OVERVIEW & OBJECTIVES

### 1.1 Objective
Membangun sistem prediksi tingkat inflasi bulanan (YoY / MoM) berbasis Machine Learning yang mengintegrasikan data makroekonomi dengan analisis sentimen publik. Sistem ini menggunakan **Random Forest Regressor** untuk pemodelan prediktif kuantitatif, dan **Large Language Model (LLM)** secara penuh (*full-driven*) untuk analisis sentimen, evaluasi dampak pemerintahan, serta perumusan rekomendasi kebijakan strategis. Output akhir wajib berupa satu file **Dashboard HTML interaktif** mandiri (*standalone*) yang dilengkapi dengan **Fitur Simulasi Variabel Interaktif**.

### 1.2 System Architecture Flow
1. **Data Ingestion Layer**: Crawling data inflasi dari URL resmi Bank Indonesia, serta integrasi API/Scraping terbuka untuk indikator ekonomi lainnya, berita, dan media sosial.
2. **Feature Engineering & LLM NLP Layer**: Sinkronisasi data temporal dan pemanfaatan LLM untuk mengekstrak skor sentimen kuantitatif dari teks berita/socmed.
3. **Predictive Modeling Layer**: Pemodelan regresi menggunakan `RandomForestRegressor` dengan validasi berbasis deret waktu (*time-series split*). Export bobot model/pohon keputusan ke format JSON agar bisa dibaca oleh JavaScript.
4. **LLM Analytical Inference Layer**: Pemrosesan *prompt engineering* tingkat tinggi untuk menghasilkan analisis dampak mendalam bagi pemerintah dan rekomendasi kebijakan taktis.
5. **Presentation & Simulation Layer**: Generator otomatis untuk menyusun file `index.html` yang responsif, interaktif, dan memiliki mesin kalkulator simulasi berbasis JavaScript.

---

## 2. DATA ACQUISITION & SPECIFICATIONS

Sistem akan mengumpulkan lima indikator makroekonomi dan dua aliran teks tidak terstruktur. Seluruh data wajib diselaraskan ke dalam agregasi waktu bulanan (*monthly cadence*).

| Feature Name | Source Type | Target Origin / Technical Implementation |
| :--- | :--- | :--- |
| **Historical Inflation** | Web Scraping / Parsing | **https://www.bi.go.id/id/statistik/indikator/data-inflasi.aspx**<br>*Instruksi:* Lakukan parsing struktur HTML/tabel pada halaman resmi Bank Indonesia tersebut secara akurat untuk mendapatkan angka inflasi historis bulanan. |
| **BI Rate** | Open Source / Scraping | Bank Indonesia / SEKI (Statistik Ekonomi dan Keuangan) atau portal open data ekonomi makro. |
| **Exchange Rate (USD/IDR)**| API / Library | Yahoo Finance API (`yfinance`) atau open exchange rate APIs. Agregasikan data harian menjadi rata-rata bulanan. |
| **IHK (Indeks Harga Konsumen)**| Open Source / Scraping| Portal Open Data Badan Pusat Statistik (BPS) / Open Data Indonesia. |
| **News Text Data** | Crawling / Scraping | Google News RSS, CNBC Indonesia, Kontan, atau Detik Finance menggunakan `BeautifulSoup` / `Scrapy`. |
| **Social Media Text Data**| Crawling / Scraping | Platform publik seperti Twitter/X (via open scrapper), Reddit, atau forum publik Indonesia terkait ekonomi dan harga pangan. |

---

## 3. FULL LLM-DRIVEN NLP & SENTIMENT PIPELINE

Berbeda dengan pendekatan kamus kata atau rule-based tradisional, ekstraksi sentimen wajib digerakkan sepenuhnya oleh LLM (melalui API seperti OpenAI GPT-4o, Anthropic Claude, atau model lokal seperti Llama-3/IndoBERT via Hugging Face Pipeline):

1. **Text Aggregation**: Kumpulkan seluruh teks berita dan media sosial dalam satu bulan berjalan ($t$).
2. **LLM Sentiment Prompting**: Berikan tumpukan teks (*batch text*) tersebut ke LLM dengan instruksi *system prompt* yang ketat untuk menghasilkan output terstruktur (JSON).
3. **Output Specification**: LLM harus mengembalikan nilai numerik kontinu (Skor Polarity): $S \in [-1, 1]$, di mana `-1` mengindikasikan kepanikan publik yang ekstrem/ekspektasi harga melonjak tinggi, `0` netral, dan `+1` stabilitas/optimisme ekonomi yang tinggi.
4. **Features Generated**: Hasil akhir berupa dua fitur baru: `News_Sentiment_LLM_Score_t` dan `SocMed_Sentiment_LLM_Score_t`.

---

## 4. MACHINE LEARNING MODEL: RANDOM FOREST

* **Target Variable**: `Inflation_Rate_t+1` (Tingkat inflasi pada 1 bulan ke depan).
* **Feature Space Matrix**: 
  $$X = [ \text{Inflation}_t, \text{BIRate}_t, \text{ExchangeRate}_t, \text{IHK}_t, \text{News\_Sentiment\_LLM}_t, \text{SocMed\_Sentiment\_LLM}_t ]$$
* **Algorithm**: `sklearn.ensemble.RandomForestRegressor`.
* **Validation**: Wajib menggunakan `TimeSeriesSplit` untuk mencegah kebocoran data (*data leakage*).
* **Metrics**: Evaluasi performa menggunakan MAE, RMSE, dan $R^2$.

---

## 5. FULL LLM-DRIVEN ANALYTICS FRAMEWORK

Setelah model Random Forest mengeluarkan angka prediksi inflasi (misal: *Prediksi Inflasi Bulan Depan: 3.4%*), sistem akan mengirimkan seluruh konteks data ke LLM untuk melakukan penalaran (*reasoning*) analitis tanpa aturan kaku (*no hardcoded rules*):

### 5.1 Input Context untuk LLM Inference:
Sistem akan menyusun prompt dinamis yang berisi:
* Angka Prediksi Inflasi hasil dari Random Forest beserta *Feature Importance*-nya.
* Tren Kurs, BI Rate, dan IHK terkini.
* Rangkuman teks berita dan keluhan media sosial bulan ini.

### 5.2 LLM Output Requirements (Harus Terstruktur):
LLM diinstruksikan untuk menghasilkan laporan komprehensif dalam format teks terstruktur yang mencakup:
1. **Analisis Dampak bagi Pemerintah (Government Impact Analysis)**: Analisis naratif mendalam mengenai stabilitas fiskal, kecukupan subsidi (BBM/Pangan), daya beli masyarakat, dan apakah inflasi berada di koridor target Bank Indonesia.
2. **Rekomendasi Kebijakan Strategis**: Langkah konkret yang dibagi menjadi 3 lini waktu (Immediate, Intermediate, Long-term).

---

## 6. OUTPUT SPECIFICATION: STANDALONE HTML DASHBOARD WITH INTERACTIVE SIMULATION

Seluruh output angka dari Random Forest dan output narasi analitis dari LLM wajib di-compile otomatis oleh skrip Python menjadi satu file file tunggal: `index.html`.

### 6.1 Desain & Struktur HTML:
* **UI Framework**: Menggunakan Tailwind CSS via CDN dengan tema warna profesional makroekonomi (Deep Corporate Blue `#1e3a8a`).
* **Interactivity**: Menggunakan Chart.js atau Plotly.js via CDN untuk visualisasi interaktif data historis vs prediksi.

### 6.2 Fitur Simulasi Inflasi Mandiri (Mekanisme JavaScript):
Sistem harus menyematkan **Simulation Control Panel** di dalam HTML agar pengguna (pemerintah) bisa melakukan pengujian skenario kebijakan (*What-If Analysis*).
* **Komponen Input (Sliders):**
  * Slider 1: Penyesuaian BI Rate (Rentang: 0.0% - 10.0%)
  * Slider 2: Estimasi Kurs USD/IDR (Rentang: Rp 14.000 - Rp 18.000)
  * Slider 3: Proyeksi Skor Sentimen Berita (Rentang: -1 hingga +1)
  * Slider 4: Proyeksi Skor Sentimen Media Sosial (Rentang: -1 hingga +1)
* **Kalkulator Prediksi Otomatis (Client-Side Engine):**
  * Skrip Python backend harus mengekspor estimator linear sederhana atau formula matematika hasil pendekatan pohon keputusan Random Forest ke dalam baris fungsi JavaScript di HTML.
  * Setiap kali pengguna menggeser slider variabel di atas, JavaScript akan menghitung ulang secara *real-time* dan memperbarui komponen visual **"Simulated Inflation Rate Score"** di dashboard (dilengkapi dengan indikator warna: Hijau jika inflasi turun, Merah jika inflasi melonjak).

---

## 7. EXECUTION BLUEPRINT FOR AI

AI Agent harus mengeksekusi proyek dengan urutan logis berikut:
1. **Phase 1**: Membuat scrapper untuk mengekstrak tabel data dari URL Bank Indonesia dan scraper data open-source lainnya.
2. **Phase 2**: Membangun modul konektor LLM (API) untuk pemrosesan skor sentimen teks.
3. **Phase 3**: Melatih model Random Forest Regressor dan mengekstrak koefisien/bobot regresi atau menyederhanakan struktur pohon prediksi untuk diubah menjadi formula JavaScript.
4. **Phase 4**: Membuat modul prompt-generator ke LLM untuk memproduksi analisis pemerintahan dan rekomendasi kebijakan secara penuh.
5. **Phase 5**: Menjalankan skrip HTML Factory untuk menyatukan semua data, visualisasi Chart.js, dan logika slider JavaScript ke dalam `index.html`.