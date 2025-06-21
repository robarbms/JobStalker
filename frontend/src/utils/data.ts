import devKeywords from './tech_keywords.json';
import dataScienceKeywords from './ds_keywords.json';
import designKeywords from './design_keywords.json';
import { JobDetails } from '../components/job';

/**
 * Helper function that creates an object of days that are keyed by day
 * @param dateStart Date to begin the array
 * @param dateEnd Optional date to end the array. Uses todays date if no date end is provided
 */
export const getDateMap = (dateStart: string | Date, dateEnd?: string | Date) => {
    // initialize dateStart and dateEnd with Date objects to work with
    if (typeof dateStart === 'string') dateStart = new Date(dateStart);
    if (!dateEnd || dateEnd === '') dateEnd = new Date();
    else if (typeof dateEnd === 'string') dateEnd = new Date(dateEnd);

    const dateMap = {};
    const oneDayInMilliseconds = 1000 * 60 * 60 * 24;

    return dateMap;
}

/**
 * Creates a tagMap for storing data about tags such as counts or dates
 *  and a tagKeyMap for quick lookup of data about specific tags
 * @param data A JSON of keywords
 * @param group The group name that this will be a part of, example: Developer
 * @returns 
 */
export const getTagMappings = (data: any) => {
    const tagMap: any = {};
    const tagKeyMap: {[key: string]: any} = {};
    for (let group in data){
        const group_data = data[group];
        const groupObj: any = {
            children: {}
        };
        group_data.forEach((category: any) => {
            const path = [group]
            const catObj: any = {
                children: {}
            };
            tagKeyMap[category.name] = { paths: [...path]};
            path.push(category.name);
            for (let key in category) {
                if (Array.isArray(category[key])) {
                    category[key].forEach((keyword: any) => {
                        catObj.children[keyword.name] = {};
                        tagKeyMap[keyword.name] = { paths: [...path]}
                    });
                }
            }
            groupObj.children[category.name] = catObj;
        });
        tagMap [group] = groupObj;
    }
    return { tagMap, tagKeyMap};
}

export const tagMappings = () => getTagMappings({
        Developer: devKeywords,
        'Data Scientist': dataScienceKeywords,
        Designer: designKeywords
    });

/**
 * Helper function to get the parent node of the tag mappings based on an array of parent nodes
 * @param data A data structure
 * @param paths An array of strings representing where in the data structure the data is
 * @returns 
 */
export const getParentFromPaths = (data: any, paths: string[]) => paths.reduce((curr, dir: string) => curr?.children?.[dir] ?? curr, data);

export const parseTags = (jobs: JobDetails[]) => {
    const keywordMappings = tagMappings();
    const tagCounts: any = {...keywordMappings.tagMap};
    const addTag = (tag: string | string[]) => {
        if (Array.isArray(tag)) tag.forEach(addTag);
        else {
            if (!(tag in keywordMappings.tagKeyMap)) return;
            const {paths} = keywordMappings.tagKeyMap[tag];
            let target = tagCounts;
            for (let i = 0; i < paths.length; i++) {
                if (!(paths[i] in target)) return;
                target = target[paths[i]];
                target.total = 'total' in target ? target.total + 1 : 1;
                target = target.children;
            }
            if (!(tag in target)) return;
            target = target[tag];
            target.count = 'count' in target ? target.count + 1 : 1;
        }
    }
    jobs.forEach(({tags}: {tags: string | string[]}) => addTag(tags));
    return tagCounts;
}