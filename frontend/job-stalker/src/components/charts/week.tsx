import React, { useContext } from "react";
import { BarChart, CartesianGrid, XAxis, YAxis, Tooltip, Legend, Bar } from 'recharts';
import {companyData} from "../../utils/companies";
import { JobContext } from '../../App';
import { JobDetails } from "../job";
import { getJobsByDate } from "./utils";

const WeekChart = () => {
    const { jobs } = useContext(JobContext);
    /**
     * Creates a data array of jobs for each day over the past week
     */
    const thisWeek = jobs.filter(job => {
        const now = new Date();
        now.setHours(0, 0, 0, 0); // set time to midnight for comparison
        const miliSecondsAgo = 1000 * 60 * 60 * 24 * 7;// 7 days in milliseconds
        return new Date(job.date_posted).getTime() >= (now.getTime() - miliSecondsAgo);
    });

    const companies = thisWeek.reduce((acc: any, job: JobDetails) => {
        if (!acc.find((company: any) => company === job.company)) {
            acc.push(job.company);
        }
        return acc;
    }, []).sort();

    /**
     * Data representing the jobs per company each day
     * 
     * [{
     *      date: "1/1",
     *      Amazon: 10,
     *      Google: 5,
     *  }]
     */

    const data = getJobsByDate(thisWeek);
 
    return (
        <div className="week-chart">
            <h2>Jobs over the last week</h2>
            <BarChart width={600} height={300} data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                {companies.map((company: string, idx: number) => <Bar key={idx} stackId="a" dataKey={company} fill={companyData[company].color} />)}
                <Legend />
            </BarChart>

        </div>
    )
}

export default WeekChart;