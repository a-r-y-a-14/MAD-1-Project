from .database import db

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email=db.Column(db.String(100), nullable=False)

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(100))
    overview = db.Column(db.String(2000), nullable=False)
    status = db.Column(db.Integer, nullable=False) # approved, pending, blacklisted

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    department = db.Column(db.String(100))
    status = db.Column(db.String(100), nullable=False) # approved, blacklisted

class Drive(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    comapny = db.Column(db.Integer, db.ForeignKey(Company.id), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    job_description = db.Column(db.String(100), nullable=True)
    salary = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(100))
    eligibility_criteria = db.Column(db.String(500), nullable=False)
    deadline = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(100), nullable=False) # ongoing, completed, cancelled


class Student_Applications(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    drive = db.Column(db.Integer, db.ForeignKey(Drive.id), nullable=False)
    company = db.Column(db.Integer, db.ForeignKey(Drive.comapny), nullable=False)
    student = db.Column(db.Integer, db.ForeignKey(Student.id), nullable=False)
    date = db.Column(db.Date, nullable=False)
    interview_type = db.Column(db.String(100), nullable=False)
    remarks = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=False) # applied, shortlisted, waiting, rejected