import React, { useState, useEffect } from 'react';
import '../../styles/keywords.css';
import { JobDetails } from '../job';
import { Filter } from '../../App';
import developerTags from '../../utils/tech_keywords.json';
import datascienceTags from '../../utils/ds_keywords.json';
import designTags from '../../utils/design_keywords.json';
import KeywordGroupOverview from './keywordGroup';
import TagsOverTime from '../tags/tagsOverTime';

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
    'Datascience': {
        tags: datascienceTags as TagList
    },
    'Design': {
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
    filterTags: (data: any) => void;
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
    const [ tagGroupData, setTagGroupData ] = useState();

    useEffect(() => {
        // Go through jobs and create a tag map with counts
        const jobTags: {[tag: string]: number} = {};
        if (jobs && Array.isArray(jobs)) {
            jobs.forEach(job => {
                if (Array.isArray(job.tags)) {
                    job.tags.forEach((tag) => {
                        if (!(tag in jobTags)) {
                            jobTags[tag] = 0;
                        }
                        jobTags[tag] += 1;
                    });
                }
            });
        }

        // Parse tags from jobs to figure out counts for each
        const tagDataLocal: any = {};
        for (const groupName in keywordGroups as KeywordGroupsT) {
            const tagLists = keywordGroups[groupName as KeywordGroupName].tags;
            let groupTotal = 0;
            const groupChildren: any[] = [];
            tagLists.forEach((category) => {
                const {name} = category;
                const areas = ['libraries', 'methods', 'models'];
                const children: any[] = [];
                const categoryCount = name in jobTags ? jobTags[name] : 0;
                let categoryTotal = categoryCount;
                areas.forEach((area) => {
                    if (area in category) {
                        const foundTags = category[area as ('libraries' | 'methods' | 'models')]?.map((item: TagCategoryItem) => item.name);
                        if (foundTags) {
                            foundTags.forEach((tag) => {
                                if (tag in jobTags) {
                                    const count = jobTags[tag];
                                    categoryTotal += count;
                                    children.push({
                                        name: tag,
                                        count
                                    });
                                }
                            });
                        }
                    }
                });
                groupChildren.push({
                    name,
                    count: categoryCount,
                    total: categoryTotal,
                    children
                });
                groupTotal += categoryTotal;
            });
            tagDataLocal[groupName] = {
                total: groupTotal,
                children: groupChildren
            }
        }
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

        setTagData(tagDataLocal);
    }, [jobs, filter]);
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
                    <TagsOverTime jobs={jobs as JobDetails[]} category={activeTab} />
                }
            </div>            
        </div>
    );
};

export default Keywords;
