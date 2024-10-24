# 注意！！
<span style="color: red;">PC側に接続しているSSIDがkeiomobile2またはCNSに繋がっている場合、PC側とラズパイ側の接続ができないので、ラズパイとPC側共に授業で提供されている同じSSIDに接続されている必要がある。</span>

# Setup

このプロジェクトをセットアップするには、以下の手順に従ってください。

1. **リポジトリをクローンする**:
   ```bash
   git clone https://github.com/smartphone-bokumetu-org/pc-app
   cd pc-app
   ```

2. **依存関係をインストールする**:
   プロジェクトのルートディレクトリで以下のコマンドを実行します。
   ```bash
   npm install
   ```

3. **アプリケーションを起動する**:
   以下のコマンドでアプリケーションを起動します。
   ```bash
   npm run start
   ```

4. **WebSocketサーバーの確認**:
   アプリケーションが起動したら、WebSocketサーバーが`ws://127.0.0.1:8000/`で動作していることを確認してください。

5. **mDNSサービスの確認**:
   mDNSサービスが`http://bokumetsu.local`で公開されていることを確認してください。

これでセットアップは完了です。アプリケーションが正常に動作していることを確認してください。
