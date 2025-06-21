import React, { useContext, useEffect, useState } from "react";
import { CartesianGrid, XAxis, YAxis, Tooltip, Legend, Bar, Line, ComposedChart, Area } from 'recharts';
import {companyData} from "../../utils/companies";
import { JobDetails } from "../job";
import { getJobsByDate } from "./utils";
import { Filter } from '../../App';
import { dateSeparation } from '../../utils/date';

type WeekChartProps = {
    jobs: JobDetails[];
    prevJobs: JobDetails[];
    filter: Filter;
}

const WeekChart = (props: WeekChartProps) => {
    const { jobs, filter, prevJobs } = props;
    const separation = dateSeparation(filter.dateEnd, filter.dateStart);
    const [ jobsTotal, setJobsTotal ] = useState({
        total: 0,
        lastWeek: 0
    });
    const [ data, setData ] = useState([]);
    const [ companies, setCompanies ] = useState([]);
    const day = 1000 * 60 * 60 * 24;
    const days = Math.round((new Date(filter.dateEnd).getTime() - new Date(filter.dateStart).getTime()) / day * 10) / 10;
//    const { jobs } = useContext(JobContext);
    useEffect(() => {
        // Helper function to get the total number of jobs
        const getTotalJobs = (jobs: any[]) => jobs.reduce((total, job) => {
            for (let key in job) {
                if (key !== 'date' && key !== 'Last week' && key !== 'Total') {
                    total += job[key];
                }
            }
            return total;
        }, 0);

        const companiesParsed = jobs.reduce((acc: any, job: JobDetails) => {
            if (!acc.find((company: any) => company === job.company)) {
                acc.push(job.company);
            }
            return acc;
        }, []).sort();

        setCompanies(companiesParsed);

        /**
         * Data representing the jobs per company each day
         * 
         * [{
         *      date: "1/1",
         *      Amazon: 10,
         *      Google: 5,
         *  }]
         */
        const parsedLastWeekData = getJobsByDate(prevJobs);

        const dataParsed = getJobsByDate(jobs)
        .map((day: any, idx: number) => {
                let total = 0;
                let lastTotal = 0;
                for (const key in day) {
                    if (key !== "date") {
                        total += day[key];
                    }
                }
                for (const key in parsedLastWeekData[idx] as any) {
                    if (key !== "date") {
                        lastTotal += parsedLastWeekData[idx][key];
                    }
                }
                day['Last week'] = lastTotal;
                return day;
        });

        setData(dataParsed);
        setJobsTotal({
            total: getTotalJobs(dataParsed),
            lastWeek: getTotalJobs(parsedLastWeekData)
        });
    }, [jobs]);
 
    return (
        <div className="week-chart">
            <h2>Jobs over time: 
                <span className="meta">
                    <label>Current {separation}:</label> {jobsTotal.total}
                    <label>Avg:</label>{Math.floor(jobsTotal.total / days * 10) / 10}
                    <label>Previous {separation}:</label>{jobsTotal.lastWeek}
                    <label>Prev avg:</label>{Math.floor(jobsTotal.lastWeek / days * 10) / 10}
                </span>
            </h2>
            <ComposedChart width={600} height={300} data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis dataKey="" />
                <Tooltip />
                <Area dataKey="Last week" fill="#222" stroke="#444" />
                {companies.map((company: string, idx: number) => <Bar key={idx} dataKey={company} fill={companyData[company].color} />)}
                <Line dataKey="Total" stroke="green" strokeDasharray={4} />
                <Legend />
            </ComposedChart>

        </div>
    )
}

export default WeekChart;