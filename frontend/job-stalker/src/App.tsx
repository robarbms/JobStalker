import React, { createContext, useCallback, useEffect, useState } from 'react';
import './styles/site.css';
import { JobDetails } from './components/job';
import Table from './components/table';

interface IContext {
  jobs: JobDetails[],
  setJobs: React.Dispatch<React.SetStateAction<JobDetails[]>>,
}

export const JobContext = createContext({} as IContext);

function App() {
  const [jobs, setJobs] = useState([] as JobDetails[]);

  const value: IContext = { jobs, setJobs };

  const getJobs = useCallback(async () => {
    const response = await fetch('http://localhost:5000/api');
    const data = await response.json();
    setJobs(data);
    console.log(data);
  }, []);

  useEffect(() => {
    getJobs();
  }, []);

  return (
    <JobContext.Provider value={value}>
      <div className="App">
        <header className="App-header">
          <h1>Job Stalker</h1>
          <Table></Table>
        </header>
      </div>
    </JobContext.Provider>
  );
}

export default App;
