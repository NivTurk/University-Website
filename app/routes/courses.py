from flask import Blueprint, request, jsonify
from bson import ObjectId
from app import mongo
from app.models.course import Course

courses_bp = Blueprint('courses', __name__, url_prefix='/api/courses')

@courses_bp.route('/', methods=['GET'])
def get_courses():
    courses = list(mongo.db.courses.find())

    for course in courses:
        course['_id'] = str(course('_id'))
    return jsonify(courses)

@courses_bp.route('/<course_id>', methods=['GET'])
def get_course(course_id):
    try:
        course = mongo.db.courses.find_one({'_id': ObjectId(course_id)})
        if course:
            course = Course.format_course(course)
            return jsonify(course)
        return jsonify({'error' : 'Course not found'}), 404
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
        
    result = mongo.db.courses.insert_one(course_data)
    new_course = mongo.db.courses.find_one({'_id': result.inserted_id})
    new_course = Course.format_course(new_course)

    return jsonify(new_course), 201

@courses_bp.route('/<course_id>', methods=['PUT'])
def update_course(course_id):
    try:
        course_data = request.json

        errors = Course.validate(course_data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        existing = mongo.db.courses.find_one({'_id': ObjectId(course_id)})
        if not existing:
            return jsonify({'error': 'Course not found'}), 404
        
        name_conflict = mongo.db.courses.find_one({
            'name': course_data['name'],
            '_id': {'$ne': ObjectId(course_id)}
        })

        if name_conflict:
            return jsonify({'error': 'Another course with this name alreadt exists'}), 409
        
        mongo.db.courses.update_one(
            { '_id': ObjectId(course_id)},
            {'$set': course_data}
        )
        updated_course = mongo.db.courses.find_one({'_id': ObjectId(course_id)})
        updated_course = Course.format_course(updated_course) 
        
        return jsonify(updated_course)
    except:
        return jsonify({'error': 'Invalid course ID'}), 400

@courses_bp.route('/<course_id>', methods=["DELETE"])
def delete_course(course_id):
    try:
        course = mongo.db.delete_one({'_id': ObjectId(course_id)})

        course = Course.format_course(course)
        return jsonify({
            'message': f'{course["name"]} has been deleted',
            'deleted': course
        })
    except:
        return jsonify({'error': 'Invalid course ID'}), 400

