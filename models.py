from app import db

class BlueButtonCaseTracking(db.Model):
    __tablename__ = 'bb-case-tracking'
    requestID = db.Column(db.INTEGER, primary_key=True)
    caseID = db.Column(db.INTEGER, db.ForeignKey('case.caseID'), nullable=False)
    deviceID = db.Column(db.TEXT)
    longitude = db.Column(db.REAL)
    latitude = db.Column(db.REAL)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
    resolved = db.Column(db.INTEGER)
    case = db.relationship('Case', backref='locations', lazy=True)
    
    def __repr__(self):
        return "ID: {} - [{}] Lat {}, Long {}, Resolved: {}".format(self.caseID, self.date, self.latitude, self.longitude, self.resolved)

class Case(db.Model):
    __tablename__ = 'case'
    caseID = db.Column(db.INTEGER, primary_key=True)

    def __repr__(self):
        return "ID <{}>".format(self.caseID)

class Numbers(db.Model):
    __tablename__ = 'numbers'
    name = db.Column(db.TEXT, primary_key=True)
    number = db.Column(db.TEXT)
    onCampus = db.Column(db.INTEGER)
    allDay = db.Column(db.INTEGER)
    description = db.Column(db.TEXT)

    def __repr__(self):
        return "Number <{}>".format(self.name)
