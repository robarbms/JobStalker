import React, { useContext, useState } from "react";
import { Line, CartesianGrid, XAxis, YAxis, Tooltip, Legend, Bar, ComposedChart } from 'recharts';
import {companyData} from "../../utils/companies";
import { JobContext } from '../../App';
import { JobDetails } from "../job";
import { getJobsByDate, filterJobs } from "./utils";

const AllTrendChart = () => {
    const { allJobs } = useContext(JobContext);
 
    const companies = allJobs.reduce((acc: any, job: JobDetails) => {
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
     *      Total: 15,
     *      Created: 6,
     *  }]
     */

    const timeSinceStart = new Date().getTime() - new Date("2024-09-17").getTime();
    const daysSinceStart = Math.floor(timeSinceStart / (1000 * 60 * 60 * 24)) + 1;

    const lastTwoMonths = filterJobs(allJobs, daysSinceStart);

    const data = getJobsByDate(lastTwoMonths);
    const created_data = getJobsByDate(allJobs, true, true);
    created_data.forEach((item: any) => {
        const {date} = item;
        const index = data.findIndex((d: any) => d.date === date);
        if (index !== -1) {
            data[index].Scraped = item.Total;
        }
    });
 
    return (
        <div className="trend-chart">
            <h2>All Jobs</h2>
            <ComposedChart width={1350} height={200} data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                {companies.map((company: string, idx: number) => <Bar key={idx} stackId="a" dataKey={company} fill={companyData[company].color} />)}
                <Line dataKey="Total" stroke="#0f0" dot={false} strokeDasharray={4} />
                <Line dataKey="Scraped" stroke="magenta" dot={false} strokeDasharray={4} />
                <Legend />
            </ComposedChart>

        </div>
    )
}

export default AllTrendChart;