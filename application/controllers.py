from flask import Flask, render_template, redirect, request, session
from flask import current_app as app
from .models import *
from sqlalchemy import and_, or_
from datetime import date, datetime
today = date.today()

@app.route("/", methods=['GET', 'POST'])
def home():
    total_companies = Company.query.filter_by(status="approved").count()
    total_students = Student.query.filter_by(status="approved").count()
    total_drives = Drive.query.count()
    total_applications = Student_Applications.query.count()
    ongoing_drives = Drive.query.filter(Drive.deadline >= today, Drive.status == "ongoing").count()
    return render_template("home.html", total_companies=total_companies, total_students=total_students, total_drives=total_drives, total_applications=total_applications, ongoing_drives=ongoing_drives)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")




@app.route("/admin-login", methods=["GET","post"])
def admin_login():
    if request.method =="POST":
        username=request.form.get("username")
        password=request.form.get("password")
        this_user=Admin.query.filter_by(username=username).first()
        if this_user:
            if this_user.password == password:
                session['user_id'] = this_user.id
                return redirect("/admin-dashboard")
            else:
                return redirect("admin_login.html")
        else:
            return render_template("admin_login.html")
    return render_template("admin_login.html")

@app.route("/admin-dashboard", methods=['GET', 'POST'])
def admin_dash():
    if 'user_id' in session:
        user_id = session['user_id']
        user = Admin.query.filter_by(id=user_id).first()
        reg_comp = Company.query.filter(Company.status == "approved").all()
        reg_stud = Student.query.filter(Student.status == "approved").all()
        comp_app = Company.query.filter(Company.status == "pending").all()
        ong_drives = Drive.query.filter(Drive.deadline >= today, Drive.status == "ongoing").all()
        stud_app = db.session.query(Student_Applications, Student, Drive, Company).join(Student, Student.id == Student_Applications.student).join(Drive, Drive.id == Student_Applications.drive).join(Company, Company.id == Student_Applications.company).all()
        return render_template("admin_dashboard.html", user=user, reg_comp=reg_comp, reg_stud=reg_stud, comp_app=comp_app, ong_drives=ong_drives, stud_app=stud_app)

@app.route("/admin-search", methods=['GET', 'POST'])
def search():
    query = request.args.get('q')
    user_id = request.args.get('user_id')
    user = Admin.query.filter_by(id=user_id).first()
    if query:
        reg_comp = Company.query.filter((Company.name.ilike(f"%{query}%") | Company.id.ilike(f"%{query}%")), Company.status == "approved").all()
        reg_stud = Student.query.filter((Student.name.ilike(f"%{query}%") | Student.id.ilike(f"%{query}%")), Student.status == "approved").all()
        comp_app = Company.query.filter((Company.name.ilike(f"%{query}%") | Company.id.ilike(f"%{query}%")), Company.status == "pending").all()
        ong_drives = Drive.query.filter(Drive.deadline <= today).all()
        stud_app = db.session.query(Student_Applications, Student, Drive, Company).join(Student, Student.id == Student_Applications.student).join(Drive, Drive.id == Student_Applications.drive).join(Company, Company.id == Student_Applications.company).all()
        return render_template("admin_dashboard.html", user=user, reg_comp=reg_comp, reg_stud=reg_stud, comp_app=comp_app, ong_drives=ong_drives, stud_app=stud_app)
    else:
        session['user_id'] = user_id
        return redirect("/admin-dashboard")
    
@app.route("/blacklist-company", methods=['GET', 'POST'])
def blacklist_company():
    id = request.args.get('id')
    comp = Company.query.filter_by(id=id).first()
    drives = Drive.query.filter(Drive.status == "ongoing", Drive.comapny == id).all()
    for drive in drives:
        drive.status = "cancelled"
    comp.status = "pending"
    db.session.commit()
    return redirect("/admin-dashboard")

@app.route("/blacklist-student", methods=['GET', 'POST'])
def blacklist_student():
    id = request.args.get('id')
    stud = Student.query.filter_by(id=id).first()
    stud.status = "pending"
    db.session.commit()
    return redirect("/admin-dashboard")

