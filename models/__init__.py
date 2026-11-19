from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .member import Member, MemberAddress
from .trainer import Trainer, TrainerCertification
from .workout import Workout, ParticipatesIn
from .membership import Membership
from .payment import Payment
from .attendance import Attendance, AttendanceRemarks

__all__ = [
    'db',
    'Member',
    'MemberAddress',
    'Trainer',
    'TrainerCertification',
    'Workout',
    'ParticipatesIn',
    'Membership',
    'Payment',
    'Attendance',
    'AttendanceRemarks'
]
