from flask_app.config.mysqlconnection import connectToMySQL
import re	# the regex module
# create a regular expression object that we'll use later   
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
from flask import flash
from flask_app.models import user

db = "location"
class Location:
    def __init__(self,data):
        self.id = data['id']
        self.title = data['title']
        self.description = data['description']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.user_id = data['user_id']
        self.user = None

    @classmethod
    def create_valid_location(cls, location_dict):
        if not cls.is_valid(location_dict):
            return False
        
        query = """INSERT INTO locations (title, description, user_id) VALUES (%(title)s, %(description)s, %(user_id)s);"""
        location_id = connectToMySQL(db).query_db(query, location_dict)
        location = cls.get_by_id(location_id)

        return location

    @classmethod
    def get_by_id(cls, location_id):

        data = {"id": location_id}
        query = "SELECT * FROM locations JOIN users ON locations.user_id = users.id WHERE locations.id = %(id)s;"
        results = connectToMySQL(db).query_db(query,data)
        if not results:
            return False
        location = results[0]
        location_obj = cls(location)

        # convert joined user data into a user object
        location_obj.user = user.User(
            {
                "id": location["users.id"],
                "first_name": location["first_name"],
                "last_name": location["last_name"],
                "email": location["email"],
                "created_at": location["users.created_at"],
                # "updated_at": location["users.updated_at"],
                "password": location["password"]
            }
        )
        print (location_obj.title)
        return location_obj
        # location = cls(result)

        # user_obj = user.User.get_by_id(result["user_id"])

        # location.user = user_obj

        # return location

    @classmethod
    def delete_location_by_id(cls, location_id):

        data = {"id": location_id}
        query = "DELETE from locations WHERE id = %(id)s;"
        connectToMySQL(db).query_db(query,data)

        return location_id


    @classmethod
    def update_location(cls, location_dict, session_id):

        # Authenticate User first
        location = cls.get_by_id(location_dict["id"])
        if location.user.id != session_id:
            flash("You must be the creator to update this location.")
            return False

        # Validate the input
        if not cls.is_valid(location_dict):
            return False
        
        # Update the data in the database.
        query = """UPDATE locations
                    SET title = %(title)s, description = %(description)s
                    WHERE id = %(id)s;"""
        results = connectToMySQL(db).query_db(query,location_dict)
        location = cls.get_by_id(location_dict["id"])
        
        return location

    @classmethod
    def get_all(cls):
        # Get all locations, and the user info for the creators
        query = """SELECT *
                    FROM locations
                    JOIN users on users.id = locations.user_id;"""
        location_data = connectToMySQL(db).query_db(query)

        # Make a list to hold location objects to return
        locations = []

        # Iterate through the list of location dictionaries
        for location in location_data:

            # convert data into a location object
            location_obj = cls(location)

            # convert joined user data into a user object
            location_obj.user = user.User(
                {
                "id": location["users.id"],
                "first_name": location["first_name"],
                "last_name": location["last_name"],
                "email": location["email"],
                "created_at": location["users.created_at"],
                # "updated_at": location["users.updated_at"],
                "password": location["password"]
                }
            )
            locations.append(location_obj)


        return locations

    @staticmethod
    def is_valid(location_dict):
        valid = True
        flash_string = " field is required and must be at least 3 characters."
        if len(location_dict["title"]) < 3:
            flash("Title " + flash_string)
            valid = False
        if len(location_dict["description"]) < 3:
            flash("Description " + flash_string)
            valid = False
 

        return valid
        