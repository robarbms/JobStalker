import React, { useContext } from 'react';
import { JobContext } from '../App';
import Job, { JobDetails } from './job';

export default function Table () {
    const {jobs, setJobs} = useContext(JobContext);
    const sorted_jobs = jobs.sort((a: JobDetails, b: JobDetails) => new Date(b.date_posted).getTime() - new Date(a.date_posted).getTime());

    return(
        <table>
            <thead>
                <tr>
                    <th>Company Name</th>
                    <th>Job Title</th>
                    <th>Date Posted</th>
                </tr>
            </thead>
            <tbody>
                {jobs.map((job, idx) => <Job key={idx} {...job} />)}
            </tbody>
        </table>
    )
}
