import React from 'react';
import { useContext } from 'react';
import { JobContext } from '../App';
import { companyData } from '../utils/companies';

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

    return (
        <div className="filter-system">
            <h2>Job Filtering</h2>
            <form onBlur={props.filterChanged} id="job-search-form">
                <div className="text-search">
                    <fieldset>
                        <legend>Title</legend>
                        <div className="filter-item">
                            <input name="title" type="text" />
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
    )
};

export default FilterSystem;