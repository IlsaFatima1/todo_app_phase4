// Simple server to serve Next.js production build
const { createServer } = require('http');
const { createReadStream } = require('fs');
const { join, extname } = require('path');
const { parse } = require('url');

const port = process.env.PORT || 3000;
const publicDir = './public';

const mimeTypes = {
  '.html': 'text/html',
  '.css': 'text/css',
  '.js': 'text/javascript',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.txt': 'text/plain',
  '.pdf': 'application/pdf',
  '.zip': 'application/zip',
  '.wav': 'audio/wav',
  '.mp3': 'audio/mpeg',
  '.mp4': 'video/mp4',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2'
};

const server = createServer((req, res) => {
  const parsedUrl = parse(req.url, true);
  let pathname = parsedUrl.pathname;

  // Default to index.html if pathname is root
  if (pathname === '/') {
    pathname = '/index.html';
  }

  const filePath = join(publicDir, pathname);

  const ext = extname(filePath).toLowerCase();
  const contentType = mimeTypes[ext] || 'application/octet-stream';

  res.writeHead(200, { 'Content-Type': contentType });

  const stream = createReadStream(filePath);
  stream.pipe(res);

  stream.on('error', (err) => {
    if (err.code === 'ENOENT') {
      res.writeHead(404);
      res.end('File not found');
    } else {
      res.writeHead(500);
      res.end('Internal server error');
    }
  });
});

server.listen(port, () => {
  console.log(`Server running on port ${port}`);
});