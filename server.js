const express = require('express');
const path = require('path');

const app = express();
const PORT = 5000;

// Serve static files from public directory
app.use(express.static(path.join(__dirname, 'public')));

// Basic route
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// API route
app.get('/api/hello', (req, res) => {
    res.json({ message: 'Hello from the 02 project!' });
});

// Start server on all interfaces (0.0.0.0) to work with Replit proxy
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on http://0.0.0.0:${PORT}`);
});