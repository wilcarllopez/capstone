from marshmallow import fields, Schema
from . import db


class FileModel(db.Model):
    __tablename__ = 'safe_files'
    file_id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(128), unique=True, nullable=False)
    size = db.Column(db.Integer, nullable=False)
    sha1 = db.Column(db.String(40), unique=True, nullable=True)
    md5 = db.Column(db.String(32), unique=True, nullable=True)
    filetypes = db.Column(db.String(10))

    def __init__(self, data):
        self.filename = data.get('filename')
        self.size = data.get('size')
        self.sha1 = data.get('sha1')
        self.md5 = data.get('md5')
        self.filetypes = data.get('filetypes')

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
    def get_all_files():
        return FileModel.query.all()

    @staticmethod
    def get_one_file_md5(md5):
        return FileModel.query.filter(FileModel.md5 == md5).first()

    @staticmethod
    def get_one_file_sha(sha1):
        return FileModel.query.filter(FileModel.sha1 == sha1).first()

    def __repr(self):
        return '<id {}>'.format(self.id)


class FileSchema(Schema):
    file_id = fields.Int(dump_only=True)
    filename = fields.String(required=True)
    size = fields.Int(required=True)
    sha1 = fields.String(required=True)
    md5 = fields.String(required=True)
    filetypes = fields.String(required=False)
