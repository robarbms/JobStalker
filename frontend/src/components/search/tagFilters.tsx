import React from 'react';
import '../../styles/tag_filters.css';
import tech_keywords from '../../utils/tech_keywords.json';

type TagProps = {

}

const Tag = (props: TagProps) => {
    return (
        <div className="tag"></div>
    );
}

type TagFiltersProps = {

}

const TagFilters = (props: TagFiltersProps) => {
    console.dir(tech_keywords);
    return (
        <div className="tag-filters">
            <h2>Tag Filters</h2>
            <div className="filter">

            </div>
        </div>
    )
}

export default TagFilters;