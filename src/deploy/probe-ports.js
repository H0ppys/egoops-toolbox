const http = require('http');
const ports = [8080, 8443, 9000, 3000, 8000, 18091, 5000];
for (const p of ports) {
  http.createServer((req, res) => { res.end('probe-' + p); })
    .listen(p, '0.0.0.0', () => console.log('listening', p))
    .on('error', e => console.log('skip', p, e.code));
}
setTimeout(() => process.exit(0), 60000);
