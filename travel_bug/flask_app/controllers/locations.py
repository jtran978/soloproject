from flask import render_template,redirect,session,request, flash
from flask_app import app
from flask_app.models.user import User
from flask_app.models.location import Location
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

# @app.route('/')
# def index():
#     return render_template('location.html')

@app.route("/locations/home")
def locations_home():
    if "user_id" not in session:
        flash("You must be logged in to access the dashboard.")
        return redirect("/")
    
    user = User.get_by_id(session["user_id"])


    return render_template("dashboard.html", user=user)

@app.route("/locations/<int:location_id>")
def location_detail(location_id):
    data = {"id":session["user_id"]}
    user = User.get_by_id(data)
    location = Location.get_by_id(location_id)
    return render_template("show_location.html", user=user, location=location)

@app.route("/locations/create")
def location_create_page():
    return render_template("add_location.html")

@app.route("/locations/edit/<int:location_id>")
def location_edit_page(location_id):
    location = Location.get_by_id(location_id)
    return render_template("edit_location.html", location=location)

######## POST and ACTION METHODS ########

@app.route("/locations", methods=["POST"])
def create_location():
    valid_location = Location.create_valid_location(request.form)
    if valid_location:
        return redirect(f'/locations/{valid_location.id}')
    return redirect('/locations/create')

@app.route("/locations/<int:location_id>", methods=["POST"])
def update_location(location_id):

    valid_location = Location.update_location(request.form, session["user_id"])

    if not valid_location:
        return redirect(f"/locations/edit/{location_id}")
        
    return redirect(f"/locations/{location_id}")

@app.route("/locations/delete/<int:location_id>")
def delete_by_id(location_id):
    Location.delete_location_by_id(location_id)
    return redirect("/dashboard")