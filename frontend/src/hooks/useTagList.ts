import React, { useState } from 'react';
import { childrenToArray, parseTags } from '../utils/data';

const useTagList = (jobs : {
    tags: string | any[];
    date_posted: string;
}[], parsedTagData: any, setTagList: React.Dispatch<React.SetStateAction<{}>>) => {
    const [ tagData, setTagData ] = useState({});
    const [tagGroupData, setTagGroupData ] = useState();
    const groupData: any = { children: [], total: 0};

    for (let name in parsedTagData) {
        const group: any = parsedTagData[name];
        groupData.total += group.total;
        groupData.children.push({
            name,
            count: group.total
        });
    }
    setTagGroupData(groupData);
    const tagDataAsArray: any = {};
    for (const type in parsedTagData) {
        const node = childrenToArray(parsedTagData[type]);
        node.children.sort((a: any, b: any) => b.children.length - a.children.length)
        tagDataAsArray[type] = node;
    }
    setTagList(tagDataAsArray);
    const keywordCounts: any = parseTags(jobs as any);
    const keywordCountsAsArray: any = {}
    for (let type in keywordCounts) {
        keywordCountsAsArray[type] = childrenToArray(keywordCounts[type]);
    }
    setTagData(keywordCountsAsArray);

    return {tagData, tagGroupData};
}

export default useTagList;