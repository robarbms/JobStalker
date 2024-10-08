import React, { useContext } from "react";
import { Tooltip, Legend, PieChart, Pie, Cell, Label } from 'recharts';
import {companyData} from "../../utils/companies";
import { JobContext } from '../../App';
import { JobDetails } from "../job";

const CompanyChart = (props: any) => {
    const {jobs} = useContext(JobContext);
    type DataType = { name: string, value: number }
    const data: DataType[] = jobs.reduce((totals: {
        name: string,
        value: number,
    }[], {company}: JobDetails) => {
        const companyIndex = totals.findIndex((total: any) => total.name === company);
        if (companyIndex !== -1) {
            totals[companyIndex].value += 1;
        }
        else {
            totals.push({name: company, value: 1});
        }
        return totals;
    }, [])
    .sort((a: DataType, b: DataType) => a.name > b.name ? 1 : -1);
    const total = data.reduce((total, {value}) => total + value, 0);

    return (
        <div className="company-chart">
            <h2>Jobs per company</h2>
            <PieChart 
                width={500}
                height={300}
                data={data}
                margin={{top: 5, right: 30, left: 20, bottom: 5}}>
                <Legend layout="vertical" verticalAlign="middle" align="left" />
                <Tooltip />
                <Pie data={data} dataKey="value" label innerRadius={60} paddingAngle={1}>
                    {data.map((entry, index) => <Cell key={index} fill={companyData[entry.name]?.color || "#8884d8"} />)}
                    <Label position="center" value={`Total Jobs: ${total}`} />
                </Pie>
            </PieChart>
        </div>
    )
}

export default CompanyChart;
