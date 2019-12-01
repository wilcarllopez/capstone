from marshmallow import fields, Schema
from . import db
# from sqlalchemy.dialects.postgresql import UUID

class JobModel(db.Model):
    __tablename__ = 'jobs'
    file_id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(128), unique=True, nullable=False)
    job_id = db.Column(UUID(as_uuid=True), unique=True, nullable=False)
    states = db.relationship('StateModel', backref='jobs', lazy=True, cascade="all, delete-orphan")

    def __init__(self, data):
        self.job_id = data.get('job_id')
        self.app_name = data.get('app_name')

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        for key, item in data.items():
            setattr(self, key, item)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all_jobs():
        return JobModel.query.all()

    @staticmethod
    def get_one_job(job_id):
        return JobModel.query.filter(JobModel.job_id == job_id).first()

    def __repr(self):
        return '<id {}>'.format(self.id)


class JobSchema(Schema):
    id = fields.Int(dump_only=True)
    job_id = fields.UUID(required=True)
    states = fields.Nested(StateSchema, many=True)