from .courses import courses
from functools import reduce

def total_duration():
    return reduce(lambda suma, x: suma + x.duration, courses, 0)
    # return sum(course for course in courses)
if __name__ == "__main__":
    total_duration()
