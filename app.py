import streamlit as st
import pandas as pd
import os
from datetime import date

# =====================
# SESSION STATE INIT (WAJIB DI AWAL)
# =====================
if "login" not in st.session_state:
    st.session_state.login = False

if "role" not in st.session_state:
    st.session_state.role = None

if "username" not in st.session_state:
    st.session_state.username = None

# =====================
# KONFIGURASI FILE
# =====================
RIWAYAT_FILE = "riwayat_kunjungan.csv"
OBAT_FILE = "data_obat.csv"
PENYAKIT_FILE = "data_penyakit.csv"

# =====================
# USER LOGIN DUMMY
# =====================
USERS = {
    "salsabila": {"password": "salsabila123", "role": "siswa"},
    "admin": {"password": "admin", "role": "admin"}
}

# =====================
# LOAD DATA
# =====================
df_riwayat = pd.read_csv(RIWAYAT_FILE)
df_obat = pd.read_csv(OBAT_FILE)
df_penyakit = pd.read_csv(PENYAKIT_FILE)
LOGO_FILE = "uks_logo.png"

df_riwayat["tanggal"] = (
    pd.to_datetime(df_riwayat["tanggal"], errors="coerce")
    .dt.strftime("%Y-%m-%d")
)

# =====================
# LOGIN PAGE
# =====================
if not st.session_state.login:
    st.image(LOGO_FILE, width=180)
    st.title("Login Layanan UKS")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USERS and USERS[username]["password"] == password:
            st.session_state.login = True
            st.session_state.role = USERS[username]["role"]
            st.session_state.username = username
            st.success("Login berhasil")
            st.rerun()
        else:
            st.error("Username atau password salah")

    st.stop()

# =====================
# FILTER DATA SETELAH LOGIN
# =====================
if st.session_state.role == "siswa":
    df_riwayat_user = df_riwayat[
        df_riwayat["nama_siswa"].str.lower()
        == st.session_state.username.lower()
    ]
else:
    df_riwayat_user = df_riwayat

# =====================
# SIDEBAR MENU
# =====================
st.sidebar.image(LOGO_FILE, width=150)
st.sidebar.title("Menu UKS")

menu_siswa = [
    "Dashboard Siswa",
    "Profil & Tata Tertib UKS",
    "Edukasi Kesehatan",
    "Riwayat Kunjungan UKS",
    "Status Kunjungan Terakhir"
]

menu_admin = menu_siswa + ["Dashboard Admin"]

menu = st.sidebar.selectbox(
    "Pilih Menu",
    menu_admin if st.session_state.role == "admin" else menu_siswa
)

st.sidebar.markdown("---")

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

# =====================
# DASHBOARD SISWA
# =====================
if menu == "Dashboard Siswa":
    st.header("Dashboard Siswa")

    st.metric("Total Kunjungan", len(df_riwayat_user))
    st.metric("Status Terakhir", df_riwayat_user.iloc[-1]["status"])

    st.subheader("Jumlah Kunjungan per Bulan")
    # kunjungan_bulanan = df_riwayat_user.groupby(
    #     df_riwayat_user["tanggal"].dt.to_period("M")
    # ).size()
    # st.bar_chart(kunjungan_bulanan)

    # kunjungan_bulanan = (
    #     df_riwayat_user
    #     .dropna(subset=["tanggal"])
    #     .groupby(pd.to_datetime(df_riwayat_user["tanggal"]).dt.strftime("%Y-%m"))

    #     .size()
    # )

    # st.bar_chart(kunjungan_bulanan)

    kunjungan_bulanan = (
        df_riwayat_user
        .dropna(subset=["tanggal"]).groupby(pd.to_datetime(df_riwayat_user["tanggal"]).dt.strftime("%Y-%m"))
        .size()
    )

    kunjungan_bulanan.name = "Jumlah Kunjungan"

    st.bar_chart(kunjungan_bulanan)

