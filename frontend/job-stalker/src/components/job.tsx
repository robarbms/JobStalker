import React from 'react';
import { months, weekDays } from '../utils/date';

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
}

const getDateString = (date: string) => {
    date = date.replace(' 00:00:00 GMT', '');
    const dateObj = new Date(date);
    const dateString = `${weekDays[dateObj.getDay()].substring(0, 3)}, ${months[dateObj.getMonth()].substring(0, 3)} ${dateObj.getDate()}`;
    return dateString;
}


export default function Job(props: JobDetails) {

    return(
        <tr>
            <td>{props.company}</td>
            <td>{getDateString(props.date_posted)}</td>
            <td><a href={props.link} target="_blank">{props.title}</a></td>
        </tr>
    )
}