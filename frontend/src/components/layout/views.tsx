import React from 'react';

/**
 * Props used by the Views component
 */
type ViewsProps = {
    activeViewIndex: number;
    viewOptions: {
        name: string;
        icon: any;
    };
    pivots: any[];
    viewContent: any[];
}

/**
 * Renders a container with switchable views
 * @param props 
 * @returns Views component
 */
const Views = (props: ViewsProps) => {
    return (
        <div className="view-switcher">

        </div>
    )
}

export default Views;