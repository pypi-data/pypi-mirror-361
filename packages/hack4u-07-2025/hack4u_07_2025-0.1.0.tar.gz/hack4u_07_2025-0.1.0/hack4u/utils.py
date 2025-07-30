from .courses import *

def totalDuration():
    return sum(course.duration for course in courses)
