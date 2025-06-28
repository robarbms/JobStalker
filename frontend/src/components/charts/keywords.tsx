import React, { useState, useEffect } from 'react';
import '../../styles/keywords.css';
import { JobDetails } from '../job';
import { Filter } from '../../App';
import developerTags from '../../utils/tech_keywords.json';
import datascienceTags from '../../utils/ds_keywords.json';
import designTags from '../../utils/design_keywords.json';
import KeywordGroupOverview from './keywordGroup';
import TagsOverTime from '../tags/tagsOverTime';
import TagFilters from '../search/tagFilters';
import { childrenToArray, parseTags } from '../../utils/data';

export type TagCategoryItem = {
    name: string;
    type: string;
};

/**
 * Type representing a tag list category
 */
export type TagListCategory = {
    'name': string;
    'libraries'?: TagCategoryItem[],
    'methods'?: TagCategoryItem[],
    'models'?: TagCategoryItem[]
}

export type TagList = TagListCategory[];

/**
 * Data used to render the tabs and parse data to the correct group
 */
export const keywordGroups = {
    'Developer': {
        tags: developerTags as TagList
    },
    'Data Scientist': {
        tags: datascienceTags as TagList
    },
    'Designer': {
        tags: designTags as TagList
    }
}

export type KeywordGroupsT = typeof keywordGroups;

/**
 * Typing for tabs
 */
export type KeywordGroupName = keyof typeof keywordGroups;


export type KeywordTabProps = {
    name: string;
    isActive: boolean;
    setActiveTab: React.Dispatch<React.SetStateAction<KeywordGroupName>>;
}

/**'
 * A tab for a keyword section
 */
export const KeywordTab = (props: KeywordTabProps) => {
    const { name, isActive, setActiveTab } = props;
    return (
        <div className={`keyword-tab ${isActive ? "active-tab" : ""}`} onClick={() => setActiveTab(name as KeywordGroupName)}>
            {name}
        </div>
    );
}

/**
 * Properties for the Keywords component
 */
export type KeywordsProps = {
    jobs: {
        tags: string | any[];
        date_posted: string;
    }[];
    filter: Filter;
    filterTags: (tag: string | string[], action: string) => void;
    tagColors: {[tag: string]: string};
    parsedTagData: any;
}

/**
 * Component that renders keyword metrics grouped by job type
 * @param props 
 * @returns 
 */
const Keywords = (props: KeywordsProps) => {
    const { jobs, filter, filterTags, tagColors, parsedTagData } = props;
    const [ activeTab, setActiveTab ] = useState<KeywordGroupName>('Developer');
    const [ tagData, setTagData ] = useState({});
    const [ tagList, setTagList ] = useState({});
    const [ tagGroupData, setTagGroupData ] = useState();

    useEffect(() => {
        if (jobs && Array.isArray(jobs) && jobs.length > 0) {
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
        }
    }, [jobs, filter, parsedTagData]);
    return (
        <div className="keywords">
            <h2>Keywords</h2>
            <div className="keyword-content">
                <div className="keyword-overviews">
                    {tagGroupData &&
                        <KeywordGroupOverview data={tagGroupData} tagColors={tagColors} />
                    }
                    <div className="keyword-cat-select">
                        <div className="keyword-tabs">
                            {(Object.keys(keywordGroups) as KeywordGroupName[]).map((group: KeywordGroupName, index: number) => <KeywordTab key={index} name={group} isActive={group === activeTab} setActiveTab={setActiveTab} />)}
                        </div>
                        {tagData && activeTab in tagData &&
                            <KeywordGroupOverview data={(tagData as any)[activeTab]} tagColors={tagColors} />
                        }
                    </div>
                </div>
                {tagData && activeTab in tagData &&
                    <>
                        <TagsOverTime jobs={jobs as JobDetails[]} category={activeTab} />
                        <TagFilters tagData={(tagList as any)[activeTab]} filter={filter} filterTags={filterTags} />
                    </>
                }
            </div>
        </div>
    );
};

export default Keywords;
