const { searchLocation } = require('./maps-core');

const query = process.argv[2];

if (!query) {
    console.error('Usage: search-maps.sh "location query"');
    process.exit(1);
}

searchLocation(query).catch(err => {
    console.error('❌ Error:', err.message);
    process.exit(1);
});
