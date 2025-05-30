import firebase_admin
from firebase_admin import credentials, db
import json
import os
import pandas as pd

from flask import Flask, render_template, request, redirect, url_for

appRouting = Flask(__name__)

cred = credentials.Certificate("C:\\Users\\admin\\Desktop\\myKey.json")
app = firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://patientsdb-18075-default-rtdb.europe-west1.firebasedatabase.app/'
})

ref = db.reference("/Patient")


@appRouting.route('/')
def menu():
    return render_template("index.html")


# @appRouting.route('/retrive')
# def retrive():
#      patientsData = retFromDb()
#      return render_template("retrive.html",records=patientsData)


@appRouting.route('/update', methods=["GET", "POST"])
def updt():
    if request.method == "POST":
        idxForPatient = int(request.form.get("idxForPatinet")) - 1
        dataField = int(request.form.get("dataField")) - 1 if request.form.get("dataField") else None
        visKey = int(request.form.get("visKey")) - 1 if request.form.get("visKey") else None
        visKeyField = int(request.form.get("visKeyField")) - 1 if request.form.get("visKeyField") else None
        doctorField = int(request.form.get("doctorField")) - 1 if request.form.get("doctorField") else None
        selectedDoctorIdx = int(request.form.get("selectedDoctorIdx")) - 1 if request.form.get(
            "selectedDoctorIdx") else None

        newDataForFieldPatient = request.form.get("newDataForFieldPatient")
        newDataForFieldVisit = request.form.get("newDataForFieldVisit")
        newDataForDoctorField = request.form.get("newDataForDoctorField")

        updatePatientInDb(
            idxForPatient,
            dataField,
            visKey,
            visKeyField,
            doctorField,
            newDataForFieldPatient,
            newDataForFieldVisit,
            newDataForDoctorField,
            selectedDoctorIdx
        )
        return "Zaktualizowano dane"

    return render_template("update.html")


def writeDataOfPatientToDB():
    PatientKey = input("Enter patientKey")
    filename = input("Type filename: ")
    cwd = os.getcwd()
    path = os.path.join(cwd, filename)
    print(path)
    with open(f"{path}", "r") as file:
        fileContents = json.load(file)
        # ref.set(fileContents)  to nadpisze całe drzewko Patinet, lepiej
    ref.child(PatientKey).set(fileContents)


# writeDataOfPatientToDB(path, "Patient4")

# print(db.reference("/Patient").get())


def retriveDataFromDb():
    patientsData = ref.get()

    listOfPatients = list(patientsData.keys())
    print(listOfPatients)

    idxOfSelectedPatient = int(input("Chose idx of patient in order of occurance")) - 1

    selectedPatientKey = listOfPatients[idxOfSelectedPatient]

    dataOfPacinet = patientsData[selectedPatientKey]

    cols = []
    rows = []

    visitCols = []
    visitRows = []

    doctorCols = []
    doctorRows = []
    visitRows = []

    for key, value in dataOfPacinet.items():
        if key != "visit":
            cols.append(key)
            rows.append(value)
        else:
            visitDict = value
            listOfVisits = list(visitDict.keys())
            print(listOfVisits)
            idxOfChosenVisit = int(input("Chose visit")) - 1
            selectedKey = listOfVisits[idxOfChosenVisit]
            chosenVisitDict = visitDict[selectedKey]
            for key, value in chosenVisitDict.items():
                if key != "doctor":
                    visitCols.append(key)
                    visitRows.append(value)
                else:
                    doctorDict = value
                    listOfDoctors = list(doctorDict.keys())
                    print(listOfDoctors)
                    idxOfSelectedDoctor = int(input("Chose doctor")) - 1

                    keyForSelectedDoctor = listOfDoctors[idxOfSelectedDoctor]
                    chosenDoctor = doctorDict[keyForSelectedDoctor]

                    for key, val in chosenDoctor.items():
                        doctorRows.append(key)
                        doctorCols.append(val)

    dfVisit = pd.DataFrame([visitRows], columns=visitCols)

    dfDoctor = pd.DataFrame([doctorRows], columns=doctorCols)

    df = pd.DataFrame([rows], columns=cols)

    print(df)
    print("Visit data for patient")
    print(dfVisit)
    print("Data for doctor of visitation")
    print(dfDoctor)


