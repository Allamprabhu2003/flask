import random
import datetime
from final import create_app, db
from final.models import Attendance, Class, Student

# Create your app and app context
app = create_app()
app.app_context().push()

def bulk_insert_attendance(num_records=1000):
    classes = Class.query.all()
    students = Student.query.all()
    
    if not classes or not students:
        print("No classes or students found in the database.")
        return

    attendance_records = []

    for _ in range(num_records):
        student = random.choice(students)
        class_ = random.choice(classes)
        timestamp = datetime.datetime.utcnow() - datetime.timedelta(days=random.randint(0, 30))

        attendance_record = Attendance(
            student_id=student.id,
            class_id=class_.id,
            timestamp=timestamp,
            status=random.choice(['present', 'absent', 'late'])
        )
        attendance_records.append(attendance_record)
    
    db.session.bulk_save_objects(attendance_records)
    db.session.commit()
    print(f"{num_records} attendance records have been inserted into the database.")

if __name__ == "__main__":
    bulk_insert_attendance(1000)  # Insert 1000 attendance records
