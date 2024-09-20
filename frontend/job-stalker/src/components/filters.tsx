import React, { useContext, useState } from 'react';
import { JobContext } from '../App';

export default function Filters() {
    const {hideManager, toggleHideManager, onlyFrontend, toggleOnlyFrontend} = useContext(JobContext);

    return (
        <div className="filters">
            <span>Filters: </span>
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