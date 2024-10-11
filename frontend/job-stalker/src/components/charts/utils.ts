import { JobDetails } from "../job";
// Helper functions for rendering charts

export let getJobsByDate = (jobs: JobDetails[], addEmpty=true) => {
    const one_day = 24 * 60 * 60 * 1000; // milliseconds in a day
    let job_groups = jobs.reduce((acc: any, job: JobDetails) => {
        const date = new Date(job.date_posted);
        const date_str = `${date.getMonth() + 1}/${date.getDate() + 1}/${date.getFullYear()}`;
        let dateIndex = acc.findIndex((d: any) => d.date === date_str);
        if (dateIndex === -1) {
            dateIndex = acc.push({date: date_str}) - 1;
        }
        if (job.company in acc[dateIndex]) {
            acc[dateIndex][job.company]++;
        } else {
            acc[dateIndex][job.company] = 1
        }

        return acc;
    }, [])
    .sort((a: any, b: any) => new Date(a.date).getTime() - new Date(b.date).getTime() * -1);
    if (addEmpty) {
        job_groups = job_groups.reduce((acc: any, group: any) => {
            if (acc.length > 1) {
                let now = new Date();
                let prevDate: any = new Date(acc[acc.length - 1].date);
                let date: any = new Date(group.date);
                // If date is greater than the previous date, it means that it went to the next year
                if (date > prevDate) {
                    date = new Date(group.date);
                    prevDate = new Date(`${acc[acc.length - 1].date}/${now.getFullYear()}`);
                }
                let diff = prevDate - date;
                let nextDay = new Date(prevDate);
                while (diff > one_day) {
                    nextDay.setDate(nextDay.getDate() - 1);
                    acc.push({
                        date: `${nextDay.getMonth() + 1}/${nextDay.getDate()}/${nextDay.getFullYear()}`,
                    });
 
                    diff -= one_day;
                }
            }
            acc.push(group);

            return acc;
        }, []);
    }

    job_groups = job_groups.map((group: any) => {
        let date: any = new Date(group.date);
        group.date = `${Weekdays[date.getDay()]?.substring(0, 3)} ${date.getMonth() + 1}/${date.getDate()}`;
        return group;
    });

    return job_groups;
}

export const Weekdays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
