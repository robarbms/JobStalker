import React, { useState } from 'react';
import { companyData } from '../../utils/companies';
import { getDateString } from '../job';
import { Filter } from '../../App';
import '../../styles/card.css';

type TagProps = {
    name: string;
    color: {
        hue: number;
        saturation: number;
        lightness: number;
    };
    filterTags: (tag: string | string[], action: string) => void;
    isActive: boolean;
}

const Tag = (props: any) => {
    const { name, color, filterTags, isActive } = props;
    let hsl = "155, 0%, 50%";
    if (color) {
        const { hue, saturation, lightness } = color;
        hsl = `${hue}, ${saturation}%, ${lightness}%`
    }
    return (
        <div className="tag" style={isActive === true ? {background: `#00aa00`} : {}} onClick={() => filterTags(name, "include")}>{name}</div>
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

type CardProps = {
    company: string;
    date_posted: string;
    title: string;
    link: string;
    created_at: string;
    tags: string | any[];
    salary_min?: string;
    salary_max?: string;
    tag_colors: any[];
    summary: string;
    filterTags: (tag: string | string[], action: string) => void;
    filter: Filter;
}

const Card = (props: CardProps) => {
    const { company, date_posted, title, link, created_at, tags, salary_min, salary_max, tag_colors, summary, filterTags, filter } = props;
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
                        {tags && Array.isArray(tags) && tags.map((tag: any, idx: number) => <Tag key={idx} isActive={filter.tagsInclude.includes(tag)} color={tag_colors[tag]} name={tag} filterTags={filterTags} />)}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Card;
