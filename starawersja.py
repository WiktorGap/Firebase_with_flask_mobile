import firebase_admin
from firebase_admin import credentials , db
import json
import os 
import pandas as pd

from flask import Flask , render_template

appRouting = Flask(__name__)


cred = credentials.Certificate("C:\\Users\\wikto\\Desktop\\myKey.json")
app = firebase_admin.initialize_app(cred,{
    'databaseURL': 'https://patientsdb-18075-default-rtdb.europe-west1.firebasedatabase.app/'
})


ref = db.reference("/Patient")


@appRouting.route('/')
def menu():
     return render_template("menu.html")
@appRouting.route('/retrive')
def retrive():
     patientsData = retFromDb()
     return render_template("retrive.html",records=patientsData)

def writeDataOfPatientToDB():
    PatientKey = input("Enter patientKey")
    filename = input("Type filename: ")
    cwd = os.getcwd()
    path = os.path.join(cwd,filename)
    print(path)
    with open(f"{path}","r") as file:
        fileContents = json.load(file) 
    #ref.set(fileContents)  to nadpisze całe drzewko Patinet, lepiej
    ref.child(PatientKey).set(fileContents)

#writeDataOfPatientToDB(path, "Patient4")

#print(db.reference("/Patient").get())




def retriveDataFromDb():
    patientsData = ref.get()

    listOfPatients = list(patientsData.keys())
    print(listOfPatients)

    idxOfSelectedPatient = int(input("Chose idx of patient in order of occurance")) -1 

    selectedPatientKey = listOfPatients[idxOfSelectedPatient]

    dataOfPacinet = patientsData[selectedPatientKey]

    cols = []
    rows = []

    visitCols = []
    visitRows = []

    doctorCols = []
    doctorRows = []
    visitRows=[]

    for key , value in dataOfPacinet.items():
        if key !="visit":
            cols.append(key)
            rows.append(value)
        else:
            visitDict = value
            listOfVisits = list(visitDict.keys())
            print(listOfVisits)
            idxOfChosenVisit = int(input("Chose visit"))-1
            selectedKey = listOfVisits[idxOfChosenVisit]
            chosenVisitDict = visitDict[selectedKey]
            for key , value in chosenVisitDict.items():
                if key != "doctor":
                     visitCols.append(key)
                     visitRows.append(value)
                else:
                     doctorDict = value
                     listOfDoctors = list(doctorDict.keys())
                     print(listOfDoctors)
                     idxOfSelectedDoctor = int(input("Chose doctor"))-1

                     keyForSelectedDoctor = listOfDoctors[idxOfSelectedDoctor]
                     chosenDoctor = doctorDict[keyForSelectedDoctor]

                     for key , val in chosenDoctor.items():
                          doctorRows.append(key)
                          doctorCols.append(val)

                          

               

       
         
    dfVisit = pd.DataFrame([visitRows],columns=visitCols)

    dfDoctor = pd.DataFrame([doctorRows],columns=doctorCols)

    df = pd.DataFrame([rows], columns=cols)

   

    print(df)
    print("Visit data for patient")
    print(dfVisit)
    print("Data for doctor of visitation")
    print(dfDoctor)


def retFromDb():
     patientsData = ref.get()
     return patientsData
     

def updatePatientInDb():
  
    patientsData = ref.get()

    listOfKeys = list(patientsData.keys())
    print(listOfKeys)
    keyIdx = int(input("Type num of patient you want to chocie (in order occurance)")) - 1
    patient = listOfKeys[keyIdx]
    
    if patient in patientsData.keys():
            patientData = patientsData[patient]
    
    aviableFieldsToUpdate = list(patientData.keys())
    print(aviableFieldsToUpdate)
    
    while(True):
        fieldIdx = int(input("Type num of field you want to update (in order occurance)")) - 1
        keyField = aviableFieldsToUpdate[fieldIdx]

        if keyField != aviableFieldsToUpdate[-1]:
             if keyField in patientData.keys():
                userInput = input(f"Enter data to upade for field {keyField} ")
                #patientData[keyField] = userInput
                ref.child(patient).update({keyField: userInput})
                print(f"Updated {keyField} to {userInput} for {patient}")
             else:
                print("Updating 'visit' field is not handled yet.")
        else:
            vistationTreeKey = patientData[keyField]
            listOfFieldsOfVistation = list(vistationTreeKey.keys())
            print(listOfFieldsOfVistation)
            vistationIdxKey = int(input("Type num of field you want to update (in order occurance)")) - 1
            vistation= listOfFieldsOfVistation[vistationIdxKey]
            visitData = vistationTreeKey[vistation]

            print(visitData)
            vistationDataFieldsList = list(visitData.keys())
            print(f"Choose field to upadye\n: {vistationDataFieldsList}")
           
            visitationDataFieldIdx = int(input("Type num of field you want to update (in order occurance)")) - 1
            visitKey = vistationDataFieldsList[visitationDataFieldIdx]  
            
            if  visitKey != "doctor":
                if  visitKey in vistationDataFieldsList:
                        userInputVis = input(f"Enter data to upade for field  ")
                        ref.child(patient).child("visit").child(vistation).update({visitKey: userInputVis})
                        print(f"Updated {visitKey } to {userInputVis} for {patient}")
                else:
                        print("Updating 'visit' field is not handled yet.")
            else:
                 doctorData = visitData[visitKey]
                 selectedDoctor= list(doctorData.keys())
                 print(selectedDoctor)
                 selectDoctorIdx = int(input("Type num of field you want to update (in order occurance)")) - 1
                 keyForSelected = selectedDoctor[selectDoctorIdx]
                 selectedDoctorData = doctorData[keyForSelected]
                 print(selectedDoctorData)

                 selectedDoctorDataKeys = list(selectedDoctorData.keys())
                 selectDoctorIdxKeys = int(input("Type num of field you want to update (in order occurance)")) - 1

                 keyToUpadate = selectedDoctorDataKeys[selectDoctorIdxKeys] 

                 print("Choose field to upadte")
                

                 if keyToUpadate in selectedDoctorDataKeys:
                        userInputForDoctor = input(f"Enter data to upade for field  ")
                        #ref.child(patient).child("visit").child(vistation).child("doctor").child(keyToUpadate).update({visitKey: userInputForDoctor})
                        ref.child(patient).child("visit").child(vistation).child("doctor").child(keyForSelected).update({keyToUpadate: userInputForDoctor})

