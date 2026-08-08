from models.schemas import LabValues, Patient


def labs():
    return LabValues(egfr=90, creatinine=1, ast=20, alt=20)


def test_turkish_gender_is_normalized():
    assert Patient(age=40, gender="Kadın", lab_values=labs()).gender == "female"
    assert Patient(age=40, gender="Erkek", lab_values=labs()).gender == "male"


def test_english_gender_is_canonical():
    assert Patient(age=40, gender="female", lab_values=labs()).gender == "female"
    assert Patient(age=40, gender="Other", lab_values=labs()).gender == "other"
