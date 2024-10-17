const { app, BrowserWindow } = require('electron');
const http = require('http'); // HTTPモジュールを追加

let mainWindow;
let isWorking = true; // 初期状態

function createWindow () {
  // Webサーバーを作成
  const server = http.createServer((req, res) => {
    if (req.method === 'POST' && req.url === '/status') {
      let body = '';
      req.on('data', chunk => {
        body += chunk.toString();
      });
      req.on('end', () => {
        const data = JSON.parse(body);
        isWorking = data.isWorking;
        res.writeHead(200, {'Content-Type': 'application/json'});
        res.end(JSON.stringify({ success: true }));
      });
    } else if (req.method === 'GET' && req.url === '/status') {
      res.writeHead(200, {'Content-Type': 'application/json'});
      res.end(JSON.stringify({ isWorking }));
    } else {
      res.writeHead(404, {'Content-Type': 'text/plain'});
      res.end('Not Found');
    }
  });

  // サーバーをポート3000でリッスン
  server.listen(8000, '127.0.0.1', () => {
    console.log('Server running at http://127.0.0.1:8000/');
  });

  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true,
    },
  });

  mainWindow.loadFile('index.html');
  mainWindow.on('closed', function () {
    mainWindow = null;
  });
}

app.on('ready', createWindow);

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', function () {
  if (mainWindow === null) {
    createWindow();
  }
});
