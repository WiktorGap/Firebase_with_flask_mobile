@appRouting.route('/retrive', methods=['GET'])
def retrive():
    pacjenci = []
    if request.method == 'GET':
        ref = db.reference('/Patient')
        dane = ref.get()

        if dane:
            for patient_id, patient_data in dane.items():
                visits = []
                visit_data = patient_data.get("visit")
                

                if visit_data:
                    for visit_id, visit_content in visit_data.items():
                        visits.append({
                            'description': visit_content.get('description'),
                            'prescription': visit_content.get('prescription'),
                            'referral': visit_content.get('referral')
                        })

                pacjenci.append({
                    'id': patient_id,
                    'name': patient_data.get('name'),
                    'surname': patient_data.get('surname') or patient_data.get('surename'),
                    'age': patient_data.get('age'),
                    'visits': visits
                })

    return render_template('retrive.html', pacjenci=pacjenci)



<!DOCTYPE html>
<html>
<head>
    <title>Pacjenci</title>
</head>
<body>
    <h2>Pobierz pacjentów</h2>
    <form action="/retrive" method="GET">
        <button type="submit">Pobierz pacjentów</button>
    </form>

    <ul>
    {% for pacjent in pacjenci %}
        <li>
            <strong>ID:</strong> {{ pacjent.id }}<br>
            <strong>Imię:</strong> {{ pacjent.name }}<br>
            <strong>Nazwisko:</strong> {{ pacjent.surname }}<br>
            <strong>Wiek:</strong> {{ pacjent.age }}
        </li>

        {% if pacjent.visits %}
            <ul>
            {% for visit in pacjent.visits %}
                <li>
                    <strong>Opis wizyty:</strong> {{ visit.description }}<br>
                    <strong>Recepta:</strong> {{ visit.prescription }}<br>
                    <strong>Skierowanie:</strong> {{ visit.referral }}<br>
                </li>
            {% endfor %}
            </ul>
        {% else %}
            <li>Brak wizyt.</li>
        {% endif %}
    {% endfor %}
    </ul>
</body>
</html>
