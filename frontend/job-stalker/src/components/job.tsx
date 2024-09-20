import React from 'react';
import { months, weekDays } from '../utils/date';
import { ReactComponent as AppleIcon } from '../static/apple.svg';
import { ReactComponent as NetflixIcon } from '../static/netflix.svg';
import { ReactComponent as GoogleIcon } from '../static/google.svg';
import { ReactComponent as MicrosoftIcon } from '../static/microsoft.svg';
import { ReactComponent as AdobeIcon } from '../static/adobe.svg';
import { ReactComponent as AmazonIcon } from '../static/amazon.svg';
import { ReactComponent as HuggingfaceIcon } from '../static/huggingface.svg';
import { ReactComponent as OpenaiIcon } from '../static/openai.svg';

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
}

const getDateString = (date: string) => {
    date = date.replace(' 00:00:00 GMT', '');
    const dateObj = new Date(date);
    const dateString = `${weekDays[dateObj.getDay()].substring(0, 3)}, ${months[dateObj.getMonth()].substring(0, 3)} ${dateObj.getDate()}`;
    return dateString;
}


export default function Job(props: JobDetails) {
    const { company, date_posted, title, link } = props;
    const icons: {[key: string]: JSX.Element} = {
        Apple: <AppleIcon className="icon" />,
        Netflix: <NetflixIcon className="icon" />,
        Microsoft: <MicrosoftIcon className="icon" />,
        Adobe: <AdobeIcon className="icon" />,
        Google: <GoogleIcon className="icon" />,
        Amazon: <AmazonIcon className="icon" />,
        OpenAI: <OpenaiIcon className="icon" />,
        HuggingFace: <HuggingfaceIcon className="icon" />,
    }

    return(
        <tr>
            <td>
                {company in icons &&
                    icons[company.replace(/ /g, '')]
                }
                {props.company}</td>
            <td>{getDateString(date_posted)}</td>
            <td><a href={link} target="_blank">{title}</a></td>
        </tr>
    )
}