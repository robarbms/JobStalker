import React, { useContext } from 'react';
import { Line, CartesianGrid, XAxis, YAxis, Tooltip, Legend, Bar, BarChart, ComposedChart, Cell } from 'recharts';
import TechTags from '../../utils/tech_keywords.json';
import DSTags from '../../utils/ds_keywords.json';
import DesignTags from '../../utils/design_keywords.json';
import { JobContext } from '../../App';
import { JobDetails } from '../job';
import { getJobsByDate, filterJobs } from '../charts/utils';
import { getTagColors } from './tagColors';
import { dateToKey, keyToDate } from '../../utils/date';
import { KeywordGroupName, keywordGroups} from '../charts/keywords';

type TagsOverTimeProps = {
    jobs: JobDetails[];
    category: KeywordGroupName;
}

export default function TagsOverTime (props: TagsOverTimeProps) {
    const { jobs, category }: {
        jobs: JobDetails[],
        category: KeywordGroupName
    } = props;
    const categoryData = keywordGroups[category];
    const compiledTags = {}
    // filter tags to only the current active tab

    const filteredTags = jobs.map((job) => {

    })

    const { allJobs } = useContext(JobContext);
    const colors = getTagColors();
    const getColor = (tag: string) => {
        const hsl = colors[tag];
        return `hsl(${hsl.hue}, ${hsl.saturation}%, ${hsl.lightness}%)`;
    }

    const timeSinceStart = new Date().getTime() - new Date("2024-09-17").getTime();
    const daysSinceStart = Math.floor(timeSinceStart / (1000 * 60 * 60 * 24)) + 1;

    const jobsSinceStart = filterJobs(jobs ?? allJobs, daysSinceStart);
    const tags = TechTags.concat(DSTags as any);
    // Collect top level categories as a hash map
    const categories = tags.reduce((cats: any, cat: any) => {
        cats[cat.name] = 0;
        return cats;
    }, {});

    // Storing category totals across all days
    const category_totals = Object.assign({}, categories);

    // Map tags in sub categories to their parent category
    const sub_cat_map = tags.reduce((subcats: any, cat: any) => {
        let category = cat.name;
        for(let key in cat) {
            if (key !== "name" && Array.isArray(cat[key])) {
                cat[key].forEach((sub: any) => {
                    if (sub.type === "version control") return;
                    subcats[sub.name] = category;
                    if (sub.creator) {
                        subcats[sub.creator] = category;
                    }
                    if (sub.versions) {
                        sub.versions.forEach((ver: any) => {
                            subcats[ver] = category;
                        })
                    }
                })
            }
        }
        return subcats;
    }, {});

    // Storing tag counts by date
    const tag_counts: any = {}

    // Adds tags by date and to the category totals
    jobsSinceStart.forEach((job: JobDetails) => {
        const key = dateToKey(job.date_posted);
        if (!(key in tag_counts)) {
            // Create a category count for the date
            tag_counts[key] = Object.assign({}, categories);
        }
        (job.tags as any[]).forEach((tag: any) => {
            let tag_point = tag;
            // If the tag is not a category, map it to the category
            if (!(tag_point in categories)) {
                if (tag in sub_cat_map){
                    tag_point = sub_cat_map[tag];
                }
                else {
                    return;
                }
            }
            if(tag_point in categories) {
                // Add the tag to the date and to the total
                tag_counts[key][tag_point] += 1;
                category_totals[tag_point] += 1;
            }
        });
    });

    // convert the categories to an array for sorting
    let category_totals_ary = [];
    for (let key in category_totals) {
        category_totals_ary.push({
            name: key,
            count: category_totals[key]
        });
    }
    category_totals_ary.sort((a: any, b: any) => b.count - a.count);
    const top_ten_cats = category_totals_ary.slice(0, 10);

    // Create a tag map for the top 10 categories
    const top_ten_map = top_ten_cats.reduce((map: any, total: any) => {
            map[total.name] = total.count
        return map;
    }, {});

    // Clean up to the total counts with only the top 10 categories and with the current date
    const data = [];
    for (let date_key in tag_counts) {
        const dataItem = tag_counts[date_key];
        for (let key in dataItem) {
            if (!(key in top_ten_map)) {
                delete dataItem[key];
            }
        }
        const date = keyToDate(date_key);
        if (date) {
            const date_str = `${date?.getMonth() + 1}/${date.getDate() + 1}`;
            dataItem.date = date_str;
            data.unshift(dataItem);
        }
    }

    return (
        <div className="tags-over-time">
            <h2>Technology Trends</h2>
            <ComposedChart width={1100} height={200} data={data}>
            <CartesianGrid />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            {top_ten_cats.map((category: any, idx: number) => {
                return <Line dataKey={category.name} key={idx} stroke={getColor(category.name)} dot={false} />
            })}
            <Legend />
            </ComposedChart>
            <BarChart width={1100} height={200} data={category_totals_ary}>
            <CartesianGrid />
            <XAxis dataKey="name" />
            <YAxis />
            <Bar dataKey="count">
                {category_totals_ary.map((cat: any, idx: number) => (
                    <Cell key={idx} fill={getColor(cat.name)} />
                ))}
            </Bar>
            <Tooltip />
            </BarChart>
        </div>
    )
}