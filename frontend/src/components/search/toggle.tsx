import React from 'react';

type ToggleProps = {
    enabled: boolean;
    toggle: React.MouseEventHandler;
}

const Toggle = (props: ToggleProps) => {
    const { enabled, toggle } = props;

    return (
        <div className={`toggle ${enabled ? "enabled" : ""}`} onClick={toggle}></div>
    )
}

export default Toggle;