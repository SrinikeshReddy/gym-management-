from . import db

class Member(db.Model):
    __tablename__ = 'MEMBER'

    Member_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(100), nullable=False)
    Gender = db.Column(db.String(10), nullable=False)
    Date_of_Birth = db.Column(db.Date, nullable=False)
    Age = db.Column(db.Integer, nullable=False)
    Phone = db.Column(db.String(15), nullable=False)
    Email = db.Column(db.String(100), nullable=False, unique=True)
    Emergency_Contact = db.Column(db.String(15), nullable=False)
    Join_Date = db.Column(db.Date, nullable=False)
    Status = db.Column(db.String(20), nullable=False, default='Active')
    Blood_Group = db.Column(db.String(5), nullable=False)
    Password = db.Column(db.String(255), nullable=True, default='member123')

    # 1:N Relationships
    addresses = db.relationship('MemberAddress', backref='member', cascade='all, delete-orphan', lazy=True)
    memberships = db.relationship('Membership', backref='member', cascade='all, delete-orphan', lazy=True)
    attendances = db.relationship('Attendance', backref='member', cascade='all, delete-orphan', lazy=True)
    
    # N:M Relationship to Workout via ParticipatesIn
    participations = db.relationship('ParticipatesIn', backref='member', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):
        return f'<Member {self.Member_ID}: {self.Name}>'


class MemberAddress(db.Model):
    __tablename__ = 'MEMBER_ADDRESS'

    Member_ID = db.Column(db.Integer, db.ForeignKey('MEMBER.Member_ID', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    Address = db.Column(db.String(255), primary_key=True)

    def __repr__(self):
        return f'<MemberAddress {self.Member_ID}: {self.Address}>'
