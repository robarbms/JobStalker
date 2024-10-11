import React, { useContext, useEffect, useRef, useState } from "react";
import { BarChart, CartesianGrid, XAxis, YAxis, Tooltip, Legend, Bar, Line, ComposedChart, Area } from 'recharts';
import {companyData} from "../../utils/companies";
import { JobContext } from '../../App';
import { JobDetails } from "../job";
import { getJobsByDate } from "./utils";

const CustomTooltip = (props: any) => {
    if (!props) return null;
    const {active, payload, label} = props;
    if (active && payload) {
        const dataPoint = payload[0].payload;
        return (
            <div className="custom-tooltip">
                <p className="label">{`${payload[0].name} : ${dataPoint.value}`}</p>
            </div>
        );
    }
    return null;
}

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
            start = start === 0 ? new Date().getTime() : now.getTime() - start * day;
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
        const lastWeek = filterJobs(7, 7);

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
        let jobsCount = 0;
        let lastWeekCount = 0;
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
                        lastWeekCount += lastTotal;
                    }
                }
                day.date += `(${total})`;
                day['Total'] = total;
                day['Last week'] = lastTotal;
                jobsCount += total;
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
            <ComposedChart width={830} height={300} data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis dataKey="" />
                <Tooltip />
                {companies.map((company: string, idx: number) => <Bar key={idx} dataKey={company} fill={companyData[company].color} />)}
                <Line dataKey="Total" stroke="green" />
                <Line dataKey="Last week" stroke="purple" strokeDasharray="4" />
                <Legend />
            </ComposedChart>

        </div>
    )
}

export default WeekChart;