import techKeywordsJson from '../../utils/tech_keywords.json'
import dsKeywordsJson from '../../utils/ds_keywords.json'
import designKeywordsJson from '../../utils/design_keywords.json'

export const getTagColors = () => {
    // Create a compilation of all tags to 
    //  equally distribute colors
    let tags = [{
        name: 'Developer',
    }, ...techKeywordsJson];
    tags = tags.concat([{
        name: 'Data Scientist'
    }, ...dsKeywordsJson] as any[]);
    tags = tags.concat([{
        name: 'Designer'
    }, ...designKeywordsJson] as any[]);
    const colors: any = {};

    // Figure out how spaced hue tints should be
    const divs = tags.length;
    const sep = Math.floor(255 / (divs - 1));

    for(let i = 0; i < tags.length; i++) {
        const tag: any = tags[i];
        const hue = i * sep;
        colors[tag.name] = {
            hue,
            saturation: 100,
            lightness: 50,
        }
        // Compile a flat list of sub items that are deduped
        const items = [];
        for(let key in tag) {
            if (key !== "name") {
                for (let ii = 0; ii < tag[key].length; ii++) {
                    const item: any = tag[key][ii];
                    if (!(item.name in colors)) {
                        items.push(item.name);
                    }
                    if ('versions' in item) {
                        for(let j = 0; j < item.versions.length; j++) {
                            const version = item.versions[j];
                            if (!(version in colors)) {
                                items.push(version);
                            }
                        }
                    }
                }
            }
        }
        const steps = Math.floor(Math.sqrt(items.length));
        const step_sep = Math.floor(40 / steps);
        const inter = Math.floor(items.length / steps) + 1;
        const inter_sep = Math.floor(40 / inter);

        items.forEach((item, idx) => {
            colors[item] = {
                hue,
                saturation: 100 - (Math.floor(idx / steps) +1) * step_sep,
                lightness: 50 + (idx % inter + 1) * inter_sep * (idx % 2 ? 1 : -1)
            }
        })
    }
    
    return colors;
}

export const test_colors = () => {
    const errors: any = {};

    const colors = getTagColors();
    const colorToString = ({hue, saturation, lightness}: any) => {
        const numb = (n: number) => `${n < 100 ? "0" : ""}${n < 10 ? "0" : ""}${n}`;
        return numb(hue) + numb(saturation) + numb(lightness)
    }
    // Helper function to loop through colors and check validity
    const apply = (check: any) => {
        for (let key in colors) {
            const color = colors[key];
            const rslt = check(color, key);
            if (rslt !== true) {
                errors[key] = {
                    error: rslt,
                    color
                }
            }
        }
    }
    // Ensure all hues are between 0 & 255
    apply((color: any) => color.hue >= 0 && color.hue <= 255 ? true : "hue");
    // Ensure saturation is a positive number between 0 and 100
    apply((color: any) => color.saturation >= 0 && color.saturation <= 100 ? true : "saturation");
    // Ensure lightness is a positive number between 0 and 100
    apply((color: any) => color.lightness >= 0 && color.lightness <= 100 ? true : "lightness");
    // Ensure there are no duplicates
    const hash: any = {}
    apply((color: any, keyin: string) => {
        const key = colorToString(color);
        if (key in hash) {
            errors[hash[key]] = {
                error: "duplicate",
                color: colors[hash[key]]
            };
            return "duplicate";
        }
        hash[key] = keyin;
        return true;
    });

    return {
        passed: Object.keys(errors).length === 0,
        errors,
        count: Object.keys(errors).length
    }
}
