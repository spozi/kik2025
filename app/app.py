from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cuti_gantian.db'  # SQLite database file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Folder to store uploaded files
db = SQLAlchemy(app)

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database Model for Leave Applications
class LeaveApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama_pemohon = db.Column(db.String(100), nullable=False)
    no_kakitangan = db.Column(db.String(20), nullable=False)
    jawatan = db.Column(db.String(100), nullable=False)
    jabatan = db.Column(db.String(100), nullable=False)
    jumlah_cuti = db.Column(db.Integer, nullable=False)
    tarikh_permohonan = db.Column(db.Date, default=datetime.utcnow)
    tandatangan_pemohon = db.Column(db.String(100), nullable=False)
    tarikh_kerja = db.Column(db.String(500), nullable=False)  # Store as JSON string
    masa_kerja = db.Column(db.String(500), nullable=False)  # Store as JSON string
    tempoh_kerja = db.Column(db.String(500), nullable=False)  # Store as JSON string
    tujuan_kerja = db.Column(db.String(500), nullable=False)  # Store as JSON string
    dokumen_sokongan = db.Column(db.String(200), nullable=False)  # Path to the uploaded file
    status_permohonan = db.Column(db.String(50), default='Pending')  # Approval status
    ulasan_ketua = db.Column(db.Text, nullable=True)
    tarikh_kelulusan = db.Column(db.Date, nullable=True)
    tandatangan_ketua = db.Column(db.String(100), nullable=True)

# Create the database and tables
with app.app_context():
    db.create_all()

# Home Page
@app.route("/")
def home():
    return render_template("home.html")

# Applicant Form
@app.route("/applicant", methods=["GET", "POST"])
def applicant():
    if request.method == "POST":
        # Capture form data
        nama_pemohon = request.form.get("nama_pemohon")
        no_kakitangan = request.form.get("no_kakitangan")
        jawatan = request.form.get("jawatan")
        jabatan = request.form.get("jabatan")
        jumlah_cuti = request.form.get("jumlah_cuti")
        tarikh_permohonan = request.form.get("tarikh_permohonan")
        tandatangan_pemohon = request.form.get("tandatangan_pemohon")

        # Capture dynamic overtime data
        tarikh_kerja_list = request.form.getlist("tarikh_kerja[]")
        masa_kerja_list = request.form.getlist("masa_kerja[]")
        tempoh_kerja_list = request.form.getlist("tempoh_kerja[]")
        tujuan_kerja_list = request.form.getlist("tujuan_kerja[]")

        # Handle file upload
        dokumen_sokongan = request.files["dokumen_sokongan"]
        if dokumen_sokongan:
            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{dokumen_sokongan.filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            dokumen_sokongan.save(filepath)
        else:
            return "Error: Dokumen sokongan diperlukan."

        # Save leave application
        new_application = LeaveApplication(
            nama_pemohon=nama_pemohon,
            no_kakitangan=no_kakitangan,
            jawatan=jawatan,
            jabatan=jabatan,
            jumlah_cuti=int(jumlah_cuti),
            tarikh_permohonan=datetime.strptime(tarikh_permohonan, "%Y-%m-%d"),
            tandatangan_pemohon=tandatangan_pemohon,
            tarikh_kerja=','.join(tarikh_kerja_list),  # Store as comma-separated string
            masa_kerja=','.join(masa_kerja_list),  # Store as comma-separated string
            tempoh_kerja=','.join(tempoh_kerja_list),  # Store as comma-separated string
            tujuan_kerja=','.join(tujuan_kerja_list),  # Store as comma-separated string
            dokumen_sokongan=filename  # Store the file name
        )
        db.session.add(new_application)
        db.session.commit()

        return redirect(url_for("home"))

    return render_template("applicant.html")

# Approver Dashboard
@app.route("/approver", methods=["GET", "POST"])
def approver():
    if request.method == "POST":
        # Capture approval data
        application_id = request.form.get("application_id")
        status_permohonan = request.form.get("status_permohonan")
        ulasan_ketua = request.form.get("ulasan_ketua")
        tarikh_kelulusan = request.form.get("tarikh_kelulusan")
        tandatangan_ketua = request.form.get("tandatangan_ketua")

        # Find the leave application
        application = LeaveApplication.query.get(application_id)
        if not application:
            return "Error: Permohonan tidak ditemui."

        # Update approval details
        application.status_permohonan = status_permohonan
        application.ulasan_ketua = ulasan_ketua
        application.tarikh_kelulusan = datetime.strptime(tarikh_kelulusan, "%Y-%m-%d")
        application.tandatangan_ketua = tandatangan_ketua
        db.session.commit()

        return redirect(url_for("approver"))

    # Fetch all leave applications for the approver to view
    leave_applications = LeaveApplication.query.all()
    return render_template("approver.html", leave_applications=leave_applications)

# Leave History Page
@app.route("/leave_history")
def leave_history():
    # Fetch all leave applications from the database
    leave_history = LeaveApplication.query.all()
    return render_template("leave_history.html", leave_history=leave_history)

if __name__ == "__main__":
    app.run(debug=True)