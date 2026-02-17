import streamlit as st
from fpdf import FPDF
from datetime import datetime
from num2words import num2words
import qrcode
from io import BytesIO
import tempfile
import os

st.set_page_config(page_title="Kwitansi Ultimate 5.0", layout="centered")
st.title("🧾 Kwitansi Ultimate 5.0 – Web App")

# --- Upload Logo / Watermark ---
logo_file = st.file_uploader("Unggah Logo / Watermark (opsional)", type=["png","jpg"])

# --- Input Data Penerima & Item ---
st.markdown("### Input Data Penerima & Item")
n_penerima = st.number_input("Jumlah Penerima", min_value=1, max_value=10, value=1)

penerima_list = []

for i in range(n_penerima):
    st.markdown(f"#### Penerima {i+1}")
    nama = st.text_input(f"Nama Penerima {i+1}", key=f"nama_{i}")
    tanggal = st.date_input(f"Tanggal {i+1}", value=datetime.today(), key=f"tanggal_{i}")
    keterangan_global = st.text_area(f"Keterangan Umum {i+1}", key=f"keterangan_{i}")

    n_item = st.number_input(f"Jumlah Item {i+1}", min_value=1, max_value=10, value=1, key=f"nitem_{i}")
    items = []
    for j in range(n_item):
        deskripsi = st.text_input(f"Deskripsi Item {j+1}", key=f"des_{i}_{j}")
        qty = st.number_input(f"Qty {j+1}", min_value=1, value=1, key=f"qty_{i}_{j}")
        harga = st.number_input(f"Harga (Rp) {j+1}", min_value=0, step=1000, key=f"harga_{i}_{j}")
        items.append({"Deskripsi": deskripsi, "Qty": qty, "Harga": harga})
    penerima_list.append({
        "nama": nama,
        "tanggal": tanggal,
        "keterangan": keterangan_global,
        "items": items
    })

# --- Generate PDF Button ---
if st.button("Buat Semua Kwitansi Ultimate"):

    pdf = FPDF(format='A4', unit='mm')
    pdf.set_auto_page_break(auto=True, margin=15)
    generated = False
    kwitansi_counter = 1000

    temp_files = []  # simpan sementara logo & qr

    try:
        for idx, penerima in enumerate(penerima_list):
            if not penerima["nama"]:
                st.warning(f"Penerima {idx+1} belum diisi nama!")
                continue

            items = penerima["items"]
            total = sum(item["Qty"]*item["Harga"] for item in items)
            terbilang = num2words(total, lang='id').capitalize() + " rupiah"
            nomor_kwitansi = f"KW-{datetime.today().strftime('%Y%m%d')}-{kwitansi_counter+idx}"

            pdf.add_page()

            # Garis tepi
            pdf.set_line_width(0.5)
            pdf.rect(5,5,200,287)

            # Logo header
            if logo_file:
                tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                tfile.write(logo_file.read())
                tfile.flush()
                pdf.image(tfile.name, x=10, y=10, w=30)
                temp_files.append(tfile.name)
                logo_file.seek(0)  # reset file pointer agar bisa dipakai lagi

            # Header
            pdf.set_font("Arial",'B',18)
            pdf.cell(0,10,"KWITANSI RESMI", ln=True, align='C')
            pdf.set_font("Arial",'',10)
            pdf.cell(0,6,f"Nomor: {nomor_kwitansi}", ln=True, align='C')
            pdf.ln(5)

            # Info penerima
            pdf.set_font("Arial",'',12)
            pdf.cell(0,8,f"Telah terima dari: {penerima['nama']}", ln=True)
            pdf.cell(0,8,f"Tanggal: {penerima['tanggal'].strftime('%d-%m-%Y')}", ln=True)
            if penerima["keterangan"]:
                pdf.multi_cell(0,8,f"Keterangan: {penerima['keterangan']}")
            pdf.ln(5)

            # Tabel item
            pdf.set_font("Arial",'B',12)
            pdf.set_fill_color(200,230,255)
            pdf.cell(80,8,"Deskripsi",border=1, fill=True)
            pdf.cell(30,8,"Qty",border=1, fill=True)
            pdf.cell(40,8,"Harga (Rp)",border=1, fill=True)
            pdf.cell(40,8,"Subtotal (Rp)",border=1, ln=True, fill=True)

            pdf.set_font("Arial",'',12)
            for item in items:
                pdf.cell(80,8,str(item["Deskripsi"]),border=1)
                pdf.cell(30,8,str(item["Qty"]),border=1)
                pdf.cell(40,8,f"{item['Harga']:,}",border=1)
                subtotal = item["Qty"]*item["Harga"]
                pdf.cell(40,8,f"{subtotal:,}",border=1, ln=True)

            pdf.ln(5)
            pdf.set_font("Arial",'B',12)
            pdf.cell(0,8,f"Total: Rp {total:,}", ln=True, align='R')
            pdf.cell(0,8,f"Terbilang: {terbilang}", ln=True)
            pdf.ln(10)

            # QR Code nomor kwitansi
            qr_img = qrcode.make(nomor_kwitansi)
            qr_bytes = BytesIO()
            qr_img.save(qr_bytes, format='PNG')
            qr_bytes.seek(0)
            qr_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            qr_temp.write(qr_bytes.read())
            qr_temp.flush()
            pdf.image(qr_temp.name, x=170, y=10, w=30)
            temp_files.append(qr_temp.name)

            # Footer profesional
            pdf.set_font("Arial",'',12)
            pdf.cell(100,8,"Penerima", ln=False, align='L')
            pdf.cell(0,8,"Hormat Kami", ln=True, align='R')
            pdf.ln(25)
            pdf.cell(100,8,"____________________", ln=False, align='L')
            pdf.cell(0,8,"____________________", ln=True, align='R')

            generated = True

        if generated:
            file_name = "kwitansi_ultimate_web.pdf"
            pdf.output(file_name)
            with open(file_name,"rb") as f:
                st.download_button(
                    label="⬇️ Unduh Semua Kwitansi Ultimate PDF",
                    data=f,
                    file_name=file_name,
                    mime="application/pdf"
                )
            st.success("Semua kwitansi web versi Ultimate berhasil dibuat!")
        else:
            st.warning("Tidak ada kwitansi yang dibuat. Pastikan semua nama penerima diisi!")
    finally:
        # Bersihkan temp files
        for f in temp_files:
            if os.path.exists(f):
                os.remove(f)
      
