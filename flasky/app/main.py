import firebase_admin
from firebase_admin import credentials, db
import json
import os
import pandas as pd

from flask import Flask, render_template, request, redirect, url_for

appRouting = Flask(__name__)

cred = credentials.Certificate(r"C:/Users/admin/Desktop/myKey.json")
app = firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://patientsdb-18075-default-rtdb.europe-west1.firebasedatabase.app/'
})

ref = db.reference("/Patient")


@appRouting.route('/')
def index():
    return render_template("index.html")


@appRouting.route('/retrive', methods = [ 'GET'])
def retrive():
    pacjenci = []
    if request.method == 'GET':
        ref = db.reference('/Patient')
        dane = ref.get()
        print(dane)

        if dane:
            for patient_id, patient_data in dane.items():
                pacjenci.append({
                    'id': patient_id,
                    'name': patient_data.get('name'),
                    'surname': patient_data.get('surname'),
                    'age': patient_data.get('age'),
                    'visit' : patient_data.get('visit')
                })
    return render_template('retrive.html', pacjenci = pacjenci)

@appRouting.route("/add", methods = ['POST', 'GET'])
def add():
    name = request.form.get("name")
    surname = request.form.get("surname")
    patient_id = request.form.get("patient_id")
    age = request.form.get("age")
    middleName = request.form.get("middleName")
    visitNumber = request.form.get("visitNumber")
    description = request.form.get("description")
    doctor = request.form.get("doctor")
    prescription = request.form.get("prescription")
    refferal = request.form.get("refferal")
    visit = {
        visitNumber : {
        "description": description,
        "doctor": doctor,
        "prescription": prescription,
        "refferal": refferal
        }
    }
    ref = db.reference(f"/Patient/{patient_id}")
    ref.set({
        'name': name,
        'middleName' : middleName,
        'surname': surname,
        'age' : age,
        'visit' : visit
    })
    return render_template("add.html")
@appRouting.route("/delete", methods = ['GET', 'POST'])
def delete():
    patientID = request.form.get("patient_id")
    ref = db.reference(f"/Patient/{patientID}")
    message = ""
    if request.method == 'POST':
        if ref.get():
            ref.delete()
            message = "usunięto pacjenta"
            redirect(url_for('delete'))
        else:
            message = "Nie ma takiego pacjenta"
            redirect(url_for('delete'))
    redirect(url_for('delete'))
    return render_template("delete.html", message = message)

if __name__ == "__main__":
    appRouting.run(debug=True)
    print('k')