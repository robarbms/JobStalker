import React, { useState, useEffect } from 'react';
import Pagination from './Pagination';
import Card from './Card';

type CardsProps = {
    jobs: any[];
    tag_colors: any[];
}

const Cards = (props: CardsProps) => {
    const {jobs, tag_colors} = props;
    const [startIndex, setStartIndex] = useState(0);
    const perPage = 40;

    useEffect(() => {
        setStartIndex(0);
    }, [jobs]);

    return (
        <div className="cards">
            <h2>Results
                <span className="meta"><label>{startIndex + 1} - {Math.min(startIndex + 1 + perPage, jobs.length)} of {jobs.length}</label></span>
            </h2>
            {props.jobs.slice(startIndex, startIndex + perPage).map((job, idx) => <Card key={idx} {...job} tag_colors={tag_colors} />)}
            <Pagination itemCount={jobs.length} itemsPerPage={perPage} currentIndex={startIndex} setPage={setStartIndex} />
        </div>
    )
}

export default Cards;