import React, {KeyboardEventHandler, useState} from 'react';
import { useContext } from 'react';
import { JobContext } from '../../App';
import { companyData } from '../../utils/companies';
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
    const keyup: any = (e: any) => {
        console.log(e);
        if (e.code.toLowerCase() === "enter") props.filterChanged(e);
    }

    return (
        <div className="filter-system">
            <h2 onClick={() => setShowFilters(!showFilters)}>
                Job Filtering
                <span className="filters-expand">
                {showFilters && <>&and;</>}
                {!showFilters && <>&or;</>}
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
                                <input name="description" type="text" />
                            </div>
                        </fieldset>
                    </div>
                    <fieldset>
                        <legend>Companies</legend>
                        {companies.map((company, idx) => <CompanySelect key={idx} company={company} toggle={props.toggleCompany(company)} filter={filter} />)}
                    </fieldset>
                </form>
            </div>
        </div>
    )
};

export default FilterSystem;