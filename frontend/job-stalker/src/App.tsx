import React, { createContext, useCallback, useEffect, useState, useRef, createRef } from 'react';
import './styles/site.css';
import { JobDetails } from './components/job';
import Table from './components/table';
import CompanyChart from './components/charts/companies';
import WeekChart from './components/charts/week';
import AllTrendChart from './components/charts/allTrend';
import FilterSystem from './components/filterSystem';

type Filter = {
  title_include: string;
  title_exclude: string;
  description_include: string;
  description_exclude: string;
  companies: string[];
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
    title_include: "",
    title_exclude: "",
    description_include: "",
    description_exclude: "",
    companies: companies
  } as Filter);
  const jobHandler = useRef<NodeJS.Timeout|null>();
  const [jobsToday, setJobsToday] = useState<JobDetails[]>([]);


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
    const response = await fetch('http://localhost:5000/api');
    let data = await response.json();
    data = data.sort((a: any, b: any) => new Date(a.date_posted) > new Date(b.date_posted) ? -1 : 1);
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
    if (jobHandler.current !== null) {
      clearTimeout(jobHandler.current);
    }
    jobHandler.current = setTimeout(getJobs, 5000);
  };

  const containsText = (text: string, search: string) => {
    const searchTerms = search.split(' ');
    if (searchTerms.length === 0) return true; // No filter, so include it!
    let containsText = false;
    searchTerms.forEach((term: string) => {
      if(text.toLowerCase().indexOf(term.toLowerCase()) >= 0) {
        containsText = true;
      }
    });
    return containsText;
  }

  const doesntContainText = (text: string, search: string) => {
    return !containsText(text, search);
  }

  const applyFilters = useCallback(() => {
     let filteredJobs = allJobs;
     if (filter.companies.length > 0) {
      filteredJobs = filteredJobs.filter(job => filter.companies.includes(job.company));
     }
     if(filter.title_include) {
        filteredJobs = filteredJobs.filter(job => containsText(job.title, filter.title_include)); 
     }
     if(filter.description_include) {
       filteredJobs = filteredJobs.filter(job => containsText(job.description, filter.description_include));
     }
     if (filter.title_exclude) {
      filteredJobs = filteredJobs.filter(job => doesntContainText(job.title, filter.title_exclude));
     }
     if (filter.description_exclude) {
      filteredJobs = filteredJobs.filter(job => doesntContainText(job.description, filter.description_exclude));
     }
     setJobs(filteredJobs);
  }, [allJobs, filter]);

  const filterChanged = (e: React.ChangeEvent<HTMLFormElement>) => {
    const {value, name} = e.target;
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
  }, [filter, allJobs, applyFilters])

  return (
    <JobContext.Provider value={value}>
      <div className="App">
        <header className="App-header">
          <h1>
            Job Stalker
            <label>Last updated: </label><span className="update_time">{lastUpdated.toLocaleString()}</span>
            <label>Total Jobs: </label><span className="total_jobs">{allJobs.length}</span>
            <label>Jobs found today:</label><span className="jobs_today">{jobsToday.length}</span>
          </h1>
        </header>
        <AllTrendChart />
        <FilterSystem filterChanged={filterChanged} toggleCompany={toggleCompany} />
        <CompanyChart />
        <WeekChart />
        <div className="job-list-container">
          <div className="job-list-header">
            <div className="job-count">
              {jobs.length} / {allJobs.length} jobs
            </div>
          </div>
            <Table></Table>
          </div>
      </div>
    </JobContext.Provider>
  );
}

export default App;
