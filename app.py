
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
from fpdf import FPDF
import base64

# --- Lógica de Negócio (DISC) ---
class DISCProfile:
    def __init__(self, d, i, s, c):
        self.scores = {'D': int(d), 'I': int(i), 'S': int(s), 'C': int(c)}

def calculate_match(student_profile, job_profile):
    sum_sq_diff = 0
    for factor in ['D', 'I', 'S', 'C']:
        sum_sq_diff += (student_profile.scores[factor] - job_profile.scores[factor]) ** 2
    distance = math.sqrt(sum_sq_diff)
    return round(max(0, 100 * (1 - (distance / 200))), 2)

def generate_behavioral_report(profile):
    scores = profile.scores
    dominant_factor = max(scores, key=scores.get)
    reports = {
        'D': "Focado em resultados, decidido e competitivo.",
        'I': "Comunicativo, entusiasmado e persuasivo.",
        'S': "Paciente, bom ouvinte e persistente.",
        'C': "Analítico, preciso e detalhista."
    }
    return reports.get(dominant_factor, "Perfil equilibrado.")

def create_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="Ranking de Match Comportamental", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(95, 10, "Candidato", border=1)
    pdf.cell(95, 10, "Match %", border=1, ln=True)
    pdf.set_font("Arial", "", 12)
    for _, row in df.iterrows():
        pdf.cell(95, 10, str(row['Nome']), border=1)
        pdf.cell(95, 10, f"{row['Match %']}%", border=1, ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- Interface Streamlit ---
st.set_page_config(page_title="Plataforma Youth Employability", layout="wide")
st.title("🚀 Dashboard de Match Comportamental")

st.sidebar.header("1. Configurar Perfil da Vaga")
v_d = st.sidebar.slider("Dominância", 0, 100, 30)
v_i = st.sidebar.slider("Influência", 0, 100, 85)
v_s = st.sidebar.slider("Estabilidade", 0, 100, 80)
v_c = st.sidebar.slider("Conformidade", 0, 100, 40)
vaga = DISCProfile(v_d, v_i, v_s, v_c)

st.sidebar.markdown("---")
st.sidebar.header("2. Upload de Candidatos")
uploaded_file = st.sidebar.file_uploader("Escolha um arquivo CSV", type="csv")

estudantes_dados = []
if uploaded_file is not None:
    df_input = pd.read_csv(uploaded_file)
    for _, row in df_input.iterrows():
        estudantes_dados.append({"nome": row['nome'], "perfil": DISCProfile(row['D'], row['I'], row['S'], row['C'])})
else:
    estudantes_dados = [
        {"nome": "João Silva", "perfil": DISCProfile(20, 90, 75, 30)},
        {"nome": "Maria Oliveira", "perfil": DISCProfile(85, 20, 30, 70)},
        {"nome": "Pedro Santos", "perfil": DISCProfile(40, 70, 85, 50)},
        {"nome": "Ana Costa", "perfil": DISCProfile(10, 40, 90, 80)}
    ]

results = []
for e in estudantes_dados:
    results.append({"Nome": e['nome'], "Match %": calculate_match(e['perfil'], vaga), "perfil": e['perfil']})
df_results = pd.DataFrame(results).sort_values("Match %", ascending=False)

col1, col2 = st.columns([1, 1])
with col1:
    st.subheader("🏆 Ranking de Match")
    st.dataframe(df_results[["Nome", "Match %"]], use_container_width=True, hide_index=True)
    pdf_bytes = create_pdf(df_results)
    st.download_button(label="📥 Exportar Ranking para PDF", data=pdf_bytes, file_name="ranking_disc.pdf", mime="application/pdf")

with col2:
    st.subheader("📊 Detalhes e Insights")
    selected_name = st.selectbox("Escolha um candidato", df_results["Nome"])
    candidate_data = next(item for item in results if item["Nome"] == selected_name)
    st.info(f"**Análise:** {generate_behavioral_report(candidate_data['perfil'])}")
    # Plot simples resumido para o app
    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    # ... (lógica de plot omitida para brevidade no script de escrita)
    st.pyplot(fig)
