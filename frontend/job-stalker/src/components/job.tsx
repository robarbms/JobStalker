import React from 'react';
import { months, weekDays } from '../utils/date';
import { companyData } from '../utils/companies';

export type JobDetails = {
    id: string,
    job_id: string,
    title: string,
    company: string,
    created_at: string,
    date_posted: string,
    link: string,
    description: string,
    location: string,
    is_frontend?: boolean,
    is_manager?: boolean,
    tags: string | any[]
}

const getDateString = (date: string) => {
    date = date.replace(' 00:00:00 GMT', '');
    const dateObj = new Date(date);
    const dateString = `${weekDays[dateObj.getDay()].substring(0, 3)}, ${months[dateObj.getMonth()].substring(0, 3)} ${dateObj.getDate()}`;

    return dateString;
}

const getDateTime = (date: string) => {
    date = date.replace('GMT', '');
    const dateObj = new Date(date);
    const dateString = `${weekDays[dateObj.getDay()].substring(0, 3)}, ${months[dateObj.getMonth()].substring(0, 3)} ${dateObj.getDate()} ${dateObj.getHours()}:${dateObj.getMinutes().toString().padStart(2, '0')}`;

    return dateString;
}

export default function Job(props: JobDetails) {
    const { company, date_posted, title, link, created_at } = props;

    return(
        <tr>
            <td>
                {company in companyData &&
                    companyData[company.replace(/ /g, '')].icon
                }
                {props.company}</td>
            <td>{getDateString(date_posted)}</td>
            <td>{getDateTime(created_at)}</td>
            <td><a href={link} target="_blank">{title}</a></td>
        </tr>
    )
}

export { getDateString, getDateTime }