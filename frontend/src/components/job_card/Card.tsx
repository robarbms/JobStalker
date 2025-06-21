import React, { useState } from 'react';
import { companyData } from '../../utils/companies';
import { getDateString } from '../job';
import '../../styles/card.css';

const Tag = (props: any) => {
    const { name, color } = props;
    let hsl = "155, 0%, 50%";
    if (color) {
        const { hue, saturation, lightness } = color;
        hsl = `${hue}, ${saturation}%, ${lightness}%`
    }
    return (
        <div className="tag" style={{background: `hsl(${hsl})`}}>{name}</div>
    )
}

const payToString = (val: any) => {
    if (!val) return val;
    val = `${val}`;
    val = val.replace(".00", "");
    val = val.split("")
    val.reverse();
    val = val.map((numb: string, idx: number) => `${numb}${idx % 3 === 0 && idx > 0 ? "," : ""}`);
    val.reverse();
    return `$${val.join("")}`
}

const Card = (props: any) => {
    const { company, date_posted, title, link, created_at, tags, salary_min, salary_max, tag_colors, summary } = props;
    const [expand, setExpand] = useState(false);
    const useExpand = false;

    return (
        <div className="job-card">
            <div className="job-card-layout">
                <div className="col-1">
                    {company in companyData &&
                        companyData[company.replace(/ /g, '')].icon
                    }
                </div>
                <div className="col-2">
                    <a href={link} target="_blank" rel="noreferrer">
                        <h3>
                            {title}
                        </h3>
                        <span className="job-card-company">
                            {company}
                        </span>
                        {salary_min && payToString(salary_min)}
                        {salary_min && salary_max && " - "}
                        {salary_max && payToString(salary_max)}
                        <span className="job-card-date">{getDateString(date_posted)}</span>
                        <p className={!useExpand || expand ? "job-card-summary-all" : ""}>{summary}</p>
                    </a>
                    {useExpand &&
                        <div className="job-card-summary-more"><span onClick={() => setExpand(expand === false)}>{expand ? "Show less" : "See more"}</span></div>
                    }
                    <div className="job-card-tags">
                        {tags && Array.isArray(tags) && tags.map((tag: any, idx: number) => <Tag key={idx} color={tag_colors[tag]} name={tag} />)}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Card;
