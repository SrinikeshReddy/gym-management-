from . import db

class Membership(db.Model):
    __tablename__ = 'MEMBERSHIP'

    Membership_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Member_ID = db.Column(db.Integer, db.ForeignKey('MEMBER.Member_ID', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    Plan_Name = db.Column(db.String(50), nullable=False)
    Plan_Description = db.Column(db.Text, nullable=True)
    Start_Date = db.Column(db.Date, nullable=False)
    End_Date = db.Column(db.Date, nullable=False)
    Amount = db.Column(db.Numeric(10, 2), nullable=False)
    Status = db.Column(db.String(20), nullable=False, default='Active')
    Duration_Days = db.Column(db.Integer, nullable=False, default=0)

    # Relationships
    payments = db.relationship('Payment', backref='membership', lazy=True)

    @property
    def total_paid(self):
        return sum(float(p.Amount) for p in self.payments if p.Status == 'Success')

    @property
    def balance_due(self):
        total = float(self.Amount) if self.Amount else 0.0
        return max(0.0, round(total - self.total_paid, 2))

    @property
    def is_fully_paid(self):
        return self.balance_due <= 0.01

    def __repr__(self):
        return f'<Membership {self.Membership_ID}: Member {self.Member_ID} - {self.Plan_Name}>'
