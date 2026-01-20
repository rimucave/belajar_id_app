from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Ganti dengan key rahasia
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///permintaan.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model Database
class Permintaan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nisn = db.Column(db.String(10), unique=True, nullable=False)
    nama = db.Column(db.String(100), nullable=False)
    kelas = db.Column(db.String(50), nullable=False)
    sekolah = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='Menunggu')  # Menunggu, Disetujui, Ditolak

# Buat database jika belum ada
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ajukan', methods=['GET', 'POST'])
def ajukan():
    if request.method == 'POST':
        nisn = request.form['nisn'].strip()
        nama = request.form['nama'].strip()
        kelas = request.form['kelas'].strip()
        sekolah = request.form['sekolah'].strip()
        email = request.form['email'].strip()

        # Validasi NISN (harus 10 digit angka)
        if not nisn.isdigit() or len(nisn) != 10:
            flash('NISN harus berupa 10 digit angka.', 'error')
            return redirect(url_for('ajukan'))

        # Cek duplikasi NISN
        existing = Permintaan.query.filter_by(nisn=nisn).first()
        if existing:
            flash('NISN ini sudah pernah mengajukan. Permintaan hanya sekali saja.', 'error')
            return redirect(url_for('ajukan'))

        # Simpan ke database
        new_request = Permintaan(nisn=nisn, nama=nama, kelas=kelas, sekolah=sekolah, email=email)
        db.session.add(new_request)
        db.session.commit()
        flash('Permintaan akun Belajar.id berhasil diajukan! Tunggu konfirmasi.', 'success')
        return redirect(url_for('index'))

    return render_template('ajukan.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        request_id = request.form['id']
        new_status = request.form['status']
        req = Permintaan.query.get(request_id)
        if req:
            req.status = new_status
            db.session.commit()
            flash('Status permintaan berhasil diupdate.', 'success')
        return redirect(url_for('admin'))

    requests = Permintaan.query.all()
    return render_template('admin.html', requests=requests)

if __name__ == '__main__':
    app.run(debug=True)
