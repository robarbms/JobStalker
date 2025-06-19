import React from 'react';
import '../../styles/tag_filters.css';
import { getTagColors } from '../tags/tagColors';
import { hslToHex } from '../charts/keywordGroup';

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

}

const Tag = (props: TagProps) => {
    return (
        <div className="tag"></div>
    );
}

type TagCategoryProps = TagGroupProps & {
    tagColors: any;
    useColors?: boolean;
}

const TagCategory = (props: TagCategoryProps) => {
    const {name, tagColors, total, count, useColors } = props;
    const colorStyles = useColors ? {
        borderColor:  hslToHex(tagColors[name])
    } : {};

    return (
        <div className="tag-category tag-status-active" style={colorStyles}>
            <div>{props.name} ({(count || 0) + (total || 0)})</div>
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

const TagGroup = (props: TagGroupProps) => {
    const { name, children, total } = props;
    const tag_colors = getTagColors();

    return (
        <div className="tag-group">
            <h2>{name}({total})</h2>
            <div className="tag-categories">
                {objToArray(children).map((data, index) => <TagCategory key={index} {...data} tagColors={tag_colors} />)}
            </div>
        </div>
    )
}

type TagFiltersProps = {
    tagData: any;
}

const TagFilters = (props: TagFiltersProps) => {
    const { tagData } = props;
    console.dir(tagData);
    return (
        <div className="tag-filters">
            <h2>Tag Filters</h2>
            {objToArray(tagData).map((data, index) => <TagGroup key={index} {...data} />)}
        </div>
    )
}

export default TagFilters;