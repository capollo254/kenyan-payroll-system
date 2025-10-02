// src/components/common/Button.js

import React from 'react';

/**
 * A reusable button component.
 * @param {object} props - Component props.
 * @param {function} props.onClick - The function to call when the button is clicked.
 * @param {string} props.children - The text or elements to display inside the button.
 * @param {string} props.className - Additional CSS classes for styling.
 * @param {boolean} props.disabled - Whether the button should be disabled.
 */
const Button = ({ onClick, children, className = 'btn-primary', disabled = false }) => {
  return (
    <button onClick={onClick} className={`btn ${className}`} disabled={disabled}>
      {children}
    </button>
  );
};

export default Button;