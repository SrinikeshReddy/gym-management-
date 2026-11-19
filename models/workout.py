from . import db

class Workout(db.Model):
    __tablename__ = 'WORKOUT'

    Workout_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Workout_Name = db.Column(db.String(100), nullable=False)
    Description = db.Column(db.Text, nullable=True)
    Calories_Burn = db.Column(db.Integer, nullable=False, default=0)
    Duration_Minutes = db.Column(db.Integer, nullable=False, default=0)
    Difficulty_Level = db.Column(db.String(20), nullable=False, default='Medium')
    Trainer_ID = db.Column(db.Integer, db.ForeignKey('TRAINER.Trainer_ID', ondelete='SET NULL', onupdate='CASCADE'), nullable=True)

    # Relationships
    attendances = db.relationship('Attendance', backref='workout', cascade='all, delete-orphan', lazy=True)
    participations = db.relationship('ParticipatesIn', backref='workout', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):
        return f'<Workout {self.Workout_ID}: {self.Workout_Name}>'


class ParticipatesIn(db.Model):
    __tablename__ = 'PARTICIPATES_IN'

    Member_ID = db.Column(db.Integer, db.ForeignKey('MEMBER.Member_ID', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    Workout_ID = db.Column(db.Integer, db.ForeignKey('WORKOUT.Workout_ID', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)

    def __repr__(self):
        return f'<ParticipatesIn Member:{self.Member_ID} Workout:{self.Workout_ID}>'