@app.route("/approve-company", methods=['GET', 'POST'])
def approve_company():
    id = request.args.get('id')
    comp = Company.query.filter_by(id=id).first()
    drives = Drive.query.filter(Drive.status == "cancelled", Drive.comapny == id).all()
    for drive in drives:
        drive.status = "ongoing"
    comp.status = "approved"
    db.session.commit()
    return redirect("/admin-dashboard")

@app.route("/mark-drive-completed", methods=['GET', 'POST'])
def mark_drive_completed():
    id = request.args.get('id')
    drive = Drive.query.filter_by(id=id).first()
    drive.status = "completed"
    db.session.commit()
    return redirect("/admin-dashboard")




@app.route("/student-login", methods=["GET","post"])
def student_login():
    if request.method =="POST":
        username=request.form.get("username")
        password=request.form.get("password")
        this_user=Student.query.filter_by(username=username).first()
        if this_user:
            if this_user.password == password:
                session['user_id'] = this_user.id
                return redirect("/student-dashboard")
            else:
                return redirect("student_login.html")
        else:
            return render_template("student_login.html")
    return render_template("student_login.html")

@app.route("/student-register", methods=['GET', 'POST'])
def student_registration():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        dob = datetime.strptime(request.form.get('dob'), "%Y-%m-%d").date()
        department = request.form.get('department')
        new_user = Student(username=username, password=password, name=fname+" "+lname, dob=dob, department=department, status="approved")
        db.session.add(new_user)
        db.session.commit()
        return redirect("/student-login")
    return render_template("student_registration.html")

@app.route("/student-dashboard", methods=['GET', 'POST'])
def student_dashboard():
    id = session['user_id']
    user = Student.query.filter_by(id=id).first()
    reg_comp = Company.query.filter(Company.status == "approved").all()
    stud_app = db.session.query(Student_Applications, Student, Drive, Company).join(Student, Student.id == Student_Applications.student).join(Drive, Drive.id == Student_Applications.drive).join(Company, Company.id == Student_Applications.company).filter(Student_Applications.student == user.id).all()
    return render_template("student_dashboard.html", user=user, reg_comp=reg_comp, stud_app=stud_app)

@app.route("/student-edit-profile", methods=['GET', 'POST'])
def student_edit_profile():
    id = session['user_id']
    student = Student.query.filter_by(id=id).first()
    if request.method == "POST":
        name = request.form.get('name')
        dob = datetime.strptime(request.form.get('dob'), "%Y-%m-%d").date()
        department = request.form.get('department')
        username = request.form.get('username')
        password = request.form.get('password')
        student.name = name
        student.dob = dob
        student.department = department
        student.username = username
        student.password = password
        db.session.commit()
        return redirect("/student-dashboard")
    return render_template("student_edit_profile.html", student=student)

@app.route("/student-history", methods=['GET', 'POST'])
def student_history():
    id = session['user_id']
    user = Student.query.filter_by(id=id).first()
    stud_app = db.session.query(Student_Applications, Drive).join(Drive, Drive.id == Student_Applications.drive).filter(Student_Applications.student == user.id).all()
    return render_template("student_history.html", stud=user, stud_app=stud_app)

@app.route("/student-view-company")
def student_view_company():
    id = request.args.get('id')
    comp = Company.query.filter_by(id=id).first()
    drives = Drive.query.filter(Drive.comapny == id, Drive.deadline >= today, Drive.status == "ongoing").all()
    return render_template("student_view_company.html", comp=comp, drives=drives)

@app.route("/student-apply-drive", methods=['GET', 'POST'])
def student_apply_drive():
    id = request.args.get('id')
    drive = Drive.query.filter_by(id=id).first()
    stud_id = session['user_id']
    stud_app = Student_Applications.query.filter(Student_Applications.drive == id, Student_Applications.student == stud_id).first()
    if stud_app:
        return redirect("/student-view-company?id="+str(drive.comapny))
    else:
        new_app = Student_Applications(drive=drive.id, company=drive.comapny, student=stud_id, date=today, interview_type="pending", remarks="none", status="applied")
        db.session.add(new_app)
        db.session.commit()
        return redirect("/student-view-company?id="+str(drive.comapny))




