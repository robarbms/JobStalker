from apscheduler.schedulers.blocking import BlockingScheduler
from .getAllJobs import getAllJobs

def job():
    scheduler = BlockingScheduler()
    scheduler.add_job(getAllJobs, 'interval', hours=1)
    scheduler.start()
