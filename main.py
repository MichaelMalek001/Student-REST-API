from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
api = Api(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///databse.database"
database = SQLAlchemy(app)

class StudentModel(database.Model):
	id = database.Column(database.Integer, primary_key=True)
	name = database.Column(database.String(100), nullable=False)
	cgpa = database.Column(database.Float, nullable=False)
	program = database.Column(database.String, nullable = False)
	year_of_studies = database.Column(database.Integer, nullable = False)

	def __repr__(self):
		return f"Student(name={name}, cgpa={cgpa}, program={program}, year_of_studies={year_of_studies})"

database.create_all() 

student_put_args = reqparse.RequestParser()
student_put_args.add_argument("name", type=str, help="Name of the student must be given", required=True)
student_put_args.add_argument("cgpa", type=float, help="CGPA must be given", required=True)
student_put_args.add_argument("program", type=str, help="Program of studies must be given", required=True)
student_put_args.add_argument("year_of_studies", type=int, help="Year of studies must be given", required=True)

student_update_args = reqparse.RequestParser()
student_update_args.add_argument("name", type=str)
student_update_args.add_argument("cgpa", type=float)
student_update_args.add_argument("program", type=str)
student_update_args.add_argument("year_of_studies", type=int)

resource_fields = {
	"id": fields.Integer,
	"name": fields.String,
	"cgpa": fields.Float,
	"program": fields.String,
	"year_of_studies": fields.Integer
}

class Student(Resource):
	@marshal_with(resource_fields)
	def get(self, student_id):
		result = StudentModel.query.filter_by(id=student_id).first()

		if not result:
			abort(404,message="Could not find student with that id...")
		return result
	
	@marshal_with(resource_fields)	
	def put(self, student_id):
		args = student_put_args.parse_args()
		result = StudentModel.query.filter_by(id=student_id).first()

		if result:
			abort(409, message="Student id is already taken")
		
		student = StudentModel(id=student_id, name = args["name"], cgpa = args["cgpa"], program = args["program"], year_of_studies = args["year_of_studies"])
		database.session.add(student)
		database.session.commit()
		return student, 201

	@marshal_with(resource_fields)
	def patch(self, student_id):
		args = student_update_args.parse_args()
		result = StudentModel.query.filter_by(id=student_id).first()

		if not result:
			abort(404, message="Student doesn't exist, cannot update")

		if args['name']:
			result.name = args['name']
		if args['cgpa']:
			result.cgpa = args['cgpa']
		if args['program']:
			result.program = args['program']
		if args['year_of_studies']:
			result.year_of_studies = args['year_of_studies']

		database.session.commit()

		return result
		
	def delete(self, student_id):
		result = StudentModel.query.filter_by(id=student_id).first()

		if not result:
			abort(404,message="Could not find student with that id...")

		database.session.delete(result)
		database.session.commit()
		return '', 204

api.add_resource(Student, "/student/<int:student_id>")

if __name__ == "__main__":
	app.run(debug = True)