// src/index.js

import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles/index.css'; // You can remove this line if you don't have this file
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);