from bson import ObjectId


class Course:
    @staticmethod
    def validate(course_data):
        errors ={}

        if not course_data.get('name'):
            errors['name'] = 'Name is required'
        elif len(course_data.get('name', '')) < 3:
            errors['name'] = 'Name must be at least 3 characters'


        if not course_data.get('syllabus'):
            errors['syllabus'] = 'Syllabus is required'
    
        return errors
    @staticmethod
    def format_course(course):
        if course:
            course['_id'] = str(course['_id'])
        return course   