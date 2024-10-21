import React from 'react';
import { months, weekDays } from '../../utils/date';
import { companyData } from '../../utils/companies';
import { getDateString, getDateTime } from '../job';

const Tag = (props: any) => {
    const { name, color } = props;
    const { hue, saturation, lightness } = color;
    return (
        <div className="tag" style={{background: `hsl(${hue}, ${saturation}%, ${lightness}%)`}}>{name}</div>
    )
}

const payToString = (val: any) => {
    val = val.replace(".00", "");
    val = val.split("")
    val.reverse();
    val = val.map((numb: string, idx: number) => `${numb}${idx % 3 === 0 && idx > 0 ? "," : ""}`);
    val.reverse();
    return `$${val.join("")}`
}

const Card = (props: any) => {
    const { company, date_posted, title, link, created_at, tags, salary_min, salary_max, tag_colors } = props;

    return (
        <div className="job-card">
            <div className="job-card-layout">
                <div className="col-1">
                    {company in companyData &&
                        companyData[company.replace(/ /g, '')].icon
                    }
                </div>
                <div className="col-2">
                    <h3>
                        <a href={link} target="_blank">{title}</a>
                        <span className="job-card-date">{getDateString(date_posted)}</span>
                    </h3>
                    <span className="job-card-company">
                        {company}
                    </span>
                    {salary_min && payToString(salary_min)}
                    {salary_min && salary_max && " - "}
                    {salary_max && payToString(salary_max)}
                    <div className="job-card-tags">
                        {tags && Array.isArray(tags) && tags.map((tag: any, idx: number) => <Tag key={idx} color={tag_colors[tag]} name={tag} />)}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Card;
