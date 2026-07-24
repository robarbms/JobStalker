import React, {useEffect, useRef} from 'react';
import '../../styles/text_search.css';

type TextSearchProps = {
    filterChanged: (event: React.ChangeEvent<HTMLFormElement>) => void;
}

const TextSearch = (props: TextSearchProps) => {
    const keyup: any = (e: any) => {
        if (!!e.code && e.code.toLowerCase() === "enter") props.filterChanged(e);
    }
    const titleRef = useRef<HTMLInputElement>(null);
    const summaryRef = useRef<HTMLInputElement>(null);
    useEffect(() => {
        const filtersString = localStorage.getItem('filters');
        if (filtersString) {
            const filterObj = JSON.parse(filtersString);
            if (filterObj.title && titleRef.current) {
                titleRef.current.value = filterObj.title;
            }
            if (filterObj.summary && summaryRef.current) {
                summaryRef.current.value = filterObj.summary;
            }
        }
    }, []);

    return (
        <div className="text-search">
            <h2>Text Search</h2>
            <form onBlur={props.filterChanged} onSubmit={props.filterChanged} id="job-search-form">
                <div className="text-search-item">
                    <label>Title</label>
                    <input ref={titleRef} name="title" type="text" onKeyUp={keyup} placeholder='Keywords to search job titles'/>
                </div>
                <div className="text-search-item">
                    <label>Summary</label>
                    <input ref={summaryRef} name="summary" type="text" onKeyUp={keyup} placeholder='Keywords to search job summaries' />
                </div>
            </form>
        </div>
    )
}

export default TextSearch;
