import React, {useEffect, useRef} from 'react';
import '../../styles/text_search.css';

type TextSearchProps = {
    filterChanged: (event: React.ChangeEvent<HTMLFormElement>) => void;
    text: string;
    summary: string;
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

    useEffect(() => {
        if (titleRef.current) {
            if (titleRef.current.value !== props.text) {
                titleRef.current.value = props.text;
            }
        }
        if (summaryRef.current) {
            if (summaryRef.current.value !== props.summary) {
                summaryRef.current.value = props.summary;
            }
        }
    }, [props.text, props.summary]);

    return (
        <div className="text-search">
            <h2>Text Search</h2>
            <p>
                Space separated words will only return searches with all words.
                You can use a pipe symbol | to return results that contain 1 of the words.
                You can remove results with specific words by prefixing them with an exclamation.
            </p>
            <form onBlur={props.filterChanged} onSubmit={props.filterChanged} id="job-search-form">
                <div className="text-search-item">
                    <label>Title</label>
                    <input ref={titleRef} defaultValue={props.text} name="title" type="text" onKeyUp={keyup} placeholder='Keywords to search job titles'/>
                </div>
                <div className="text-search-item">
                    <label>Summary</label>
                    <input ref={summaryRef} defaultValue={props.summary} name="summary" type="text" onKeyUp={keyup} placeholder='Keywords to search job summaries' />
                </div>
            </form>
        </div>
    )
}

export default TextSearch;
