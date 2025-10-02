// src/components/common/InputField.js

import React from 'react';

/**
 * A reusable input field component for forms.
 * @param {object} props - Component props.
 * @param {string} props.label - The text label for the input.
 * @param {string} props.type - The HTML input type (e.g., 'text', 'email', 'password').
 * @param {string} props.name - The name attribute of the input.
 * @param {string} props.value - The current value of the input.
 * @param {function} props.onChange - The function to call when the input value changes.
 * @param {boolean} props.required - Whether the input is required.
 * @param {string} props.placeholder - Placeholder text for the input.
 */
const InputField = ({ label, type = 'text', name, value, onChange, required = false, placeholder }) => {
  return (
    <div className="form-group">
      <label htmlFor={name}>{label}</label>
      <input
        type={type}
        id={name}
        name={name}
        value={value}
        onChange={onChange}
        required={required}
        placeholder={placeholder}
      />
    </div>
  );
};

export default InputField;