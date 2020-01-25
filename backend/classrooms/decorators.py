from flask import request
from backend.classrooms.schemas import classroom_form_schema
from backend.models import Classroom
from functools import wraps


# Decorator to check if a classroom exists
def classroom_exists(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        classroom = Classroom.query.get(kwargs['classroom_id'])

        if classroom:
            return f(*args, **kwargs)
        else:
            return {
                       "message": "Classroom does not exist"
                   }, 404

    return wrap


# Decorator to check if a classroom form data is valid
def valid_classroom_form(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        form_data = request.get_json()
        errors = classroom_form_schema.validate(form_data)

        # If form data is not validated by the classroom_schema, then return a 500 error
        # else create the classroom and add it to the database
        if errors:
            return {
                       "message": "Missing or sending incorrect data to create a classroom. Double check the JSON data that it has everything needed to create a classroom."
                   }, 500
        else:
            return f(*args, **kwargs)

    return wrap
