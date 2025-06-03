import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="SPK Pemilihan Tanaman", layout="wide")

st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #4CAF50, #8BC34A);
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
            
    .recommendation-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(17, 153, 142, 0.3);
        margin: 2rem 0;
    }
    
    .input-section {
        background: #f8f9fa;
        padding-top: 1rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        border: 1px solid #e9ecef;
    }
    
    .input-section h3 {
        color: #2e7d32;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #4CAF50, #8BC34A);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 25px;
        font-weight: bold;
        font-size: 1.1rem;
        width: 100%;
        transition: all 0.3s ease;
    }
                
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>🌱 Sistem Pendukung Keputusan Pemilihan Tanaman</h1>
    <p>Temukan tanaman yang paling cocok untuk lahan Anda dengan metode SAW (Simple Additive Weighting)</p>
</div>
""", unsafe_allow_html=True)



def hitung_saw(alternatif_matrix, input_vector, bobot, atribut):
    selisih = np.abs(alternatif_matrix - input_vector)
    m, n = selisih.shape
    normalisasi = np.zeros((m, n))
    
    for j in range(n):
        if atribut[j] == 1:
            normalisasi[:, j] = selisih[:, j] / np.max(selisih[:, j])
        else:
            normalisasi[:, j] = np.min(selisih[:, j]) / selisih[:, j]

    return np.dot(normalisasi, bobot)


def get_user_inputs(df, deskripsi_kriteria):
    st.markdown("""
    <div class="input-section">
        <h3>Input Kondisi Lahan Anda</h3>
    </div>
    """, unsafe_allow_html=True)
    
    input_user = {}
    
    col1, col2, col3 = st.columns(3)
    
    kriteria_cols = [
        (['N', 'P', 'K'], col1),
        (['temperature', 'humidity'], col2), 
        (['ph', 'rainfall'], col3)
    ]
    
    for kriteria_group, kolom in kriteria_cols:
        with kolom:
            for kriteria in kriteria_group:
                if kriteria in deskripsi_kriteria:
                    min_val, max_val = float(df[kriteria].min()), float(df[kriteria].max())
                    default_val = round((min_val + max_val) / 2, 2)
                    step = 0.1 if kriteria in ['temperature', 'humidity', 'ph', 'rainfall'] else 1.0

                    input_user[kriteria] = st.slider(
                        label=f"{deskripsi_kriteria[kriteria]}",
                        min_value=min_val,
                        max_value=max_val,
                        value=default_val,
                        step=step,
                        key=f"slider_{kriteria}"
                    )
    
    return input_user

def tampilkan_hasil(preferensi, labels, crop_avg, input_user):
    df_hasil = pd.DataFrame({
        'Tanaman': labels,
        'Nilai Preferensi': preferensi
    }).sort_values(by='Nilai Preferensi', ascending=False).reset_index(drop=True)
    df_hasil.index += 1

    st.markdown(f"""
    <div class="recommendation-card">
        <h2>🌱 Rekomendasi Terbaik</h2>
        <h1>{df_hasil.iloc[0]['Tanaman']}</h1>
        <p>Skor Preferensi: <strong>{df_hasil.iloc[0]['Nilai Preferensi']:.4f}</strong></p>
        <p>Tanaman ini paling cocok dengan kondisi lahan Anda!</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(['📋 Kondisi Lahan', '📊 Semua Hasil', '🧮 Matriks Data', '⚖️ Bobot Kriteria'])

    with tab1:
        st.markdown("### 📋 Data Kondisi Lahan yang Diinput:")
        df_input = pd.DataFrame(input_user, index=["Nilai"])
        df_input_renamed = df_input.rename(columns={
            'N': "Nitrogen (N)",
            'P': "Fosfor (P)", 
            'K': "Kalium (K)",
            'temperature': "Suhu (°C)",
            'humidity': "Kelembapan (%)",
            'ph': "pH Tanah",
            'rainfall': "Curah Hujan (mm)"
        })
        st.dataframe(df_input_renamed.T, use_container_width=True)

    with tab2:
        st.markdown("### 📊 Semua Hasil Penilaian:")
        df_hasil_display = df_hasil.copy()
        df_hasil_display['Ranking'] = df_hasil_display.index
        df_hasil_display['Skor (%)'] = (df_hasil_display['Nilai Preferensi'] * 100).round(2)
        st.dataframe(df_hasil_display[['Ranking', 'Tanaman', 'Nilai Preferensi', 'Skor (%)']], 
                    use_container_width=True)

    with tab3:
        st.markdown("### 🧮 Data Rata-rata Kondisi Optimal Tanaman:")
        crop_avg_display = crop_avg.round(2)
        crop_avg_display.columns = [
            "Nitrogen (N)", "Fosfor (P)", "Kalium (K)", 
            "Suhu (°C)", "Kelembapan (%)", "pH Tanah", "Curah Hujan (mm)"
        ]
        st.dataframe(crop_avg_display, use_container_width=True)
        
    with tab4:
        st.markdown("### ⚖️ Bobot Kriteria yang Digunakan:")
        bobot_data = {
            'Kriteria': ["Nitrogen (N)", "Fosfor (P)", "Kalium (K)", "Suhu", "Kelembapan", "pH Tanah", "Curah Hujan"],
            'Bobot': [0.15, 0.15, 0.15, 0.2, 0.1, 0.15, 0.1],
            'Jenis': ["Benefit", "Benefit", "Benefit", "Cost", "Cost", "Cost", "Cost"]
        }
        df_bobot = pd.DataFrame(bobot_data)
        st.dataframe(df_bobot, use_container_width=True, hide_index=True)
        

def main():
    dataset = pd.read_csv("crop_recommendation.csv")

    kriteria = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    deskripsi_kriteria = {
        'N': "🧪 Nitrogen (N) di Tanah (kg/ha)",
        'P': "🧪 Fosfor (P) di Tanah (kg/ha)", 
        'K': "🧪 Kalium (K) di Tanah (kg/ha)",
        'temperature': "🌡️ Suhu (°C)",
        'humidity': "💧 Kelembapan Relatif (%)",
        'ph': "⚗️ pH Tanah",
        'rainfall': "🌧️ Curah Hujan (mm)"
    }

    crop_avg = dataset.groupby('label')[kriteria].mean()
    alternatif_matrix = crop_avg.values
    label_tanaman = crop_avg.index.tolist()

    bobot = np.array([0.15, 0.15, 0.15, 0.2, 0.1, 0.15, 0.1])
    atribut = [1, 1, 1, 0, 0, 0, 0]

    input_user = get_user_inputs(dataset, deskripsi_kriteria)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔍 Analisis & Cari Rekomendasi", key="analyze_button"):
            with st.spinner('🔄 Sedang menganalisis kondisi lahan Anda...'):
                input_vector = np.array([input_user[k] for k in kriteria])
                skor_preferensi = hitung_saw(alternatif_matrix, input_vector, bobot, atribut)
                tampilkan_hasil(skor_preferensi, label_tanaman, crop_avg, input_user)



if __name__ == "__main__":
    main()