# =====================
# PROFIL UKS
# =====================
elif menu == "Profil & Tata Tertib UKS":
    st.header("Profil & Tata Tertib UKS")

    st.write("**Definisi UKS**")
    st.write("Unit Kesehatan Sekolah adalah layanan kesehatan di lingkungan sekolah.")

    st.write("**Visi & Misi**")
    st.write("Mewujudkan siswa yang sehat jasmani dan rohani.")

    st.write("**Tata Tertib**")
    st.write("- Datang dengan tertib\n- Laporkan keluhan dengan jujur")

    st.write("**Petugas UKS**")
    st.write("- Bu Ani\n- Pak Budi")

# =====================
# EDUKASI KESEHATAN
# =====================
elif menu == "Edukasi Kesehatan":
    st.header("Edukasi Kesehatan")

    keyword = st.text_input("Masukkan nama penyakit atau obat").lower()

    if keyword:
        obat_match = df_obat[df_obat["nama"].str.lower() == keyword]
        penyakit_match = df_penyakit[df_penyakit["nama"].str.lower() == keyword]

        if not obat_match.empty:
            st.subheader("Kategori: Obat")
            row = obat_match.iloc[0]
            st.write("**Pengertian:**", row["pengertian"])
            st.write("**Manfaat:**", row["manfaat"])
            st.write("**Dosis:**", row["dosis"])
            st.write("**Efek Samping:**", row["efek_samping"])

        elif not penyakit_match.empty:
            st.subheader("Kategori: Penyakit")
            row = penyakit_match.iloc[0]
            st.write("**Pengertian:**", row["pengertian"])
            st.write("**Gejala:**", row["gejala"])
            st.write("**Penyebab:**", row["penyebab"])
            st.write("**Pengobatan:**", row["pengobatan"])

        else:
            st.warning("Data tidak ditemukan")

# =====================
# RIWAYAT KUNJUNGAN
# =====================
elif menu == "Riwayat Kunjungan UKS":
    st.header("Riwayat Kunjungan UKS")

    if df_riwayat_user.empty:
        st.info("Tidak ada riwayat kunjungan")
    else:
        selected = st.selectbox(
            "Pilih Tanggal Kunjungan",
            df_riwayat_user.index,
            format_func=lambda x: df_riwayat_user.loc[x, "tanggal"]

        )

        row = df_riwayat_user.loc[selected]
        for col in df_riwayat_user.columns:
            st.write(f"**{col.capitalize()}** : {row[col]}")

# =====================
# STATUS TERAKHIR
# =====================
elif menu == "Status Kunjungan Terakhir":
    st.header("Status Kunjungan Terakhir")

    if df_riwayat_user.empty:
        st.info("Belum ada kunjungan")
    else:
        last = df_riwayat_user.iloc[-1]
        for col in df_riwayat_user.columns:
            st.write(f"**{col.capitalize()}** : {last[col]}")

# =====================
# DASHBOARD ADMIN
# =====================
elif menu == "Dashboard Admin":
    st.header("Dashboard Admin UKS")

    st.metric("Total Kunjungan", len(df_riwayat))

    st.subheader("Distribusi Status Kunjungan")
    st.bar_chart(df_riwayat["status"].value_counts())

    st.subheader("Input Kunjungan Baru")

    with st.form("input_kunjungan"):
        tanggal = st.date_input("Tanggal", date.today())
        nama = st.text_input("Nama Siswa")
        keluhan = st.text_input("Keluhan")
        tindakan = st.text_input("Tindakan")
        obat = st.text_input("Obat")
        status = st.selectbox("Status", ["Dirawat", "Dipulangkan", "Dirujuk"])
        catatan = st.text_input("Catatan")

        submit = st.form_submit_button("Simpan")

        if submit:
            new_row = {
                "tanggal": str(tanggal),
                "nama_siswa": nama,
                "keluhan": keluhan,
                "tindakan": tindakan,
                "obat": obat,
                "status": status,
                "catatan": catatan
            }

            df_riwayat = pd.concat(
                [df_riwayat, pd.DataFrame([new_row])],
                ignore_index=True
            )
            df_riwayat.to_csv(RIWAYAT_FILE, index=False)

            st.success("Data berhasil disimpan")
            st.rerun()
