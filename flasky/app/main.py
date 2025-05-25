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
                    'surname': patient_data.get('surname') or patient_data.get('surename'),
                    'age': patient_data.get('age')
                })
        print(pacjenci)
    return render_template('retrive.html', pacjenci= pacjenci)

@appRouting.route("/add", methods = ['POST', 'GET'])
def add():
    ref = db.reference("/Patient")
    name = request.form.get("name")
    surname = request.form.get("surname")
    patient_id = request.form.get("patient_id")
    age = request.form.get("age")
    middleName = request.form.get("middleName")
    ref = db.reference(f"/Patient/{patient_id}")
    ref.set({
        'name': name,
        'middleName' : middleName,
        'surname': surname,
        'age' : age
    })
    return render_template("add.html")



if __name__ == "__main__":
    appRouting.run(debug=True)