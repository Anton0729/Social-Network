  const path = require('path');

module.exports = {
    entry: './assets/scripts/index.js',
    output: {
        'path': path.resolve(__dirname, 'network_life', 'static'),
        'filename': 'bundle.js'
    }
}