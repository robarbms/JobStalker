import React from 'react';
import '../../styles/tag_filters.css';
import { getTagColors } from '../tags/tagColors';
import { hslToHex } from '../charts/keywordGroup';
import { Filter } from '../../App';

const objToArray = (obj: any) => {
    const objOut = [];
    for (let name in obj) {
        objOut.push({
            name,
            ...obj[name]
        });
    }
    return objOut;
}

type TagProps = {
    name: string;
    count: number;
    filterTags: (tag: string | string[], action: string) => void;
    filter: Filter;
}  

const Tag = (props: TagProps) => {
    const { name, filterTags, filter, count } = props;
    const isInclude = filter.tagsInclude.includes(name);
    const isExclude = filter.tagsExclude.includes(name);

    return (
        <div className={`tag-filter tag-status ${isInclude ? "tag-status-active" : ""} ${isExclude ? "tag-status-disabled": ""}`}>
            <div className="tag-name">{name} ({count})</div>
            <div className="tag-controls">
                <div className="tag-disable-cont">
                    <div className="tag-control-name" onClick={() => filterTags(name, "exclude")}>Exclude</div>
                    <div className="tag-disable"></div>
                </div>
                <div className="tag-activate-cont">
                    <div className="tag-control-name" onClick={() => filterTags(name, "include")}>Includes</div>
                    <div className="tag-activate"></div>
                </div>
            </div>
        </div>
    );
}

type TagCategoryProps = TagGroupProps & {
    tagColors: any;
    useColors?: boolean;
    filterTags: (tag: string | string[], action: string) => void;
    filter: Filter;
}

const TagCategory = (props: TagCategoryProps) => {
    const {name, tagColors, total, count, useColors, children, filterTags, filter } = props;
    const colorStyles = useColors ? {
        borderColor:  hslToHex(tagColors[name])
    } : {};
    const childTags: string[] = children.map((child) => child.name);
    const { tagsInclude, tagsExclude } = filter;
    let status = 'tag-status';
    if (tagsExclude.includes(name)) {
        status += ' tag-status-disable';
    }
    else if (tagsInclude.includes(name) ||
        tagsInclude.some((t) => childTags.includes(t))) {
        status += ' tag-status-active';
    }

    return (
        <div className={`tag-category ${status} ${children.length > 8 ? 'tag-cat-2-col' : ''}`} style={colorStyles}>
            <div className="tag-category-name">
                {props.name} ({(count || 0) + (total || 0)})
                <div className="button" onClick={() => filterTags(name, "exclude")}>Exclude</div>
                <div className="button" onClick={() => filterTags(name, "include")}>Includes</div>
                <div className="button" onClick={() => filterTags([name, ...childTags], "include")}>All on</div>
                <div className="button" onClick={() => filterTags([name, ...childTags], "clear")}>Clear</div>
            </div>
            <div className="tags">
                {objToArray(children).map((data, index) => <Tag key={index} {...data} tagColors={tagColors} filterTags={filterTags} filter={filter} />)}
            </div>
        </div>
    )
}

type TagGroupProps = {
    name: string;
    children: any[];
    total?: number;
    count?: number;
    useColors?: boolean;
}

type TagFiltersProps = {
    tagData: any;
    filter: Filter;
    filterTags: (tag: string | string[], action: string) => void;
}

const TagFilters = (props: TagFiltersProps) => {
    const { tagData, filter, filterTags } = props;
    const tag_colors = getTagColors();

    return (
        <div className={`tag-filters`}>
            <h2>Tag Filters
                <div className="button" onClick={() => filterTags('clear', 'clear')}>Clear all</div>
            </h2>
            <div className="tag-categories">
                {tagData && tagData.children.map((data: any, index: number) => <TagCategory key={index} {...data} filter={filter} tagColors={tag_colors} filterTags={filterTags} />)}
            </div>
        </div>
    )
}

export default TagFilters;