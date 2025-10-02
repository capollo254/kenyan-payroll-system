// src/components/dashboard/DashboardWidget.js

import React from 'react';

/**
 * A reusable component to display a key metric or piece of information.
 * @param {object} props - Component props.
 * @param {string} props.title - The title of the widget (e.g., "Total Employees").
 * @param {string|number} props.value - The main value or metric to display.
 * @param {string} props.description - A brief description or additional context.
 */
const DashboardWidget = ({ title, value, description }) => {
  return (
    <div className="card" style={{ textAlign: 'center' }}>
      <h3>{title}</h3>
      <div style={{ fontSize: '2.5em', fontWeight: 'bold', margin: '10px 0' }}>
        {value}
      </div>
      <p style={{ color: '#6c757d' }}>{description}</p>
    </div>
  );
};

export default DashboardWidget;