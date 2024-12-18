import React, { useContext, useEffect, useState } from 'react';
import { JobContext } from '../App';
import Job, { JobDetails } from './job';

export default function Table () {
    let {jobs} = useContext(JobContext);
    const [showCount, setShowCount] = useState(100);
    const sortColumn: string = "";
    const setSortColumn = (column: string) => {}

    // jobs = jobs.filter((job, idx) => idx >= 12);


    const handleShowMore = () => {
        setShowCount(showCount + 100);
    }

    const handleShowLess = () => {
        setShowCount(100);
    }

    const handleSort = (column: string) => () => setSortColumn(column as keyof JobDetails);

    return(
        <div className="job-list">
        <table>
            <thead>
                <tr>
                    <th onClick={handleSort('company')}>
                        Company
                        {sortColumn === 'company' && <span>&#8595;</span>}
                    </th>
                    <th onClick={handleSort('date_posted')}>
                        Date Posted
                        {sortColumn === 'date_posted' && <span>&#8595;</span>}
                    </th>
                    <th onClick={handleSort('created_at')}>
                        Scraped
                        {sortColumn === 'created_at' && <span>&#8595;</span>}
                    </th>
                    <th onClick={handleSort('title')}>
                        Job Title
                        {sortColumn === 'title' && <span>&#8595;</span>}
                    </th>
                </tr>
            </thead>
            <tbody>
                {jobs.filter((x, idx) => showCount < 0 || idx < showCount).map((job, idx) => <Job key={idx} {...job} />)}
            </tbody>
        </table>
        {showCount < jobs.length && 
            <button className="show-more" onClick={handleShowMore}>Show More Jobs</button>
        }
        {showCount >= jobs.length &&
            <button className="show-more" onClick={handleShowLess}>Show Less Jobs</button>
        }
        </div>
    )
}
