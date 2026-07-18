import React from 'react';
import './admin_panel.css';

export type AdminPanelProps = {
    open: boolean;
    setAdminPanel: (isOpen: boolean) => void;
}

const AdminPanel = (props: AdminPanelProps) => {
    return (
        <div className={`admin-panel ${props.open ? 'show' : 'hide'}`}>
            <div className="admin-panel-header">
                <h2>Admin Panel</h2>
                <div className="admin-panel-close" onClick={() => props.setAdminPanel(false)}>x</div>
            </div>
        </div>
    );
}

export default AdminPanel;
