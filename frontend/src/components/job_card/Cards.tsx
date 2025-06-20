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
    const perPage = 36;

    useEffect(() => {
        setStartIndex(0);
    }, [jobs]);

    return (
        <div className="cards">
            {props.jobs.slice(startIndex, startIndex + perPage).map((job, idx) => <Card key={idx} {...job} tag_colors={tag_colors} />)}
            <Pagination itemCount={jobs.length} itemsPerPage={perPage} currentIndex={startIndex} setPage={setStartIndex} />
        </div>
    )
}

export default Cards;