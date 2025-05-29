import React, { useContext, useEffect, useState } from "react";
import { CartesianGrid, XAxis, YAxis, Tooltip, Legend, Bar, Line, ComposedChart, Area } from 'recharts';
import {companyData} from "../../utils/companies";
import { JobContext } from '../../App';
import { JobDetails } from "../job";
import { getJobsByDate } from "./utils";

const WeekChart = () => {
    const [ jobsTotal, setJobsTotal ] = useState({
        total: 0,
        lastWeek: 0
    });
    const [ data, setData ] = useState([]);
    const [ companies, setCompanies ] = useState([]);
    const { jobs } = useContext(JobContext);
    useEffect(() => {
        // Helper function to get data between a specific timeframe
        const filterJobs = (end: number, start: number = 0) => {
            const now = new Date();
            now.setHours(0, 0, 0, 0);
            const day = 1000 * 60 * 60 * 24; // milliseconds in a day
            start = now.getTime() - (start === 0 ? start * day : 0);
            end = start - end * day;

            return jobs.filter((job: JobDetails) => {
                const jobDateTime = new Date(job.date_posted).getTime();
                return jobDateTime < start && jobDateTime >= end;
            });
        }

        // Helper function to get the total number of jobs
        const getTotalJobs = (jobs: any[]) => jobs.reduce((total, job) => {
            for (let key in job) {
                if (key !== 'date' && key !== 'Last week' && key !== 'Total') {
                    total += job[key];
                }
            }
            return total;
        }, 0);

        /**
         * Creates a data array of jobs for each day over the past week
         */
        const thisWeek = filterJobs(7);
        const lastWeek = filterJobs(7, 8);

        const companiesParsed = thisWeek.reduce((acc: any, job: JobDetails) => {
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
        const parsedLastWeekData = getJobsByDate(lastWeek);

        const dataParsed = getJobsByDate(thisWeek)
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
            <h2>Jobs for the week: <span className="meta"><label>This week:</label> {jobsTotal.total} <label>Last week:</label>{jobsTotal.lastWeek}</span></h2>
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