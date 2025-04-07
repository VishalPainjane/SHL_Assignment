const express = require('express');
const app = express();
const port = 3000;

// Middleware to parse JSON body
app.use(express.json());

// API endpoint to handle query
app.post('/api/query', (req, res) => {
    const { query } = req.body;

    if (!query) {
        return res.status(400).json({ error: 'Query parameter is required' });
    }

    // Process the query (example: reverse the text)
    const result = {
        original: query,
        processed: query.split('').reverse().join('') // Example processing
    };

    res.json(result);
});

// Start the server
app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});
