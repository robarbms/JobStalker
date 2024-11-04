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
import { ReactComponent as SalesforceIcon } from '../static/salesforce.svg'

export type Company = {
    icon: JSX.Element;
    color: string;
}

export const companyData: {[key: string]: Company} = {
    Adobe: {
        icon: <AdobeIcon className="icon" />,
        color: "#ff6038",
    },
    Apple: {
        icon: <AppleIcon className="icon" />,
        color: "#999"
    },
    Amazon: {
        icon: <AmazonIcon className="icon" />,
        color: "#f79400",
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
    }
}
