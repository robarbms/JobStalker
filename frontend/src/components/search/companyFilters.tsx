import React, { useContext, useState } from 'react';
import { JobContext } from '../../App';
import { companyData } from '../../utils/companies';
import Toggle from './toggle';
import '../../styles/company_search.css';

type CompanyFilterProps = {
    company: string;
    toggle: any;
    setFocus: any;
    enabled: boolean;
    focused: boolean;
}

const CompanyFilter = (props: CompanyFilterProps) => {
    const { company, enabled, toggle, setFocus, focused} = props;

    return (
        <div className="company-filter">
            {company in companyData && companyData[company].icon}
            <div>{company}</div>
            <div className="company-controls">
                <div className="company-toggle" onClick={toggle}>
                    Enable
                    <Toggle toggle={toggle} enabled={enabled} />
                </div>
                <div className="company-focus" onClick={setFocus}>
                    Focus
                    <Toggle toggle={setFocus} enabled={focused} />
                </div>
            </div>
        </div>
    )
}

type CompanyFiltersProps = {
    toggleCompany: Function;
    focusCompany: Function;
    setFilter: any;
}

const CompanyFilters = (props: CompanyFiltersProps) => {
    const { companies, filter } = useContext(JobContext);
    const isEnabled = (company: string) => filter.companies.includes(company) || filter.companies.length === 0;
    const allOn = () => props.setFilter({...filter, companies});

    return (
    <div>
        <h2>Company Filters</h2>
        <div className="button" onClick={allOn}>Enable all</div>
        <div className="company-filters">
            {companies.map((company, index) => <CompanyFilter key={index} company={company} focused={filter.focusedCompany === company} enabled={isEnabled(company)} toggle={props.toggleCompany(company)} setFocus={props.focusCompany(company)} />)}
        </div>
    </div>);
};

export default CompanyFilters;