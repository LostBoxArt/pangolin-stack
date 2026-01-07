const http = require('http');
const https = require('https');

const TARGET_HOST = process.env.TARGET_HOST || 'torrent.dennisb.xyz';
const TARGET_IP = process.env.TARGET_IP || '192.168.0.10';
const LISTEN_PORT = process.env.LISTEN_PORT || 8081;

console.log(`qBit Proxy listening on http://0.0.0.0:${LISTEN_PORT} -> https://${TARGET_HOST} (${TARGET_IP})`);

http.createServer((req, res) => {
    // console.log(`[Proxy] ${req.method} ${req.url}`);

    const options = {
        hostname: TARGET_IP,
        port: 443,
        path: req.url,
        method: req.method,
        headers: {
            ...req.headers,
            host: TARGET_HOST
        },
        rejectUnauthorized: false
    };

    const proxyReq = https.request(options, (proxyRes) => {
        // Strip the 'secure' flag from cookies to allow Homarr (non-HTTPS) to handle them
        if (proxyRes.headers['set-cookie']) {
            proxyRes.headers['set-cookie'] = proxyRes.headers['set-cookie'].map(cookie =>
                cookie.replace(/;\s*secure/gi, '')
            );
        }

        res.writeHead(proxyRes.statusCode, proxyRes.headers);
        proxyRes.pipe(res);
    });

    req.pipe(proxyReq);

    proxyReq.on('error', (e) => {
        console.error(`Proxy Error: ${e.message}`);
        res.statusCode = 502;
        res.end();
    });
}).listen(LISTEN_PORT, '0.0.0.0');