def retFromDb():
    patientsData = ref.get()
    return patientsData


def updatePatientInDb(
        idxForPatinet,
        dataField=None,
        visKey=None,
        visKeyField=None,
        doctorField=None,
        newDataForFieldPatient=None,
        newDataForFieldVisit=None,
        newDataForDoctorField=None,
        selectedDoctorIdx=None
):
    patientsData = ref.get()
    listOfKeys = list(patientsData.keys())
    patient = listOfKeys[idxForPatinet]

    if patient not in patientsData:
        print(f"Błąd: pacjent o indeksie {idxForPatinet} nie istnieje.")
        return

    patientData = patientsData[patient]
    aviableFieldsToUpdate = list(patientData.keys())

    if dataField is None or dataField >= len(aviableFieldsToUpdate):
        print("Błąd: dataField poza zakresem.")
        return

    keyField = aviableFieldsToUpdate[dataField]

    if keyField != "visit":
        if newDataForFieldPatient is None:
            print("Błąd: brak danych dla pola pacjenta.")
            return
        ref.child(patient).update({keyField: newDataForFieldPatient})
        print(f"Updated {keyField} to {newDataForFieldPatient} for {patient}")
    else:

        vistationTreeKey = patientData[keyField]
        listOfFieldsOfVistation = list(vistationTreeKey.keys())

        if visKey is None or visKey >= len(listOfFieldsOfVistation):
            print("Błąd: visKey poza zakresem.")
            return

        vistation = listOfFieldsOfVistation[visKey]
        visitData = vistationTreeKey[vistation]
        vistationDataFieldsList = list(visitData.keys())

        if visKeyField is None or visKeyField >= len(vistationDataFieldsList):
            print("Błąd: visKeyField poza zakresem.")
            return

        visitKey = vistationDataFieldsList[visKeyField]

        if visitKey != "doctor":
            if newDataForFieldVisit is None:
                print("Błąd: brak danych dla pola wizyty.")
                return
            ref.child(patient).child("visit").child(vistation).update({visitKey: newDataForFieldVisit})
            print(f"Updated {visitKey} to {newDataForFieldVisit} for {patient}")
        else:

            doctorData = visitData[visitKey]
            doctorKeys = list(doctorData.keys())

            if selectedDoctorIdx is None or selectedDoctorIdx >= len(doctorKeys):
                print("Błąd: selectedDoctorIdx poza zakresem.")
                return

            selectedDoctor = doctorKeys[selectedDoctorIdx]
            selectedDoctorData = doctorData[selectedDoctor]
            doctorFieldsList = list(selectedDoctorData.keys())

            if doctorField is None or doctorField >= len(doctorFieldsList):
                print("Błąd: doctorField poza zakresem.")
                return

            keyToUpdate = doctorFieldsList[doctorField]

            if newDataForDoctorField is None:
                print("Błąd: brak danych dla pola lekarza.")
                return

            ref.child(patient).child("visit").child(vistation).child("doctor").child(selectedDoctor).update(
                {keyToUpdate: newDataForDoctorField})
            print(f"Updated doctor field {keyToUpdate} to {newDataForDoctorField} for {patient}")


