import React, { createRef, useEffect } from 'react';
import { dateToString, DateOffsetObj, dateOffset } from '../../utils/date';

type DateFiltersProps = {
    filterChanged: (event: React.ChangeEvent<HTMLFormElement>) => void;
}

const DateFilters = (props: DateFiltersProps) => {
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
        <div className="date-filters">
            <h2>Date Filters</h2>
        </div>
    );
}

export default DateFilters;
