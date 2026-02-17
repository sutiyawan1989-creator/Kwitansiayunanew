import streamlit as st
from fpdf import FPDF
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="Kwitansi Otomatis", layout="centered")

st.title("🧾 Aplikasi Kwitansi Otomatis")

# --- INPUT DATA ---
nama = st.text_input("Nama Penerima")
nominal = st.number_input("Nominal (Rp)", min_value=0, step=1000)
terbilang = st.text_input("Terbilang (opsional)")
keterangan = st.text_area("Keterangan")
tanggal = st.date_input("Tanggal", value=datetime.today())

# --- GENERATE PDF BUTTON ---
if st.button("Buat Kwitansi"):
    if not nama or nominal <= 0:
        st.warning("Isi semua data dengan benar!")
    else:
        pdf = FPDF(format='A5', unit='mm')
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "KWITANSI", ln=True, align='C')
        pdf.ln(10)

        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 8, f"Telah terima dari: {nama}", ln=True)
        pdf.cell(0, 8, f"Jumlah Uang: Rp {nominal:,.0f}", ln=True)
        if terbilang:
            pdf.cell(0, 8, f"Terbilang: {terbilang}", ln=True)
        pdf.cell(0, 8, f"Untuk Pembayaran: {keterangan}", ln=True)
        pdf.cell(0, 8, f"Tanggal: {tanggal.strftime('%d-%m-%Y')}", ln=True)
        pdf.ln(20)
        pdf.cell(0, 8, "Penerima", ln=True, align='R')
        pdf.ln(20)
        pdf.cell(0, 8, "____________________", ln=True, align='R')

        # Save PDF ke file sementara
        file_name = f"kwitansi_{nama.replace(' ', '_')}.pdf"
        pdf.output(file_name)

        # Tampilkan link download
        with open(file_name, "rb") as f:
            st.download_button(
                label="⬇️ Unduh Kwitansi PDF",
                data=f,
                file_name=file_name,
                mime="application/pdf"
            )

        st.success("Kwitansi berhasil dibuat!")
        