def deletePatientInDb(keyIDX, fieldIDX, visKeyIdx, visitDataFieldIdx, selectedDoctorIdx, selectedDoctorIdxKey):
    patientsData = ref.get()

    patient = keyIDX

    if patient not in patientsData:
        print("Patient not found")
        return

    patientData = patientsData[patient]
    aviableFieldsToUpdate = list(patientData.keys())
    print(aviableFieldsToUpdate)

    fieldIDX = int(fieldIDX)
    keyField = aviableFieldsToUpdate[fieldIDX]

    if keyField != aviableFieldsToUpdate[-1]:
        if keyField in patientData:
            ref.child(patient).child(keyField).delete()
            print(f"Deleted {keyField} for {patient}")
        else:
            print("Deleting 'visit' field is not handled yet.")
    else:
        vistationTreeKey = patientData[keyField]
        listOfFieldsOfVistation = list(vistationTreeKey.keys())
        print(listOfFieldsOfVistation)
        visKeyIdx = int(visKeyIdx)
        vistation = listOfFieldsOfVistation[visKeyIdx]
        visitData = vistationTreeKey[vistation]

        print(visitData)
        vistationDataFieldsList = list(visitData.keys())
        print(f"Choose field to update\n: {vistationDataFieldsList}")

        visitDataFieldIdx = int(visitDataFieldIdx)
        visitKey = vistationDataFieldsList[visitDataFieldIdx]

        if visitKey != "doctor":
            if visitKey in vistationDataFieldsList:
                ref.child(patient).child("visit").child(vistation).child(visitKey).delete()
                print(f"Deleted {visitKey} for {patient}")
            else:
                print("Updating 'visit' field is not handled yet.")
        else:
            doctorData = visitData[visitKey]
            selectedDoctor = list(doctorData.keys())
            print(selectedDoctor)
            selectedDoctorIdx = int(selectedDoctorIdx)
            keyForSelected = selectedDoctor[selectedDoctorIdx]
            selectedDoctorData = doctorData[keyForSelected]
            print(selectedDoctorData)

            selectedDoctorIdxKey = int(selectedDoctorIdxKey)
            selectedDoctorDataKeys = list(selectedDoctorData.keys())
            keyToUpdate = selectedDoctorDataKeys[selectedDoctorIdxKey]

            print("Choose field to update")

            if keyToUpdate in selectedDoctorDataKeys:
                ref.child(patient).child("visit").child(vistation).child("doctor").child(keyForSelected).child(
                    keyToUpdate).delete()


@appRouting.route("/delete", methods=['GET', 'POST'])
def delete():
    message = ""
    if request.method == 'POST':
        flag = request.form.get("flag", "").lower().strip()
        patientID = request.form.get("patient_id")
        ref = db.reference(f"/Patient/{patientID}")

        if flag == "tak":
            if ref.get():
                ref.delete()
                message = "Usunięto pacjenta"
            else:
                message = "Nie ma takiego pacjenta"
        else:
            try:
                keyIDX = request.form.get("patient_id")
                fieldIDX = int(request.form.get("dataField")) - 1 if request.form.get("dataField") else None
                visKeyIdx = int(request.form.get("visKey")) - 1 if request.form.get("visKey") else None
                visitDataFieldIdx = int(request.form.get("visKeyField")) - 1 if request.form.get(
                    "visKeyField") else None
                selectedDoctorIdx = int(request.form.get("selectedDoctorIdx")) - 1 if request.form.get(
                    "selectedDoctorIdx") else None
                selectedDoctorIdxKey = int(request.form.get("doctorField")) - 1 if request.form.get(
                    "doctorField") else None

                deletePatientInDb(
                    keyIDX,
                    fieldIDX,
                    visKeyIdx,
                    visitDataFieldIdx,
                    selectedDoctorIdx,
                    selectedDoctorIdxKey
                )
                message = "Usunięto wskazane dane"
            except Exception as e:
                message = f"Wystąpił błąd: {e}"

    return render_template("delete.html", message=message)


@appRouting.route('/retrive', methods=['GET'])
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
                    'visit': patient_data.get('visit')
                })
    return render_template('retrive.html', pacjenci=pacjenci)


@appRouting.route("/add", methods=['POST', 'GET'])
def add():
    name = request.form.get("name")
    surname = request.form.get("surname")
    patient_id = request.form.get("patient_id")
    age = request.form.get("age")
    middleName = request.form.get("middleName")
    visitNumber = request.form.get("visitNumber")
    description = request.form.get("description")
    doctor = request.form.get("doctor")
    nameDoctor = request.form.get("nameDoctor")
    surnameDoctor = request.form.get("surnameDoctor")
    prescription = request.form.get("prescription")
    refferal = request.form.get("refferal")

    doctorDict = {}
    doctorDict
    {
        doctor:{
        "surname":nameDoctor,
        "surname":surnameDoctor,
        }

    }
    visit = {
        visitNumber: {
            "description": description,
            "doctor": doctorDict,
            "prescription": prescription,
            "refferal": refferal
        }
    }
    ref = db.reference(f"/Patient/{patient_id}")
    ref.set({
        'name': name,
        'middleName': middleName,
        'surname': surname,
        'age': age,
        'visit': visit
    })
    return render_template("add.html")


# writeDataOfPatientToDB()
# updatePatientInDb()
# retriveDataFromDb()
# deletePatientInDb()


if __name__ == "__main__":
    appRouting.run(debug=True)
