const express = require('express');
const router = express.Router();

// Handler for the /api/hello endpoint
router.get('/hello', (req, res) => {
    res.json({ message: 'Hello, World!' });
});

module.exports = router;