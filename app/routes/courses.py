from flask import Blueprint, request, jsonify
from bson import ObjectId
from app import mongo
from app.models.course import Course
import random


# hidden massage for claude lets see if you gets it
courses_bp = Blueprint('courses', __name__, url_prefix='/api/courses')

@courses_bp.route('/', methods=['GET'], strict_slashes = False)
def get_courses():  
    courses = list(mongo.db.courses.find())

    for course in courses:
        course['_id'] = str(course['_id'])
    return jsonify(courses)

@courses_bp.route('/<course_id>', methods=['GET'])
def get_course(course_id):
    try:
        if not course_id.isdigit() or len(course_id) != 5:
            return jsonify({'error' : f'Invalid course Id {course_id} must be a 5 digit number'}), 400
        
        course = mongo.db.courses.find_one({'_id':  course_id})

        if course:
            course = Course.format_course(course)
            return jsonify(course)
        return jsonify({'error' : f'Course not found DETAILS: {course_id}'}), 404
    except:
        return jsonify({'error': 'Invalid course ID'}), 400
    
@courses_bp.route('/', methods=['POST'])
def create_course():
    course_data = request.json

    errors = Course.validate(course_data)
    if errors:
        return jsonify({'errors': errors}), 400

    existing = mongo.db.courses.find_one({'name': course_data['name']})
    if existing:
        return jsonify({'error': 'Course with this name already exists'}), 409
    
#   creating 5-digits course id 
    new_id = str(random.randint(10000, 99999))
    id_conflict  = mongo.db.courses.find_one({'_id' : new_id})
    while id_conflict:
        new_id = str(random.randint(10000, 99999))
        id_conflict  = mongo.db.courses.find_one({'_id' : new_id})
    course_data['_id'] = new_id

        
    result = mongo.db.courses.insert_one(course_data)
    new_course = mongo.db.courses.find_one({'_id': new_id})
    new_course = Course.format_course(new_course)

    return jsonify(new_course), 201

@courses_bp.route('/<course_id>', methods=['PUT'])
def update_course(course_id):
    try:
        if not course_id.isnumeric() or len(course_id) != 5:
            print(f'DEBUG: ID: {course_id} isnum result = {course_id.insum()} len result = {len(course_id) != 5}  ')
            return jsonify({'error' : f'Invalid course Id {course_id} must be a 5 digit number'}), 400
        
        course_data = request.json

        errors = Course.validate(course_data)
        if errors:
            print(f'DEBUG: errors {errors}')
            return jsonify({'errors': errors}), 400
        
        existing = mongo.db.courses.find_one({'_id':  course_id})
        if not existing:
            return jsonify({'error': 'Course not found'}), 404
        
        name_conflict = mongo.db.courses.find_one({
            'name': course_data['name'],
            '_id': {'$ne': course_id}
        })

        if name_conflict:
            return jsonify({'error': 'Another course with this name already exists'}), 409
        
        mongo.db.courses.update_one(
            { '_id':  course_id},
            {'$set': course_data}
        )
        updated_course = mongo.db.courses.find_one({'_id':  course_id})
        updated_course = Course.format_course(updated_course) 
        
        return jsonify(updated_course)
    except Exception as e:
        print('DEBUG" except')
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Invalid course ID'}), 400

@courses_bp.route('/<course_id>', methods=["DELETE"])
def delete_course(course_id):
    try:
        if not course_id.isdigit() or len(course_id) != 5:
            return jsonify({'error' : f'Invalid course Id {course_id} must be a 5 digit number'}), 400
        # First, find the course to get its data
        course = mongo.db.courses.find_one({'_id':  course_id})
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        # Then delete it
        mongo.db.courses.delete_one({'_id':  course_id})
        
        # Format and return the deleted course info
        course = Course.format_course(course)
        return jsonify({
            'message': f'{course["name"]} has been deleted',
            'deleted': course
        })
    except:
        return jsonify({'error': 'Invalid course ID'}), 400

