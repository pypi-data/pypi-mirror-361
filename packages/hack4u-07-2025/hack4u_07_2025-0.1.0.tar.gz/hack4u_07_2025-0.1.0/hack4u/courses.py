#!/usr/bin/python3

class Course:
    def __init__(self,name,duration,link):
        self.name=name
        self.duration=duration
        self.link=link
    
    def __str__(self):
        return f"Curso: {self.name}\n\n\tDuracion: {self.duration}\n\tLink: {self.link}\n"

courses = [
    Course("Introduccion a Linux", 15,"1"),
    Course("Personalizacion Linux",3,"2"),
    Course("Introduccion a la ciberseguridad",52,"3")
]

def listarCursos():
    for course in courses:
        print(course)

def findCourseByName():
    flag=False
    courseName= input("Nombre de Curso a Buscar: ")
    for course in courses:
        if courseName == course.name:
            flag=True
            break
    if flag:
        print(f"[{courseName}] encontrado")
        print(course)
    else:
        print(f"Curso: [{courseName}] no encontrado.")

def totalDuration():
    return sum(course.duration for course in courses)
