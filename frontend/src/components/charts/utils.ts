import { JobDetails } from "../job";
// Helper functions for rendering charts

// Helper function to get data between a specific timeframe
export const filterJobs = (jobs: JobDetails[], end: number, start: number = 0) => {
    const now = new Date();
    now.setHours(0, 0, 0, 0);
    const day = 1000 * 60 * 60 * 24; // milliseconds in a day
    start = start === 0 ? new Date().getTime() : now.getTime() - start * day;
    end = start - end * day;

    return jobs.filter((job: JobDetails) => {
        const jobDateTime = new Date(job.date_posted).getTime();
        return jobDateTime < start && jobDateTime >= end;
    });
}



export let getJobsByDate = (jobs: JobDetails[], addEmpty=true, created_date=false) => {
    const one_day = 24 * 60 * 60 * 1000; // milliseconds in a day
    const timeOffset = 1000 * 60 * 60 * 7; // Times are coming in 7 hours behind because the DB time is in UTC
    let job_groups = jobs.reduce((acc: any, job: JobDetails) => {
        const date = new Date(new Date(created_date ? job.created_at : job.date_posted).getTime() + timeOffset + one_day);
        if (!isNaN(date.getTime())){
            const date_str = `${date.getMonth() + 1}/${date.getDate()}/${date.getFullYear()}`;
            let dateIndex = acc.findIndex((d: any) => d.date === date_str);
            if (date.getMonth() !== undefined && dateIndex === -1) {
                dateIndex = acc.push({date: date_str}) - 1;
            }
            if (job.company in acc[dateIndex]) {
                acc[dateIndex][job.company]++;
            } else {
                acc[dateIndex][job.company] = 1
            }
        }

        return acc;
    }, [])
    .sort((a: any, b: any) => new Date(a.date).getTime() <= new Date(b.date).getTime() ? 1 : -1);
    if (addEmpty) {
        job_groups = job_groups.reduce((acc: any, group: any) => {
            if (acc.length > 1) {
                let prevDate: any = new Date(acc[acc.length - 1].date);
                let date: any = new Date(group.date);
                let nextDay = new Date(prevDate.getTime() - one_day);
                while (nextDay > date) {
                    acc.push({
                        date: `${nextDay.getMonth() + 1}/${nextDay.getDate()}/${nextDay.getFullYear()}`,
                    });
 
                    nextDay = new Date(nextDay.getTime() - one_day);
                }
            }
            acc.push(group);

            return acc;
        }, []);
    }

    job_groups = job_groups.map((group: any) => {
        let date: any = new Date(group.date);
        group.date = `${Weekdays[date.getDay()]?.substring(0, 3)} ${date.getMonth() + 1}/${date.getDate()}`;
        let Total = 0;
        for (let key in group) {
            if (key !=='date') {
                Total += group[key];
            }
        }
        group.Total = Total;
        return group;
    });

    return job_groups;
}

export const Weekdays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
