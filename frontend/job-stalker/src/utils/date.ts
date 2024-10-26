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
    const day = `${date.getDate() < 9 ? '0' : ''}${date.getDate() + 1}`;
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