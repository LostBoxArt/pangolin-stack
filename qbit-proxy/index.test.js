const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { EventEmitter } = require('node:events');
const { PassThrough } = require('node:stream');
const { test } = require('node:test');

function proxy() {
    let handler, options, respond;
    const upstream = new PassThrough();
    const response = new PassThrough();
    response.statusCode = 200;
    response.headersSent = false;
    response.writeHead = (status, headers) => {
        response.statusCode = status;
        response.headers = headers;
        response.headersSent = true;
    };
    response.on('error', () => {});
    vm.runInNewContext(fs.readFileSync(path.join(__dirname, 'index.js'), 'utf8'), {
        require: (name) => name === 'http' ? {
            createServer: (fn) => { handler = fn; return { listen() {} }; }
        } : {
            request: (opts, fn) => { options = opts; respond = fn; return upstream; }
        },
        process: { env: { TARGET_HOST: 'torrent.example.test', TARGET_IP: '192.0.2.10' } },
        console: { log() {}, error() {} },
        AbortSignal: { timeout: (ms) => ({ timeout: ms }) }
    });
    const request = new PassThrough();
    Object.assign(request, {
        method: 'POST', url: '/api/v2/example',
        headers: { host: 'untrusted.example.test', 'content-type': 'application/json' }
    });
    handler(request, response);
    return { options, request, upstream, response, respond };
}

function upstreamResponse(status = 200) {
    const stream = new PassThrough();
    stream.statusCode = status;
    stream.headers = { 'set-cookie': ['SID=test; Secure; HttpOnly', 'other=value; secure', 'QBT_SID_8080=test; Secure; HttpOnly'] };
    return stream;
}

test('TLS, upstream host, request forwarding and total deadline', () => {
    const p = proxy();
    assert.equal(p.options.rejectUnauthorized, true);
    assert.equal(p.options.headers.host, 'torrent.example.test');
    assert.equal(p.options.hostname, '192.0.2.10');
    assert.equal(p.options.method, 'POST');
    assert.equal(p.options.path, '/api/v2/example');
    assert.equal(p.options.signal.timeout, 10000);
    let body = '';
    p.upstream.on('data', (chunk) => { body += chunk; });
    p.request.end('payload');
    assert.equal(body, 'payload');
});

test('upstream response and Secure-cookie compatibility stay intact', () => {
    const p = proxy();
    const reply = upstreamResponse(201);
    let body = '';
    p.response.on('data', (chunk) => { body += chunk; });
    p.respond(reply);
    reply.end('result');
    assert.equal(p.response.statusCode, 201);
    assert.equal(p.response.headers['set-cookie'][0], 'SID=test; HttpOnly');
    assert.equal(p.response.headers['set-cookie'][1], 'other=value');
    assert.equal(p.response.headers['set-cookie'][2], 'QBT_SID_8080=test; HttpOnly');
    assert.equal(body, 'result');
    const empty = proxy();
    empty.respond(upstreamResponse(204));
    assert.equal(empty.response.statusCode, 204);
});

test('TLS or connection failure before headers returns 502', () => {
    const p = proxy();
    p.upstream.emit('error', new Error('certificate rejected'));
    assert.equal(p.response.statusCode, 502);
    assert.equal(p.response.writableEnded, true);
});

test('deadline before headers returns 504', () => {
    const p = proxy();
    const error = new Error('deadline');
    error.name = 'AbortError';
    p.upstream.emit('error', error);
    assert.equal(p.response.statusCode, 504);
    assert.equal(p.response.writableEnded, true);
});

test('failure after headers destroys the incomplete response', () => {
    const p = proxy();
    p.respond(upstreamResponse());
    p.upstream.emit('error', new Error('upstream failed'));
    assert.equal(p.response.statusCode, 200);
    assert.equal(p.response.destroyed, true);
});

test('an upstream response-stream failure destroys the downstream response', () => {
    const p = proxy();
    const reply = upstreamResponse();
    p.respond(reply);
    reply.emit('error', new Error('incomplete body'));
    assert.equal(p.response.destroyed, true);
});

function health(status, body, errorEvent) {
    const req = new EventEmitter();
    const res = new EventEmitter();
    res.statusCode = status;
    res.setEncoding = () => {};
    let options, respond, exitCode;
    vm.runInNewContext(fs.readFileSync(path.join(__dirname, 'healthcheck.js'), 'utf8'), {
        require: () => ({ get: (opts, cb) => { options = opts; respond = cb; return req; } }),
        process: { env: {}, exit: (code) => { exitCode = code; } },
        AbortSignal: { timeout: (ms) => ({ timeout: ms }) }
    });
    if (errorEvent === 'request') req.emit('error', new Error('connection refused'));
    else {
        respond(res);
        if (errorEvent === 'response') res.emit('error', new Error('incomplete response'));
        else { res.emit('data', body); res.emit('end'); }
    }
    return { options, exitCode };
}

test('health requires a successful qBittorrent version response through the proxy', () => {
    const result = health(200, 'v5.1.4\n');
    assert.equal(result.exitCode, 0);
    assert.equal(result.options.hostname, '127.0.0.1');
    assert.equal(result.options.path, '/api/v2/app/version');
    assert.equal(result.options.signal.timeout, 8000);
});

test('auth denials, an HTML login page and proxy errors are unhealthy', () => {
    for (const [status, body] of [[401, 'denied'], [403, 'denied'], [200, '<html>login</html>'], [502, ''], [504, '']]) {
        assert.equal(health(status, body).exitCode, 1);
    }
});

test('health connection and response errors fail', () => {
    assert.equal(health(200, '', 'request').exitCode, 1);
    assert.equal(health(200, '', 'response').exitCode, 1);
});
