const { app, BrowserWindow } = require('electron');
const WebSocket = require('ws'); // WebSocketモジュールを追加
const bonjour = require('bonjour')(); // bonjourモジュールを追加

let mainWindow;
let isWorking;

async function createWindow () {
  // mDNSサービスを開始
  const bonjourService = bonjour.publish({ name: 'bokumetsu', type: 'http', port: 8000 });
  
  bonjourService.on('error', (error) => {
    console.error('mDNS service error:', error);
  });

  bonjourService.on('up', () => {
    console.log('mDNS service is up and running');
    console.log('mDNS service published: http://bokumetsu.local');
  });

  // WebSocketサーバーを作成
  const wss = new WebSocket.Server({ port: 8000 });

  wss.on('connection', (ws) => {
    ws.on('message', (message) => {
      const data = JSON.parse(message);
      if (data.type === 'status') {
        isWorking = data.isWorking;
        ws.send(JSON.stringify({ success: true }));
      }
    });

    (async function sendStatus() {
      while (true) {
        ws.send(JSON.stringify({ isWorking }));
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    })();
  });

  console.log('WebSocket server running at ws://127.0.0.1:8000/');

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
