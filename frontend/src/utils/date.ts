// Month names
export const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

// Weekday names
export const weekDays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

// Helper function to convert a date to a string key
export const dateToKey = (date: Date | string) => {
    if (typeof date === "string") {
        date = new Date(date);
    }
    const year = date.getFullYear();
    const month = `${date.getMonth() < 9 ? '0' : ''}${date.getMonth() + 1}`
    const day = `${date.getDate() < 10 ? '0' : ''}${date.getDate()}`;
    return `${year}${month}${day}`
}

// Converts a date key back to a date
export const keyToDate = (key: string) => {
    const dateParts = key.match(/(\d{4})(\d{2})(\d{2})/);
    if (dateParts){
        const date = new Date(`${dateParts[2]}/${dateParts[3]}/${dateParts[1]}`);
        return date;
    }

    return null;
}

/* Renders a date object as YYYY-MM-DD for use by date inputs */
export const dateToString = (date: Date | undefined) => {
    date = date || new Date();
    const numbToString = (numb: number) => `${numb < 10 ? "0" : ""}${numb}`;
    return `${date.getFullYear()}-${numbToString(date.getMonth() + 1)}-${numbToString(date.getDate())}`;
}

/* An object used to hold date offset settings */
export type DateOffsetObj = {
    years?: number;
    months?: number;
    weeks?: number;
    days?: number;
    hours?: number;
    minutes?: number;
    seconds?: number;
    miliseconds?: number;
}

/* Returns a time based off of a date or current date time and a date offset setting object */
export const dateOffset = (dateObj: DateOffsetObj, date?: Date | undefined) => {
    const offsets: DateOffsetObj = {
        years: 1000 * 60 * 60 * 24 * 365,
        months: 1000 * 60 * 60 * 24 * 30,
        weeks: 1000 * 60 * 60 * 24 * 7,
        days: 1000 * 60 * 60 * 24,
        hours: 1000 * 60 * 60,
        minutes: 1000 * 60,
        seconds: 1000,
        miliseconds: 1,
    }
    let offsetTime = 0;
    date = date || new Date();
    let key: keyof DateOffsetObj;
    for (key in dateObj) {
        offsetTime += (dateObj[key] ?? 0) * (offsets[key] ?? 0)
    }
    return new Date(date.getTime() + offsetTime);
}
