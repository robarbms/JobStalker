from scrapers import getAllJobs

def main():
    jobs = getAllJobs()
    print(len(jobs))

if __name__ == "__main__":
    main()
