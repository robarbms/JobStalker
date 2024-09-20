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
}

export const JobContext = createContext({} as IContext);

function App() {
  let stored_jobs = useRef([]);
  const [jobs, setJobs] = useState([] as JobDetails[]);
  const [hideManager, setHideManager] = useState(false);
  const [onlyFrontend, setOnlyFrontend] = useState(false);

  const value: IContext = { 
    jobs,
    setJobs,
    hideManager,
    onlyFrontend,
    toggleOnlyFrontend: () => setOnlyFrontend(!onlyFrontend),
    toggleHideManager: () => setHideManager(!hideManager)
  };

  const getJobs = useCallback(async () => {
    const response = await fetch('http://localhost:5000/api');
    const data = await response.json();
    const data_options = data.map((job: JobDetails) => {
      if (job.description.match(/react|typescript/i)) {
        job.is_frontend = true;
      }
      if (job.title.match(/manager/i)) {
        job.is_manager = true;
      }
      return job;
    });

    stored_jobs.current = data_options;
    setJobs(data_options);
  }, []);

  useEffect(() => {
    getJobs();
  }, []);

  useEffect(() => {
    setJobs(stored_jobs.current.filter((job: JobDetails) => {
      if (hideManager && job.is_manager) {
        return false;
      }
      if (onlyFrontend && !job.is_frontend) {
        return false;
      }
      return true;
    }));
  }, [hideManager, onlyFrontend]);

  return (
    <JobContext.Provider value={value}>
      <div className="App">
        <header className="App-header">
          <h1>Job Stalker</h1>
        </header>
        <div className="job-list">
            <Filters />
            <Table></Table>
          </div>
      </div>
    </JobContext.Provider>
  );
}

export default App;
