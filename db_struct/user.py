from flask_login import UserMixin

class User(UserMixin):
    def __init__(self,id,fname,lname,email,mobile,username,password,created_at,updated_at,deleted_at):
        self.id = id
        self.fname = fname
        self.lname = lname
        self.email = email
        self.mobile = mobile
        self.username = username
        self.password = password
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted_at = deleted_at
