const { openGoogleMaps } = require('./maps-core');

openGoogleMaps().catch(err => {
    console.error('❌ Error:', err.message);
    process.exit(1);
});
