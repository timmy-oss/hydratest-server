from .import users, courses, exams, results, sessions
from lib.db import redis_db

redis_db.json().set("users", "$",  [],  nx =True)
redis_db.json().set("courses", "$",  [],  nx =True)
redis_db.json().set("course_questions", "$",  [],  nx =True)
redis_db.json().set("exams", "$",  [],  nx =True)
redis_db.json().set("examresponses", "$",  [],  nx =True)
redis_db.json().set("results", "$",  [],  nx =True)




