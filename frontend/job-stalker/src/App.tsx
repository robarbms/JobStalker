import React, { createContext, useCallback, useEffect, useState, useRef } from 'react';
import './styles/site.css';
import { JobDetails } from './components/job';
import Table from './components/table';
import Filters from './components/filters';

interface IContext {
  jobs: JobDetails[],
  setJobs: React.Dispatch<React.SetStateAction<JobDetails[]>>,
  toggleHideManager: () => void;
  toggleOnlyFrontend: () => void;
  hideManager: boolean;
  onlyFrontend: boolean;
  companyFilter: string;
  setCompanyFilter: React.Dispatch<React.SetStateAction<string>>;
  sortColumn: keyof JobDetails;
  setSortColumn: React.Dispatch<React.SetStateAction<keyof JobDetails>>;
  companies: string[];
  setCompanies: React.Dispatch<React.SetStateAction<string[]>>;
  lastUpdated: Date;
}

export const JobContext = createContext({} as IContext);

function App() {
  let stored_jobs = useRef([]);
  const [jobs, setJobs] = useState([] as JobDetails[]);
  const [hideManager, setHideManager] = useState(true);
  const [onlyFrontend, setOnlyFrontend] = useState(true);
  const [ companyFilter, setCompanyFilterMaster] = useState("All");
  const [ sortColumn, setSortColumn ] = useState("created_at" as keyof JobDetails);
  const [ companies, setCompanies] = useState([] as string[]);
  const [ lastUpdated, setLastUpdated] = useState(new Date());

  const setCompanyFilter = (value: any) => {
    setCompanyFilterMaster(value);
  }

  const value: IContext = { 
    jobs,
    setJobs,
    hideManager,
    onlyFrontend,
    toggleOnlyFrontend: () => setOnlyFrontend(!onlyFrontend),
    toggleHideManager: () => setHideManager(!hideManager),
    companyFilter,
    setCompanyFilter,
    sortColumn,
    setSortColumn,
    companies,
    setCompanies,
    lastUpdated
  };

  const getJobs = async () => {
    const response = await fetch('http://localhost:5000/api');
    const data = await response.json();
    const data_options = data.map((job: JobDetails) => {
      if (job.description.match(/\W(react|typescript)\W/i)) {
        job.is_frontend = true;
      }
      if (job.title.match(/manager/i)) {
        job.is_manager = true;
      }
      return job;
    });

    stored_jobs.current = data_options;
    const companies = data_options.reduce((c: string[], job: JobDetails) => {
        if (!c.includes(job.company)) {
            c.push(job.company);
        }
        return c;
    }, []).sort();
    setCompanies(["All", ...companies]);
    const processed_jobs = processJobs(data_options, sortColumn, companyFilter, hideManager, onlyFrontend);
    setJobs(processed_jobs);
    setLastUpdated(new Date());
  };

  useEffect(() => {
    const updateJobs = () => {
      getJobs();
    }
    updateJobs();
    const jobHandle = setInterval(updateJobs, 5000);
    return () => clearInterval(jobHandle);
  }, [sortColumn, companyFilter, hideManager, onlyFrontend]);

  const processJobs = (jobs: JobDetails[], sortColumn: keyof JobDetails, companyFilter: string, hideManager: boolean, onlyFrontend: boolean) => {
    const sorted_jobs = jobs.sort((a: JobDetails, b: JobDetails) => {
      if (sortColumn === "date_posted" || sortColumn === "created_at") {
        const sort_a = new Date(a[sortColumn].replace(/ gmt/i, '')).getTime();
        const sort_b = new Date(b[sortColumn].replace(/ gmt/i, '')).getTime();
        return sort_a > sort_b ? -1 : 1;
      }
      if (sortColumn !== undefined && a !== undefined && b !== undefined && 
        sortColumn in a && sortColumn in b) {
        const sort_a = a[sortColumn];
        const sort_b = b[sortColumn];
        if (sort_a !== undefined && sort_b !== undefined) {
          return (sort_a as string).localeCompare(sort_b as string)
        }
      }
      return -1;
    });
    const filtered_jobs = sorted_jobs.filter((job: JobDetails) => {
      if (hideManager && job.is_manager) {
        return false;
      }
      if (onlyFrontend && !job.is_frontend) {
        return false;
      }
      if (companyFilter !=="All" && job.company!==companyFilter) {
        return false;
      }
      return true;
    });

    return filtered_jobs;
  };

  useEffect(() => {
    if (stored_jobs.current) {
      setJobs(processJobs(stored_jobs.current, sortColumn, companyFilter, hideManager, onlyFrontend));
    }
  }, [hideManager, onlyFrontend, companyFilter, sortColumn]);

  return (
    <JobContext.Provider value={value}>
      <div className="App">
        <header className="App-header">
          <h1>Job Stalker</h1>
          <label>Last updated: </label><span className="update_time">{lastUpdated.toString()}</span>
        </header>
        <div className="job-list-container">
          <div className="job-list-header">
            <div className="job-count">
              {jobs.length} / {stored_jobs.current.length} jobs
            </div>
            <Filters />
          </div>
            <Table></Table>
          </div>
      </div>
    </JobContext.Provider>
  );
}

export default App;
