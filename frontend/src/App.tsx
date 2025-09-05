import React, { createContext, useCallback, useEffect, useState, useRef, createRef } from 'react';
import './styles/site.css';
import { JobDetails } from './components/job';
import Table from './components/table';
import CompanyChart from './components/charts/companies';
import WeekChart from './components/charts/week';
import AllTrendChart from './components/charts/allTrend';
import { getTagColors } from "./components/tags/tagColors";
import Cards from './components/job_card/Cards';
import Switcher from './components/layout/switcher';
import { dateOffset, dateToString } from './utils/date';
import DateFilters from './components/search/dateFilters';
import CompanyFilters from './components/search/companyFilters';
import Keywords, { KeywordGroupName } from './components/charts/keywords';
import TagFilters from './components/search/tagFilters';
import { parseTags } from './utils/data';
import TextSearch from './components/search/textSearch';

export type Filter = {
  title: string;
  description: string;
  summary: string;
  companies: string[];
  dateStart: string;
  dateEnd: string;
  focusedCompany: string | null;
  tagsInclude: string[];
  tagsExclude: string[];
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
  const [allJobs, setAllJobs] = useState<JobDetails[]>([]);
  const [jobs, setJobs] = useState<JobDetails[]>([]);
  const [ prevJobs, setPrevJobs ] = useState<JobDetails[]>([])
  const [ companies, setCompanies] = useState<string[]>([]);
  const [ lastUpdated, setLastUpdated] = useState<Date>(new Date());
  const [ tagData, setTagData] = useState<any>({});
  const [ filter, setFilter ] = useState<Filter>({
    title: "",
    description: "",
    summary: "",
    companies: companies,
    dateStart: dateToString(dateOffset({days: -6})),
    dateEnd: dateToString(new Date()),
    focusedCompany: null,
    tagsInclude: [],
    tagsExclude: []
  } as Filter);
  const jobHandler = useRef<NodeJS.Timeout|null>();
  const [jobsToday, setJobsToday] = useState<JobDetails[]>([]);
  const [ lastScraped, setLastScraped ] = useState<Date|null>(null);
  const [ tagList, setTagList ] = useState({});
  const [ activeTab, setActiveTab ] = useState<KeywordGroupName>('Developer');

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
      const api_url = window.location.protocol + "//" + window.location.hostname + ":5000/api";
      const response = await fetch(api_url);
      let data = await response.json();
      data.sort((a: any, b: any) => new Date(b.date_posted).getTime() - new Date(a.date_posted).getTime())
      data = data.map((job: JobDetails) => {
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
      setFilter({...filter, companies});
      setAllJobs(data);
      setLastUpdated(new Date());
      const today = new Date();
      today.setHours(0, 0, 0, 0); // Set to midnight of the current day
      setJobsToday(data.filter((job: JobDetails) => new Date(job.created_at).getTime() >= today.getTime()));
      let mostRecentScraped = 0;
      data.forEach((job: JobDetails) => {
        mostRecentScraped = Math.max(new Date(job.created_at).getTime(), mostRecentScraped);
      });
      setLastScraped(new Date(mostRecentScraped));
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
     if (filter.focusedCompany) {
        filteredJobs = filteredJobs.filter(job => job.company === filter.focusedCompany);
     }
     else if (filter.companies.length > 0) {
      filteredJobs = filteredJobs.filter(job => filter.companies.includes(job.company));
     }
     if(filter.title) {
        filteredJobs = filteredJobs.filter(job => textSearch(job.title, filter.title)); 
     }
     if(filter.description) {
       filteredJobs = filteredJobs.filter(job => textSearch(job.description, filter.description));
     }
     if(filter.summary) {
      filteredJobs = filteredJobs.filter(job => textSearch(job.summary, filter.summary));
     }
     if (filter.dateStart) {
      const ds = new Date(filter.dateStart).getTime();
      const dateEnd = new Date(filter.dateEnd + "T01:00:00");
      dateEnd.setHours(23, 59, 59);
      const de = filter.dateEnd ? dateEnd.getTime() : new Date().getTime();
      const diff = Math.abs(de - ds);
      const prevFilteredJobs = filteredJobs.filter(job => new Date(job.date_posted).getTime() < ds && new Date(job.date_posted).getTime() >= ds - diff);
      setPrevJobs(prevFilteredJobs);
      filteredJobs = filteredJobs.filter(job => new Date(job.date_posted).getTime() >= ds && new Date(job.date_posted).getTime() <= de);
    }
    const parsedTags = parseTags(filteredJobs);
    setTagData(parsedTags);
    if (filter.tagsInclude.length > 0) {
      filteredJobs = filteredJobs.filter(job => (job.tags as string[]).some((tag: string) => filter.tagsInclude.includes(tag)));
    }
    if (filter.tagsExclude.length > 0) {
      filteredJobs = filteredJobs.filter(job => !(job.tags as string[]).some((tag: string) => filter.tagsExclude.includes(tag)));
    }
    setJobs(filteredJobs);
  }, [allJobs, filter]);

  const filterChanged = (e: React.ChangeEvent<HTMLFormElement>) => {
    let data = {};
    if ('target' in e) {
      const {name, value} = e.target;
      data = {[name]: value}
    }
    else {
      data = e;
    }
    console.log(data);
    setFilter({...filter, ...data});
  }

  const toggleCompany = (company: string) => () => {
    let filter_companies = filter.companies.includes(company) ? filter.companies.filter(c => c !== company) : [...filter.companies, company];
    if (filter_companies.length === 0) {
      filter_companies = companies;
    }
    const updatedFilter = {...filter, companies: filter_companies};
    setFilter(updatedFilter);
  }

  const focusCompany = (company: string) => () => {
    const updatedFilter = Object.assign({}, filter, {focusedCompany: filter.focusedCompany === company ? null : company});
    setFilter(updatedFilter);
  }

  const filterTags = (tag: string | string[], action="include") => {
    const filter_cpy = {...filter};
    if (action === 'clear') {
      if (tag === 'clear') {
        filter_cpy.tagsInclude = [];
        filter_cpy.tagsExclude = [];
      }
      else if (Array.isArray(tag)) {
        filter_cpy.tagsInclude = filter_cpy.tagsInclude.filter(t => !tag.includes(t))
      }
    }
    else if (action === "include") {
      if (Array.isArray(tag)) {
        tag.forEach((curr) => {
          if (!filter_cpy.tagsInclude.includes(curr)) {
            filter_cpy.tagsInclude.push(curr);
          }
        })
      }
      else if (!filter_cpy.tagsInclude.includes(tag)) {
        filter_cpy.tagsInclude.push(tag);
        filter_cpy.tagsExclude = filter_cpy.tagsExclude.filter(tag_a => tag_a !== tag);
      }
      else {
        filter_cpy.tagsInclude = filter_cpy.tagsInclude.filter(tag_a => tag_a !== tag);
      }
    }
    else {
      if (Array.isArray(tag)) {
        filter_cpy.tagsExclude = filter_cpy.tagsExclude.filter(tag_a => !tag.includes(tag_a))
      }
      else if (!filter_cpy.tagsExclude.includes(tag)) {
        filter_cpy.tagsExclude.push(tag);
        filter_cpy.tagsInclude = filter_cpy.tagsInclude.filter(tag_a => tag_a !== tag);
      }
      else {
        filter_cpy.tagsExclude = filter_cpy.tagsExclude.filter(tag_a => tag_a !== tag);
      }
    }
    setFilter(filter_cpy);
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
        <div className="col-layout">
          <div className="job-lists">
            <div className="job-list-container">
              <Switcher title="Search Results" job_count={jobs.length} options={[
                {
                  'tab': 'Cards',
                  'content': <Cards jobs={jobs} tag_colors={tag_colors} filterTags={filterTags} filter={filter} />
                },
                {
                  'tab': 'Table',
                  'content': <Table />
                },
                {
                  'tab': 'Graphs',
                  'content':  <><div className="job-search">
                                <CompanyChart jobs={jobs} />
                                <WeekChart jobs={jobs} filter={filter} prevJobs={prevJobs} />
                              </div>
                              <div className="trends">
                                <AllTrendChart jobs={jobs} />
                                <Keywords 
                                  parsedTagData={tagData}
                                  jobs={jobs}
                                  filter={filter}
                                  filterTags={filterTags}
                                  tagList={tagList}
                                  setTagList={setTagList}
                                  activeTab={activeTab}
                                  setActiveTab={setActiveTab}
                                  tagColors={tag_colors as {[tag: string]: string}} />
                              </div>
                            </>
                }
              ]} />
            </div>
          </div>
          <div className="job-charts">
            <TextSearch filterChanged={filterChanged} />
            <DateFilters filterChanged={filterChanged} />
            <CompanyFilters toggleCompany={toggleCompany} focusCompany={focusCompany} setFilter={setFilter} />
            <TagFilters tagData={(tagList as any)['Developer']} filter={filter} filterTags={filterTags} />
          </div>
        </div>
      </div>
    </JobContext.Provider>
  );
}

export default App;
