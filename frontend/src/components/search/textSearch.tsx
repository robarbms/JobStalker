import React from 'react';
import '../../styles/text_search.css';

type TextSearchProps = {
    filterChanged: (event: React.ChangeEvent<HTMLFormElement>) => void;
}

const TextSearch = (props: TextSearchProps) => {
    const keyup: any = (e: any) => {
        if (!!e.code && e.code.toLowerCase() === "enter") props.filterChanged(e);
    }

    return (
        <div className="text-search">
            <h2>Text Search</h2>
                <form onBlur={props.filterChanged} onSubmit={props.filterChanged} id="job-search-form">
                    <div className="text-search-item">
                        <label>Title</label>
                        <input name="title" type="text" onKeyUp={keyup} placeholder='Keywords to search job titles'/>
                    </div>
                    <div className="text-search-item">
                        <label>Summary</label>
                        <input name="summary" type="text" onKeyUp={keyup} placeholder='Keywords to search job summaries' />
                    </div>
                </form>
        </div>
    )
}

export default TextSearch;
