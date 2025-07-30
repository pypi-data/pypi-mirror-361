
class Course:
    def __init__(self, name, duration, link):
        self.name = name
        self.duration = duration
        self.link = link
    
    
    def __repr__(self):
        return f"{self.name} [{self.duration}] ({self.link})"

courses = [
    Course("Introducción a Linux", 15, "https://hack4u.io/cursos/introduccion-a-linux/"),
    Course("Personalización de Linux", 3, "https://hack4u.io/cursos/personalizacion-de-entorno-en-linux/"),
    Course("Introducción al Hacking", 53, "https://hack4u.io/cursos/introduccion-al-hacking/")
]

def list_courses():
    for course in courses:
        print(course)


def search_course_by_name(name):
    return list(filter(lambda x: x.name == name, courses))

if __name__ == "__main__":
    print("1")
    print(search_course_by_name("Introducción a Linux"))
    print("2")
    print(search_course_by_name("Introducción a Linu"))
