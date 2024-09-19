import React, { useContext, useState } from 'react';
import { JobContext } from '../App';
import Job, { JobDetails } from './job';

export default function Table () {
    const {jobs, setJobs} = useContext(JobContext);
    const sorted_jobs = jobs.sort((a: JobDetails, b: JobDetails) => new Date(b.date_posted).getTime() - new Date(a.date_posted).getTime());
    const [showCount, setShowCount] = useState(20);

    const handleShowMore = () => {
        setShowCount(showCount + 20);
    }

    const handleShowLess = () => {
        setShowCount(20);
    }

    return(
        <div className="job-list">
        <table>
            <thead>
                <tr>
                    <th>Company</th>
                    <th>Date Posted</th>
                    <th>Job Title</th>
                </tr>
            </thead>
            <tbody>
                {sorted_jobs.filter((x, idx) => showCount < 0 || idx < showCount).map((job, idx) => <Job key={idx} {...job} />)}
            </tbody>
        </table>
        {showCount < sorted_jobs.length && 
            <button className="show-more" onClick={handleShowMore}>Show More Jobs</button>
        }
        {showCount >= sorted_jobs.length &&
            <button className="show-more" onClick={handleShowLess}>Show Less Jobs</button>
        }
        </div>
    )
}
