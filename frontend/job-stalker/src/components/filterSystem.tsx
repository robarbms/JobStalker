import React from 'react';
import { useContext } from 'react';
import { JobContext } from '../App';
import { companyData } from '../utils/companies';

type FilterSystemProps = {
    filterChanged: (event: React.ChangeEvent<HTMLFormElement>) => void;
}

 const CompanySelect = (props: any) => {
    const { company, toggle } = props;
    return(
        <div className="company-select" onClick={toggle}>
            {company in companyData && companyData[company].icon}
            <div>{company}</div>
        </div>
    )
 }

const FilterSystem = (props: FilterSystemProps) => {
    const { companies } = useContext(JobContext);
    const companyToggle = (company: string) => {
        return () => {};
    }
    return (
        <div className="filter-system">
            <h2>Job search</h2>
            <form onBlur={props.filterChanged} id="job-search-form">
                <div className="text-search">
                    <fieldset>
                        <legend>Title</legend>
                        <div className="filter-item">
                            <label>Include</label><input name="title_include" type="text" />
                        </div>
                        <div className="filter-item">
                            <label>Exclude</label><input name="title_exclude" type="text" />
                        </div>
                    </fieldset>
                    <fieldset>
                        <legend>Descrpition</legend>
                        <div className="filter-item">
                            <label>Include</label><input name="description_include" type="text" />
                        </div>
                        <div className="filter-item">
                            <label>Exclude</label><input name="description_exclude" type="text" />
                        </div>
                    </fieldset>
                </div>
                <fieldset>
                    <legend>Companies</legend>
                    {companies.map((company, idx) => <CompanySelect key={idx} company={company} toggle={companyToggle(company)} />)}
                </fieldset>
            </form>
        </div>
    )
};

export default FilterSystem;