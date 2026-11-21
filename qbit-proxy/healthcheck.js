const http = require('http');

const req = http.get({
    hostname: '127.0.0.1',
    port: process.env.LISTEN_PORT || 8081,
    path: '/api/v2/app/version',
    signal: AbortSignal.timeout(8000)
}, (res) => {
    let body = '';
    res.setEncoding('utf8');
    res.on('data', (chunk) => { body += chunk; });
    res.on('end', () => {
        process.exit(res.statusCode === 200 && /^v\d+\.\d+/.test(body.trim()) ? 0 : 1);
    });
    res.on('error', () => process.exit(1));
});
req.on('error', () => process.exit(1));
