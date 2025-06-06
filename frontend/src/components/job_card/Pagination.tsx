import React from 'react';

type PaginationProps = {
    itemCount: number;
    currentIndex: number;
    setPage: (start: number) => void;
    itemsPerPage?: number;
}

const Pagination = (props: PaginationProps) => {
    const { itemCount, currentIndex, setPage, itemsPerPage } = props;
    const perPage = itemsPerPage || 20;
    const pageCount = Math.ceil(itemCount / perPage);
    const currentPage = Math.floor(currentIndex / perPage);
    return (
        <div className="pagination">
            {new Array(pageCount).fill(null).map((_, index) => 
                <span key={index} className={`pag ${index === currentPage ? "pag-active" : ""}`} onClick={() => setPage(index * perPage)}>{index + 1}</span>
            )}
        </div>
    );
}

export default Pagination;