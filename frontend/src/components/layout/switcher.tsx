import React, { useState } from 'react';
import '../../styles/switcher.css';

type SwitcherTabProps = {
    index: number;
    activeIdx: number;
    text: string;
    setSelectedTab: (activeTab: number) => void;
}

const SwitcherTab = (props: SwitcherTabProps) => {
    const { index, activeIdx, text, setSelectedTab } = props;
    const handler = () => {
        setSelectedTab(index);
    }

    return (
        <div className={`switcher-tab ${index === activeIdx ? "switcher-tab-active" : ""}`} onClick={handler}>{text}</div>
    )
}

type SwitcherOption = {
    tab: string;
    content: React.ReactElement;
}

type SwitcherProps = {
    title: string;
    job_count: number;
    options: SwitcherOption[]
}

const Switcher = (props: SwitcherProps) => {
    const [ selectedOption, setSelectedOption ] = useState(0);

    return (
        <div className="switcher">
            <div className="title-area">
                <div className="switcher-tabs">
                    {props.options.map((option, index) => <SwitcherTab key={index} index={index} text={option.tab} activeIdx={selectedOption} setSelectedTab={setSelectedOption} />)}
                </div>
                <h2><span className="meta">Search results: </span>{props.job_count}</h2>
            </div>
            <div className="switcher-content">
                {props.options[selectedOption].content}
            </div>
        </div>
    )
}

export default Switcher;