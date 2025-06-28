import React, { useState, useEffect } from 'react';
import Pagination from './Pagination';
import Card from './Card';
import { Filter } from '../../App';
import { JobDetails } from '../job';

type CardsProps = {
    jobs: JobDetails[];
    tag_colors: any[];
    filterTags: (tag: string | string[], action: string) => void;
    filter: Filter;
}

const Cards = (props: CardsProps) => {
    const {jobs, tag_colors, filterTags, filter} = props;
    const [startIndex, setStartIndex] = useState(0);
    const perPage = 36;

    useEffect(() => {
        setStartIndex(0);
    }, [jobs]);

    return (
        <div className="cards">
            {props.jobs.slice(startIndex, startIndex + perPage).map((job, idx) => <Card key={idx} {...job} tag_colors={tag_colors} filterTags={filterTags} filter={filter} />)}
            <Pagination itemCount={jobs.length} itemsPerPage={perPage} currentIndex={startIndex} setPage={setStartIndex} />
        </div>
    )
}

export default Cards;