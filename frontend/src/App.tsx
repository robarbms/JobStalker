import React, { createContext, useCallback, useEffect, useState, useRef, createRef } from 'react';
import './styles/site.css';
import { JobDetails } from './components/job';
import Table from './components/table';
import CompanyChart from './components/charts/companies';
import WeekChart from './components/charts/week';
import AllTrendChart from './components/charts/allTrend';
import TagsOverTime from './components/tags/tagsOverTime';
import FilterSystem from './components/search/filterSystem';
import { getTagColors } from "./components/tags/tagColors";
import Card from './components/job_card/Card';
import Cards from './components/job_card/Cards';
import ApiService from './components/api_service';
import Switcher from './components/layout/switcher';
import { dateOffset, DateOffsetObj, dateToString } from './utils/date';

type Filter = {
  title: string;
  description: string;
  companies: string[];
  dateStart: string;
  dateEnd: string;
}
interface IContext {
  allJobs: JobDetails[],
  jobs: JobDetails[],
  setJobs: React.Dispatch<React.SetStateAction<JobDetails[]>>,
  companies: string[];
  setCompanies: React.Dispatch<React.SetStateAction<string[]>>;
  lastUpdated: Date;
  filter: Filter;
  setFilter: React.Dispatch<React.SetStateAction<Filter>>;
}

export const JobContext = createContext({} as IContext);