@app.route("/company-login", methods=["GET","post"])
def company_login():
    if request.method =="POST":
        username=request.form.get("username")
        password=request.form.get("password")
        this_user=Company.query.filter_by(username=username).first()
        if this_user:
            if this_user.password == password:
                session['user_id'] = this_user.id
                return redirect("/company-dashboard")
            else:
                return redirect("company_login.html")
        else:
            return render_template("company_login.html")
    return render_template("company_login.html")

@app.route("/company-register", methods=['GET', 'POST'])
def company_registration():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        email = request.form.get('email')
        overview = request.form.get('overview')
        address = request.form.get('address')
        new_user = Company(username=username, password=password, name=name, email=email, overview=overview, address=address, status="pending")
        db.session.add(new_user)
        db.session.commit()
        return redirect("/company-login")
    return render_template("company_registration.html")

@app.route("/company-dashboard", methods=['GET', 'POST'])
def company_dashboard():
    id = session['user_id']
    user = Company.query.filter_by(id=id).first()
    ong_drives = Drive.query.filter(Drive.comapny == id, Drive.deadline >= today, Drive.status == "ongoing").all()
    closed_drives = Drive.query.filter(Drive.comapny == id, or_((Drive.deadline < today), (Drive.status == "completed"))).all()
    stud_app = Student_Applications.query.filter(Student_Applications.status == "waiting", Student_Applications.company == id).join(Student, Student.id == Student_Applications.student).join(Drive, Drive.id == Student_Applications.drive).join(Company, Company.id == Student_Applications.company).all()
    return render_template("company_dashboard.html", user=user, ong_drives=ong_drives, closed_drives=closed_drives, stud_app=stud_app)

@app.route("/company-create-drive", methods=['GET', 'POST'])
def company_create_drive():
    id = session['user_id']
    user = Company.query.filter_by(id=id).first()
    if request.method == "POST":
        name = request.form.get('name')
        job_title = request.form.get('job_title')
        job_description = request.form.get('job_description')
        salary = request.form.get('salary')
        location = request.form.get('location')
        eligibility_criteria = request.form.get('eligibility_criteria')
        deadline = datetime.strptime(request.form.get('deadline'), "%Y-%m-%d").date()
        new_drive = Drive(comapny=user.id, name=name, job_title=job_title, job_description=job_description, salary=salary, location=location, eligibility_criteria=eligibility_criteria, deadline=deadline, status="ongoing")
        db.session.add(new_drive)
        db.session.commit()
        return redirect("/company-dashboard")
    return render_template("company_create_new_drive.html")

@app.route("/company-view-drive-details")
def company_view_drive_details():
    id = request.args.get('id')
    drive = Drive.query.filter_by(id=id).first()
    stud_apps = db.session.query(Student_Applications, Student).join(Student, Student.id == Student_Applications.student).filter(Student_Applications.drive == id).all()
    return render_template("company_view_applications.html", drive=drive, stud_apps=stud_apps)

@app.route("/company-update-applications", methods=['GET', 'POST'])
def company_update_application():
    id = request.args.get('app_id')
    stud_app = Student_Applications.query.filter_by(id=id).first()
    drive = Drive.query.filter_by(id=(stud_app.drive)).first()
    stud = Student.query.filter_by(id=(stud_app.student)).first()
    if request.method == "POST":
        status = request.form.get('status')
        stud_app.status = status
        db.session.commit()
        return redirect("/company-view-drive-details?id="+str(stud_app.drive))
    return render_template("company_update_applications.html", drive=drive, stud=stud)

@app.route("/company-mark-drive-completed", methods=['GET', 'POST'])
def company_mark_drive_completed():
    id = request.args.get('id')
    drive = Drive.query.filter_by(id=id).first()
    drive.status = "completed"
    db.session.commit()
    return redirect("/company-dashboard")

@app.route("/company-update-drive-details", methods=['GET', 'POST'])
def company_update_drive_details():
    id = request.args.get('id')
    drive = Drive.query.filter_by(id=id).first()
    if request.method == "POST":
        deadline = datetime.strptime(request.form.get('deadline'), "%Y-%m-%d").date()
        drive.deadline = deadline
        drive.status = "ongoing"
        db.session.commit()
        return redirect("/company-dashboard")
    return render_template("company_update_drive_details.html", drive=drive)
