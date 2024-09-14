from scrapers import getNetflixJobs

def main():
    print("Executing main()ven")
    jobs = getNetflixJobs()
    print(jobs)

if __name__ == "__main__":
    main()
