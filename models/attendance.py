from . import db

class Attendance(db.Model):
    __tablename__ = 'ATTENDANCE'

    Attendance_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Member_ID = db.Column(db.Integer, db.ForeignKey('MEMBER.Member_ID', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    Workout_ID = db.Column(db.Integer, db.ForeignKey('WORKOUT.Workout_ID', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    Date = db.Column(db.Date, nullable=False)
    Check_In_Time = db.Column(db.Time, nullable=False)
    Check_Out_Time = db.Column(db.Time, nullable=True)
    Workout_Duration = db.Column(db.Integer, nullable=False, default=0)

    # 1:N Relationship
    remarks = db.relationship('AttendanceRemarks', backref='attendance', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):
        return f'<Attendance {self.Attendance_ID}: Member {self.Member_ID} on {self.Date}>'


class AttendanceRemarks(db.Model):
    __tablename__ = 'ATTENDANCE_REMARKS'

    Attendance_ID = db.Column(db.Integer, db.ForeignKey('ATTENDANCE.Attendance_ID', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    Remarks = db.Column(db.String(255), primary_key=True)

    def __repr__(self):
        return f'<AttendanceRemarks {self.Attendance_ID}: {self.Remarks}>'
