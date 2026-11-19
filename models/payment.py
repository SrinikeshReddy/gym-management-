from . import db

class Payment(db.Model):
    __tablename__ = 'PAYMENT'

    Payment_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Membership_ID = db.Column(db.Integer, db.ForeignKey('MEMBERSHIP.Membership_ID', ondelete='SET NULL', onupdate='CASCADE'), nullable=True)
    Trainer_ID = db.Column(db.Integer, db.ForeignKey('TRAINER.Trainer_ID', ondelete='SET NULL', onupdate='CASCADE'), nullable=True)
    Amount = db.Column(db.Numeric(10, 2), nullable=False)
    Payment_Method = db.Column(db.String(20), nullable=False)
    Payment_Date = db.Column(db.Date, nullable=False)
    Due_Date = db.Column(db.Date, nullable=True)
    Status = db.Column(db.String(20), nullable=False, default='Success')
    Transaction_ID = db.Column(db.String(100), unique=True, nullable=True)
    Invoice_Number = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f'<Payment {self.Payment_ID}: {self.Invoice_Number} - {self.Amount}>'
