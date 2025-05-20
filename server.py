from flask import Flask, jsonify, request

app= Flask (__name__)
app.config['JSON_SORT_KEYS'] = False

courses = [
    {'id': 1, "name": "linear algebra 1", "cylabus": "vectors, matrices and all kind of shit"},
    {'id': 2, "name": "intro to ai", "cylabus": "csp lm nice course"}
]

@app.route('/')
def home():
    return "Hello world im alive"

@app.route('/info')
def info():
    return "This is the info page"

@app.route('/api/courses', methods=['GET'])
def get_courses():
    return jsonify(courses)

@app.route('/api/courses/<string:course_name>', methods=['GET'])
def get_course(course_name):
    course = next ((course for course in courses if course['name'] == course_name), None)
    
    if course:
        return jsonify(course)
    return jsonify({'error': "Course not fount"}), 404

@app.route('/api/courses', methods=['POST'])
def put_course():
    new_course = request.json
    if not new_course or 'id' not in new_course or not 'name' in new_course or not 'cylabus' in new_course:
        return jsonify('error: missing details') , 400
    
    if not id_available(new_course['id']):
        return jsonify('error: duplicate id'), 409
    
    courses.append(new_course)

    return jsonify(new_course), 201

@app.route('/api/courses/<int:course_id>', methods= ['PUT'])
def update(course_id):
    new_course = request.json

    if not new_course or "name" not in new_course or 'cylabus' not in new_course:
        return jsonify('error: missing details'), 400 

    course = next((course for course in courses if course['id'] == course_id), None)
    if not course:
        return jsonify('error: course not exist to update', 404)

    course['name'] = new_course['name']
    course['cylabus'] = new_course['cylabus']
    
    return jsonify(course)

@app.route('/api/courses/<int:course_id>', methods=["DELETE"])
def remove_course(course_id):
    course_index = next ((index for index, course in enumerate(courses) if course['id'] == course_id) , None)
    
    if not course_index:
        return jsonify("error: course is not in the list"), 404
    
    removed = courses.pop(course_index)
    return jsonify({'message': f'{removed["name"]} has deleted',
                    'deleted': removed })


def id_available(id):
    available = next((True for coures in courses if courses['id'] == id), False)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')