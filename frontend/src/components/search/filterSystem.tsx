import React, {KeyboardEventHandler, useEffect, useState, createRef} from 'react';
import { useContext } from 'react';
import { JobContext } from '../../App';
import { companyData } from '../../utils/companies';
import { dateToString, DateOffsetObj, dateOffset } from '../../utils/date';
import '../../styles/filters.css';

type FilterSystemProps = {
    filterChanged: (event: React.ChangeEvent<HTMLFormElement>) => void;
    toggleCompany: (company: string) => () => void;
}

 const CompanySelect = (props: any) => {
    const { company, toggle, filter } = props;
    const isSelected = filter.companies.length === 0 ||
       filter.companies.includes(company);
    return(
        <div className={`company-select ${isSelected ? "company-selected" : ""}`} onClick={toggle}>
            {company in companyData && companyData[company].icon}
            <div>{company}</div>
        </div>
    )
 }

const FilterSystem = (props: FilterSystemProps) => {
    const { companies, filter } = useContext(JobContext);
    const [ showFilters, setShowFilters ] = useState(true);
    const dateStart = createRef<HTMLInputElement>();
    const dateEnd = createRef<HTMLInputElement>();
    const keyup: any = (e: any) => {
        if (!!e.code && e.code.toLowerCase() === "enter") props.filterChanged(e);
    }

    const getStartDate = () => {
        const weekAgo = dateOffset({days: -6});
        weekAgo.setHours(0, 0, 0);
        return dateToString(weekAgo);
    }

    const getEndDate = () => {
        const today = new Date();
        today.setHours(23, 59, 59);
        return dateToString(today);
    }

    useEffect(() => {
        if (dateStart.current) {
            dateStart.current.value = getStartDate();
        }
        if (dateEnd.current) {
            dateEnd.current.value = getEndDate();
        }
    }, []);

    return (
        <div className="filter-system">
            <h2 onClick={() => setShowFilters(!showFilters)}>
                Job Filtering
                <span className="filters-expand">
                {showFilters && <>&#9650;</>}
                {!showFilters && <>&#9660;</>}
                </span>
            </h2>
            <div className={`filters-cont ${showFilters ? 'show-filters' : 'hide-filters'}`}>
                <form onBlur={props.filterChanged} onSubmit={props.filterChanged} id="job-search-form">
                    <div className="text-search">
                        <fieldset>
                            <legend>Title</legend>
                            <div className="filter-item">
                                <input name="title" type="text" onKeyUp={keyup} />
                            </div>
                        </fieldset>
                        <fieldset>
                            <legend>Descrpition</legend>
                            <div className="filter-item">
                                <input name="description" type="text" onKeyUp={keyup} />
                            </div>
                        </fieldset>
                        <fieldset>
                            <legend>Date Range</legend>
                            <input className="filter-date" type="date" name="dateStart" ref={dateStart} onInput={keyup} /> <span className="date-separate">to</span> <input className="filter-date" type="date" name="dateEnd" ref={dateEnd} onChange={keyup} />
                        </fieldset>
                    </div>
                </form>
            </div>
        </div>
    )
};

export default FilterSystem;