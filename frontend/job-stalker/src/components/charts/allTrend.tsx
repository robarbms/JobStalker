import React, { useContext } from "react";
import { LineChart, Line, BarChart, CartesianGrid, XAxis, YAxis, Tooltip, Legend, Bar } from 'recharts';
import {companyData} from "../../utils/companies";
import { JobContext } from '../../App';
import { JobDetails } from "../job";
import { getJobsByDate } from "./utils";

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
     *  }]
     */

    const data = getJobsByDate(allJobs, false);
 
    return (
        <div className="trend-chart">
            <h2>All Jobs</h2>
            <BarChart width={1350} height={200} data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                {companies.map((company: string, idx: number) => <Bar key={idx} dataKey={company} fill={companyData[company].color} />)}
                <Legend />
            </BarChart>

        </div>
    )
}

export default AllTrendChart;