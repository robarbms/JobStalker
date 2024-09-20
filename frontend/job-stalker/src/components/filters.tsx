import React, { useContext, useEffect, useState, useRef } from 'react';
import { JobContext } from '../App';
import { JobDetails } from './job';

export default function Filters() {
    const {hideManager, toggleHideManager, onlyFrontend, toggleOnlyFrontend, jobs, companyFilter, setCompanyFilter, companies} = useContext(JobContext);
    const companySelectRef = useRef<HTMLSelectElement>(null);

    const companyFilterChanged = () => {
        if (companySelectRef.current) {
            const index = companySelectRef.current.selectedIndex;
            setCompanyFilter(companySelectRef.current.options[index].value);
        }
    }

    return (
        <div className="filters">
            <span>Filters: </span>
            <span className="filter-item">
                <label>Company</label>
                <select ref={companySelectRef} onChange={companyFilterChanged}>
                    {companies.map((c, i) => <option key={i}>{c}</option>)}
                </select>
            </span>
            <span className="filter-item">
                <input type='checkbox' checked={hideManager} onChange={toggleHideManager}/>
                Hide managers
            </span>
            <span className="filter-item">
                <input type='checkbox' checked={onlyFrontend} onChange={toggleOnlyFrontend}/>
                Show only frontend jobs
            </span>
        </div>
    )
}