function App() {
  const [allJobs, setAllJobs] = useState([] as JobDetails[]);
  const [jobs, setJobs] = useState([] as JobDetails[]);
  const [ companies, setCompanies] = useState([] as string[]);
  const [ lastUpdated, setLastUpdated] = useState(new Date());
  const [ filter, setFilter ] = useState<Filter>({
    title: "",
    description: "",
    companies: companies,
    dateStart: dateToString(dateOffset({weeks: -1})),
    dateEnd: dateToString(new Date())
  } as Filter);
  const jobHandler = useRef<NodeJS.Timeout|null>();
  const [jobsToday, setJobsToday] = useState<JobDetails[]>([]);
  const [ lastScraped, setLastScraped ] = useState<Date|null>(null);


  const value: IContext = { 
    allJobs,
    jobs,
    setJobs,
    companies,
    setCompanies,
    lastUpdated,
    filter,
    setFilter,
  };

  const getJobs = async () => {
    try {
      const response = await fetch('http://localhost:5000/api');
      let data = await response.json();
      data = data.sort((a: any, b: any) => new Date(a.date_posted) > new Date(b.date_posted) ? -1 : 1)
        .map((job: JobDetails) => {
          job.tags = JSON.parse(job.tags as string) as any[];
          return job;
        });
      
      const companies = data.reduce((c: string[], job: JobDetails) => {
          if (!c.includes(job.company)) {
            c.push(job.company);
          }
          return c;
      }, []).sort();
      setCompanies(companies);
      setAllJobs(data);
      setLastUpdated(new Date());
      const today = new Date();
      today.setHours(0, 0, 0, 0); // Set to midnight of the current day
      setJobsToday(data.filter((job: JobDetails) => new Date(job.created_at).getTime() >= today.getTime()));
      const mostRecentScraped = new Date(data.sort((a: any, b: any) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())[0]['created_at']);
      mostRecentScraped.setTime(mostRecentScraped.getTime()); // + 1000 * 60 * 60 * 7); // Add 7 hours to the timestamp
      setLastScraped(mostRecentScraped);
      if (jobHandler.current !== null) {
        clearTimeout(jobHandler.current);
      }
      jobHandler.current = setTimeout(getJobs, 1000 * 60 * 60 * 2);
    }
    catch (err) {
      // No response from the API
      // Either the API is down or there is no content in jobs.db yet
      if (jobHandler.current !== null) {
        clearTimeout(jobHandler.current);
      }
      // Wait 10 minutes and try again
      jobHandler.current = setTimeout(getJobs, 1000 * 60 * 10);
    }
  };

  const textSearch = (text: string, search: string) => {
    text = text.toLowerCase().trim();
    search = search.toLowerCase().trim();
    const joins = search.split(",").map((t: string) => t.trim());
    return joins.reduce((contains: boolean, join_term: string) => {
      if (contains) return true;
      const unions = join_term.split(" ").map((t: string) => t.trim());
      return unions.reduce((contains: boolean, union_term: string) => {
        union_term = union_term.trim();
        if (contains === false) return false;
        let include = union_term.indexOf("!") !== 0;
        union_term = union_term.replace(/^!/, "").trim()
        return include ? text.match("\\b" + union_term + "\\b") !== null : text.match("\\b" + union_term + "\\b") === null;
      }, true);
    }, false);
  }

  const applyFilters = useCallback(() => {
     let filteredJobs = allJobs;
     if (filter.companies.length > 0) {
      filteredJobs = filteredJobs.filter(job => filter.companies.includes(job.company));
     }
     if(filter.title) {
        filteredJobs = filteredJobs.filter(job => textSearch(job.title, filter.title)); 
     }
     if(filter.description) {
       filteredJobs = filteredJobs.filter(job => textSearch(job.description, filter.description));
     }
     if (filter.dateStart) {
      filteredJobs = filteredJobs.filter(job => new Date(job.date_posted).getTime() > new Date(filter.dateStart).getTime());
     }
     setJobs(filteredJobs);
  }, [allJobs, filter]);

  const filterChanged = (e: React.ChangeEvent<HTMLFormElement>) => {
    const {value, name} = e.target;
    console.log({name, value});
    setFilter({...filter, [name]: value});
  }

  const toggleCompany = (company: string) => () => {
    let filter_companies = filter.companies.includes(company) ? filter.companies.filter(c => c !== company) : [...filter.companies, company];
    if (filter_companies.length === 0) {
      filter_companies = companies;
    }
    const updatedFilter = {...filter, companies: filter_companies};
    setFilter(updatedFilter);
  }

  useEffect(() => {
    getJobs();
    return () => {
      if (jobHandler.current) {
        clearTimeout(jobHandler.current);
      }
    }
  }, []);

  useEffect(() => {
    applyFilters();
  }, [filter, allJobs, applyFilters]);

  const getStatus = (time: Date | null, scale: number = 1000 * 60 * 60 * 2.2, map: any = {
    success: 12,
    warn: 36,
    error: 999
  }) => {
      if (time) {
        const now = new Date().getTime();
        const compare = time?.getTime();
        const diff = (now - compare)  / scale;

        for (let key in map) {
          if (diff < map[key]) {
            return key;
          }
      }
      return "";
    }
  }
  const tag_colors = getTagColors();

  return (
    <JobContext.Provider value={value}>
      <div className="App">
        <header className="App-header">
          <h1>
            Job Stalker
            <label>Last updated: </label><span className={`update_time ${getStatus(lastUpdated, 1000 * 5)}`}>{lastUpdated.toLocaleString()}</span>
            <label>Total Jobs: </label><span className="total_jobs">{allJobs.length}</span>
            <label>Jobs found today:</label><span className="jobs_today">{jobsToday.length}</span>
            <label>Last scraped: </label><span className={`last_scraped ${getStatus(lastScraped)}`}>{lastScraped && lastScraped.toLocaleString()}</span>
          </h1>
        </header>
        {jobs && jobs.length > 0 &&
          <div className="col-layout">
            <div className="job-lists">
              <div className="job-list-container">
                <h2>
                  Search Results
                  <span className="meta">
                    <label>{jobs.length} / {allJobs.length} jobs</label>
                  </span>            
                </h2>
                <Switcher options={[
                  {
                    'tab': 'Cards',
                    'content': <Cards jobs={jobs} tag_colors={tag_colors} />
                  },
                  {
                    'tab': 'Table',
                    'content': <Table />
                  }
                ]} />
              </div>
            </div>
            <div className="job-charts">
              <FilterSystem filterChanged={filterChanged} toggleCompany={toggleCompany} />
              <div className="job-search">
                <CompanyChart jobs={jobs} />
                <WeekChart />
              </div>
              <div className="trends">
                <AllTrendChart jobs={jobs} />
                <TagsOverTime jobs={jobs} />
              </div>
            </div>
          </div>
        }
        {( !jobs || jobs.length < 1 ) &&
          <ApiService />
        }
      </div>
    </JobContext.Provider>
  );
}

export default App;
