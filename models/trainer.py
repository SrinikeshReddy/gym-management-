from . import db

class Trainer(db.Model):
    __tablename__ = 'TRAINER'

    Trainer_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(100), nullable=False)
    Phone = db.Column(db.String(15), nullable=False)
    Email = db.Column(db.String(100), nullable=False, unique=True)
    Specialization = db.Column(db.String(100), nullable=False)
    Experience_Years = db.Column(db.Integer, nullable=False, default=0)
    Salary = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)

    # 1:N Relationships
    certifications = db.relationship('TrainerCertification', backref='trainer', cascade='all, delete-orphan', lazy=True)
    workouts = db.relationship('Workout', backref='trainer', lazy=True)
    payments = db.relationship('Payment', backref='trainer', lazy=True)

    def __repr__(self):
        return f'<Trainer {self.Trainer_ID}: {self.Name}>'


class TrainerCertification(db.Model):
    __tablename__ = 'TRAINER_CERTIFICATION'

    Trainer_ID = db.Column(db.Integer, db.ForeignKey('TRAINER.Trainer_ID', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    Certification = db.Column(db.String(100), primary_key=True)

    def __repr__(self):
        return f'<TrainerCertification {self.Trainer_ID}: {self.Certification}>'
