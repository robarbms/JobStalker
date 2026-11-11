import React from "react";
import { ReactComponent as AppleIcon } from '../static/apple.svg';
import { ReactComponent as NetflixIcon } from '../static/netflix.svg';
import { ReactComponent as GoogleIcon } from '../static/google.svg';
import { ReactComponent as MicrosoftIcon } from '../static/microsoft.svg';
import { ReactComponent as AdobeIcon } from '../static/adobe.svg';
import { ReactComponent as AmazonIcon } from '../static/amazon.svg';
import { ReactComponent as HuggingfaceIcon } from '../static/huggingface.svg';
import { ReactComponent as OpenaiIcon } from '../static/openai.svg';
import { ReactComponent as NvidiaIcon } from '../static/nvidia.svg';
import { ReactComponent as MetaIcon } from '../static/meta.svg';
import { ReactComponent as SalesforceIcon } from '../static/salesforce.svg';
import { ReactComponent as Zillow } from '../static/zillow.svg';
import { ReactComponent as AtlassianIcon } from '../static/atlassian.svg';
import { ReactComponent as ExpediaIcon } from '../static/expedia.svg';
import { ReactComponent as AirbnbIcon } from '../static/airbnb.svg';
import BlizzardIconSrc from '../static/blizzard.png';

export type Company = {
    icon: JSX.Element;
    color: string;
}

export const companyData: {[key: string]: Company} = {
    Adobe: {
        icon: <AdobeIcon className="icon" />,
        color: "#ff6038",
    },
    Airbnb: {
        icon: <AirbnbIcon className="icon" />,
        color: "rgb(255 56 92)",
    },
    Apple: {
        icon: <AppleIcon className="icon" />,
        color: "#999"
    },
    Amazon: {
        icon: <AmazonIcon className="icon" />,
        color: "#f79400",
    },
    Atlassian: {
        icon: <AtlassianIcon className="icon" />,
        color: "#1868db"
    },
    Blizzard: {
        icon: <img src={BlizzardIconSrc} className="icon" />,
        color: "#67a3f6"
    },
    Expedia: {
        icon: <ExpediaIcon className="icon expedia-icon" />,
        color: "#fddb32"
    },
    Google: {
        icon: <GoogleIcon className="icon" />,
        color: "#bb6dd6",
    },
    Meta: {
        icon: <MetaIcon className="icon" />,
        color: "#007cf2"
    },
    Microsoft: {
        icon: <MicrosoftIcon className="icon" />,
        color: "#13acf0",
    },
    Netflix: {
        icon: <NetflixIcon className="icon" />,
        color: "#e50914"
    },
    Nvidia: {
        icon: <NvidiaIcon className="icon" />,
        color: "#72b300",
    },
    Salesforce: {
        icon: <SalesforceIcon className="icon" />,
        color: "#00a6ed",
    },
    Zillow: {
        icon: <Zillow className="icon" />,
        color: "#000dff"
    }
}

export const applyCompanyColors = (companies: any[]) => 
    companies.reduce((acc, company, index) => {
        if (!(company in companyData) || !('color' in companyData[company])) {
            acc[company] = {
                color: colorFromIndex(index)
            };
        }
        else {
            acc[company] = {
                color: companyData[company].color
            };
        }
        return acc;
    }, {} as {[key: string]: string});

export const colorFromIndex = (index: number) => {
    const r = index % 6 === 0 || index % 6 === 3 || index % 6 === 4 ? (index + 10) * 20 % 255 : 0;
    const g = index % 6 === 1 || index % 6 === 3 || index % 6 === 5 ? (index + 10) * 20 % 255 : 0;
    const b = index % 6 === 2 || index % 6 === 4 || index % 6 === 5 ? (index + 10) * 20 % 255 : 0;

    return `rgb(${r}, ${g}, ${b})`;
}

export const CompanyIcon = ({name, color: color}: {name: string, color: string | {color: string}}) => {
    let letters = name.substring(0, 2);
    if (name.trim().match(/\W/)) {
        const matches = name.match(/\W/g);
        if (matches) {
            letters = matches.slice(0, 1).join("");
        }
    }
    const upperCaseLetters = name.match(/[A-Z]/g)?.slice(0, 2).join(""); 
    if (upperCaseLetters && upperCaseLetters.length > 1) {
        letters = upperCaseLetters;
    }
    letters = letters.toUpperCase();
    const iconColor = typeof color === 'string' ? color : color.color;
    return <span className="icon job-card-temp-icon" style={{backgroundColor: iconColor}}>{letters}</span>;
}

export const getCompanyData = (companies: string[]) => {
    const colors: {[key: string]: string} = applyCompanyColors(companies);
    return companies.reduce((acc, company) => {
    if (company in companyData) {
        acc[company] = companyData[company];
    } else {
        acc[company] = {
            icon: <CompanyIcon name={company} color={colors[company]} />,
            color: colors[company]
        };
    }
    return acc;
}, {} as {[key: string]: {
    icon: React.ReactNode;
    color: string;
}})
};
