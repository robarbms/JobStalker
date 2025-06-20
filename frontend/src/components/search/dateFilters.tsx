import React, { createRef, useEffect, useCallback } from 'react';
import { dateToString, DateOffsetObj, dateOffset } from '../../utils/date';

type DateFilterButtonProps = {
    text: string;
    start: any;
    end?: any;
    changeDates: Function;
}

const DateFilterButton = (props: DateFilterButtonProps) => {
    const { text, changeDates } = props;
    let { start, end } = props;
    start.setHours(0, 0, 0);
    if (!end) {
        end = new Date();
    }
    end.setHours(23, 59, 59);
    const data = {
        dateStart: dateToString(start),
        dateEnd: dateToString(end),
    }

    return (
        <div className="button" onClick={() => changeDates(data)}>
            {text}
        </div>
    )
}

type DateFiltersProps = {
    filterChanged: (event: React.ChangeEvent<HTMLFormElement>) => void;
}

const DateFilters = (props: DateFiltersProps) => {
    const dateStart = createRef<HTMLInputElement>();
    const dateEnd = createRef<HTMLInputElement>();
    const keyup: any = (e: any) => {
        if (!!e.code && e.code.toLowerCase() === "enter") props.filterChanged(e);
    }

    const today = new Date();
    today.setHours(0, 0, 0);
    const weekday = today.getDay();
    const day = 1000 * 60 * 60 * 24;
    const sunday = new Date(today.getTime() - day * weekday);

    const filters = [
        {
            text: '1 week',
            start: new Date(today.getTime() - day * 6)
        },
        {
            text: 'This week',
            start: sunday
        },
        {
            text: 'Last week',
            start: new Date(sunday.getTime() - day * 7),
            end: new Date(sunday.getTime() - day)
        },
        {
            text: '30 days',
            start: new Date(today.getTime() - day * 30)
        },
        {
            text: 'This month',
            start: new Date(today.setDate(1))
        },
        {
            text: 'Last month',
            start: new Date(today.setMonth(today.getMonth() === 0 ? 11 : today.getMonth() - 1, 1)),
            end: new Date(new Date(new Date().setDate(1)).getTime() - day)
        }
    ]

    const getStartDate = () => {
        const weekAgo = dateOffset({days: -6});
        weekAgo.setHours(0, 0, 0);
        return dateToString(weekAgo);
    }

    const getEndDate = useCallback(() => {
        const today = new Date();
        today.setHours(23, 59, 59);
        return dateToString(today);
    }, []);

    const endDate = dateToString(new Date());

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
            {filters.map((data, index) => <DateFilterButton {...data} key={index} changeDates={props.filterChanged} />)}
            <form onBlur={props.filterChanged} id="job-search-form">
                <label>Custom date range:</label>&nbsp;&nbsp;
                <input className="filter-date" type="date" name="dateStart" ref={dateStart} onInput={keyup} /> <span className="date-separate">to</span> <input className="filter-date" type="date" name="dateEnd" ref={dateEnd} onChange={keyup} />
                <div className="button">Change date</div>
            </form>
        </div>
    );
}

export default DateFilters;
