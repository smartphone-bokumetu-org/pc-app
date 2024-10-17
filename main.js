const { app, BrowserWindow } = require('electron');
const WebSocket = require('ws'); // WebSocketモジュールを追加

let mainWindow;
let isWorking = true; // 初期状態

function createWindow () {
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

    // 初期状態を送信
    ws.send(JSON.stringify({ isWorking }));
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
