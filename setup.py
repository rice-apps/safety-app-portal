# setup.py
# (c) Rice Apps 2017

import json
from app import app, db
from models import Number

def insert_number():
    data = []
    numbers = json.load(open('data/numbers_data.json'))['data']
    for n in numbers:
        row = Number(name=n['name'], number=n['number'], on_campus=n['onCampus'], all_day=n['allDay'], description=n['description'])
        db.session.add(row)
    db.session.commit()

def populate_db():
	# add numbers
	insert_number()

if __name__ == '__main__':
	populate_db()