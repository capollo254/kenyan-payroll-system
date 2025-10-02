// src/utils/formatters.js

/**
 * Formats a number as Kenyan Shillings currency.
 * @param {number} amount - The number to format.
 * @returns {string} The formatted currency string (e.g., "KES 1,234.56").
 */
export const formatCurrency = (amount) => {
  if (typeof amount !== 'number') {
    return 'KES 0.00';
  }

  const formatter = new Intl.NumberFormat('en-KE', {
    style: 'currency',
    currency: 'KES',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

  return formatter.format(amount);
};