def deletePatientInDb():
  
    patientsData = ref.get()

    
    choice = input("Do you want to remove patient from db? y/n").lower().strip()
    if choice == "y":
        listOfKeys = list(patientsData.keys())
        print(listOfKeys)
        keyIdx = int(input("Type num of patient you want to dekete (in order occurance)")) - 1
        patient = listOfKeys[keyIdx]
        ref.child(patient).set({})
        print(f"Patient {patient} deleted from db")
    else:
        print("You are going to delete one single field")

        listOfKeys = list(patientsData.keys())
        print(listOfKeys)
        keyIdx = int(input("Type num of patient you want to dekete (in order occurance)")) - 1
        patient = listOfKeys[keyIdx]
        
        if patient in patientsData.keys():
                patientData = patientsData[patient]
        
        aviableFieldsToUpdate = list(patientData.keys())
        print(aviableFieldsToUpdate)
        
        while(True):
            fieldIdx = int(input("Type num of field you want to delete (in order occurance)")) - 1
            keyField = aviableFieldsToUpdate[fieldIdx]

            if keyField != aviableFieldsToUpdate[-1]:
                if keyField in patientData.keys():

                    ref.child(patient).child(keyField).delete()
                    print(f"Deleted {keyField} for {patient}")
                else:
                    print("Deleting 'visit' field is not handled yet.")
            else:
                vistationTreeKey = patientData[keyField]
                listOfFieldsOfVistation = list(vistationTreeKey.keys())
                print(listOfFieldsOfVistation)
                vistationIdxKey = int(input("Type num of field you want to update (in order occurance)")) - 1
                vistation= listOfFieldsOfVistation[vistationIdxKey]
                visitData = vistationTreeKey[vistation]

                print(visitData)
                vistationDataFieldsList = list(visitData.keys())
                print(f"Choose field to upadye\n: {vistationDataFieldsList}")
            
                visitationDataFieldIdx = int(input("Type num of field you want to update (in order occurance)")) - 1
                visitKey = vistationDataFieldsList[visitationDataFieldIdx]  
                
                if  visitKey != "doctor":
                    if  visitKey in vistationDataFieldsList:
                            ref.child(patient).child("visit").child(vistation).child(visitKey).delete()
                            print(f"Deleted {visitKey } for {patient}")
                    else:
                            print("Updating 'visit' field is not handled yet.")
                else:
                    doctorData = visitData[visitKey]
                    selectedDoctor= list(doctorData.keys())
                    print(selectedDoctor)
                    selectDoctorIdx = int(input("Type num of field you want to delete (in order occurance)")) - 1
                    keyForSelected = selectedDoctor[selectDoctorIdx]
                    selectedDoctorData = doctorData[keyForSelected]
                    print(selectedDoctorData)

                    selectedDoctorDataKeys = list(selectedDoctorData.keys())
                    selectDoctorIdxKeys = int(input("Type num of field you want to delete (in order occurance)")) - 1
                    
                    keyToUpadate = selectedDoctorDataKeys[selectDoctorIdxKeys] 

                    print("Choose field to upadte")
                    

                    if keyToUpadate in selectedDoctorDataKeys:
                            
                            #ref.child(patient).child("visit").child(vistation).child("doctor").child(keyToUpadate).update({visitKey: userInputForDoctor})
                            ref.child(patient).child("visit").child(vistation).child("doctor").child(keyForSelected).child(keyToUpadate).delete()




#writeDataOfPatientToDB()
#updatePatientInDb()
#retriveDataFromDb()
#deletePatientInDb()



if __name__ == "__main__":
    appRouting.run(debug=True)

    
