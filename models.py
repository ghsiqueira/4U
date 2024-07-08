from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, username, _id):
        self.username = username
        self.id = _id

class PDF:
    def __init__(self, title, description, cover_image, filename, publish_date, uploaded_by):
        self.title = title
        self.description = description
        self.cover_image = cover_image
        self.filename = filename
        self.publish_date = publish_date
        self.uploaded_by = uploaded_by
        self._id = None

    def set_id(self, _id):
        self._id = _id
