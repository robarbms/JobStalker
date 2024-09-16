from .apple import getAppleJobs
from .netflix import getNetflixJobs

def getAllJobs():
    jobs = []
    jobs += getAppleJobs()
    jobs += getNetflixJobs()

    return jobs