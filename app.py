from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages
import mysql.connector
import datetime

# Membuat koneksi flask
app = Flask(__name__)
app.secret_key = 'supersecretkey'  

# Koneksi ke database MySQL
def create_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost", 
            user="root", 
            password="",  
            database="restoran"  
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    
def initialize_database():
    connection = create_connection()
    if connection is None:
        return
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS makanan (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nama VARCHAR(255) NOT NULL,
            harga INT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS minuman (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nama VARCHAR(255) NOT NULL,
            harga INT NOT NULL
        )
    """)
    connection.close()

# menyambungkan ke index.html untuk halaman pertama
@app.route('/')
def index():
    return render_template('index.html')

# menyambungkan ke kasir.html untuk halaman kasir
# mode kasir digunakan untuk memanggil menu makanan dan minuman dari database beserta harganya
@app.route('/kasir', methods=['GET', 'POST'])
def kasir():
    if request.method == 'POST':
        pesanan = request.form.getlist('pesanan')
        total_harga = sum(int(item.split(',')[1]) for item in pesanan)
        pesanan_nama = ', '.join([item.split(',')[0] for item in pesanan])
        waktu_pesanan = datetime.datetime.now().strftime("%d/%b/%Y %X")
        return render_template('pesanan_selesai.html', pesanan=pesanan_nama, total_harga=total_harga, waktu_pesanan=waktu_pesanan)

    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT nama, harga FROM makanan")
    makanan = cursor.fetchall()
    cursor.execute("SELECT nama, harga FROM minuman")
    minuman = cursor.fetchall()
    connection.close()
    return render_template('kasir.html', makanan=makanan, minuman=minuman)

# menyambungkan ke admin.html untuk halaman admin
# mode admin digunakan untuk menambahkan database baik makanan maupun minuman dengan harganya
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        jenis = request.form['jenis']
        nama = request.form['nama']
        harga = request.form['harga']

        if not nama or not harga.isdigit():
            flash("Nama harus berupa string dan harga harus berupa angka")
            return redirect(url_for('admin'))

        harga = int(harga)
        connection = create_connection()
        cursor = connection.cursor()
        if jenis == 'makanan':
            cursor.execute("INSERT INTO makanan (nama, harga) VALUES (%s, %s)", (nama, harga))
        else:
            cursor.execute("INSERT INTO minuman (nama, harga) VALUES (%s, %s)", (nama, harga))
        connection.commit()
        connection.close()

        flash(f"{jenis.capitalize()} {nama} dengan harga Rp{harga} telah ditambahkan")
        return redirect(url_for('admin', show_dialog=True))

    show_dialog = request.args.get('show_dialog', 'false').lower() == 'true'
    return render_template('admin.html', show_dialog=show_dialog)

# menjalankan program dengan "debug true" agar update terjadi secara live
if __name__ == "__main__":
    initialize_database()
    app.run(debug=True)
