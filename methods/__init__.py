from .import users, courses, exams
from lib.db import redis_db


redis_db.json().set("users", "$",  [],  nx =True)
redis_db.json().set("courses", "$",  [],  nx =True)
redis_db.json().set("exams", "$",  [],  nx =True)


