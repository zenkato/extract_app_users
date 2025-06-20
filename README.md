# アプリユーザーリスト抽出・アップロードツール

## 概要

このツールは、MySQLデータベースから特定の条件に一致するアプリケーションユーザーのリストを抽出し、CSVファイルとしてGoogle Driveの指定フォルダに自動でアップロードします。日次バッチ処理などでの使用を想定しています。

## 特徴

* **設定の分離**: データベースの接続情報やAPIキーなどの機密情報を `.env` ファイルに分離しているため、安全に設定を管理できます。
* **クリーンアーキテクチャ**: 各機能（DBアクセス、CSV書き込み、Google Driveアップロード）が独立したクラスとして設計されており、保守・拡張・テストが容易です。
* **堅牢なエラーハンドリング**: 処理の各段階で発生しうるエラーを検知し、詳細なログファイル (`pipeline.log`) に記録します。
* **再利用性**: 各コンポーネントは依存性の注入（DI）パターンで疎結合に設計されているため、個々の機能を別のプロジェクトで再利用することも可能です。

## ファイル構成

```
extract_app_users/
├── .env                  # 環境変数ファイル (各自で作成)
├── .gitignore            # Gitの無視リスト
├── credentials.json      # Google API認証情報 (各自で配置)
├── README.md             # このファイル
├── requirements.txt      # 依存ライブラリ
├── main.py               # アプリケーションを起動するエントリーポイント
└── app_extractor/        # ソースコードパッケージ
    ├── __init__.py     # Pythonパッケージマーカー
    ├── config.py       # 環境変数を読み込む設定モジュール
    ├── data_fetcher.py # データ取得クラス
    ├── exceptions.py   # カスタム例外クラス
    ├── file_writer.py  # CSV書き込みクラス
    ├── pipeline.py     # 全体を制御するパイプラインクラス
    └── uploader.py     # Google Driveアップロードクラス
```

## セットアップ手順

### 1. Python環境の準備
このプロジェクトは **Python 3.9以上** を推奨します。

### 2. 依存ライブラリのインストール
ターミナルで以下のコマンドを実行し、必要なライブラリをインストールします。

```bash
pip install -r requirements.txt
```

### 3. Google API認証情報の設定

1.  [Google Cloud Console](https://console.cloud.google.com/) にアクセスし、新しいプロジェクトを作成するか、既存のプロジェクトを選択します。
2.  「APIとサービス」>「ライブラリ」で **Google Drive API** を検索し、有効にします。
3.  「APIとサービス」>「認証情報」に移動し、「認証情報を作成」>「OAuth クライアント ID」を選択します。
4.  アプリケーションの種類で「デスクトップアプリ」を選択し、名前を付けます。
5.  作成後、JSONファイルをダウンロードし、ファイル名を `credentials.json` に変更して、このプロジェクトのルートディレクトリに配置してください。

### 4. 環境変数ファイルの設定

1.  プロジェクトのルートディレクトリに `.env` という名前でファイルを作成します。
2.  以下の内容を `.env` ファイルにコピーし、ご自身の環境に合わせて値を設定してください。

    ```dotenv
    # .env - 環境設定ファイル

    # --- MySQL 設定 ---
    DB_USER="your_mysql_user"
    DB_PASSWORD="your_mysql_password"
    DB_HOST="localhost"
    DB_NAME="your_database_name"

    # --- Google Drive 設定 ---
    # アップロードしたいGoogle DriveフォルダのURLの末尾にあるIDを指定
    # 例: [https://drive.google.com/drive/folders/xxxxxxxxxx](https://drive.google.com/drive/folders/xxxxxxxxxx)
    GOOGLE_DRIVE_FOLDER_ID="YOUR_GOOGLE_DRIVE_FOLDER_ID"

    # --- (通常は変更不要) ---
    GOOGLE_CREDENTIALS_FILE="credentials.json"
    GOOGLE_TOKEN_FILE="token.json"
    OUTPUT_DIR="./output"
    ```

## 実行方法

すべての設定が完了したら、ターミナルで以下のコマンドを実行します。

```bash
python main.py
```

### 初回実行時の注意
初回実行時には、Googleの認証画面がブラウザで開きます。アカウントを選択し、アクセスを許可してください。
認証が成功すると、プロジェクトルートに `token.json` というファイルが自動で生成されます。2回目以降の実行では、このファイルを使って自動的に認証が行われます。

## 処理フロー

1.  `main.py` が起動し、`.env` ファイルから設定情報を読み込みます。
2.  `MySqlFetcher` がデータベースに接続し、ユーザーデータを取得します。
3.  `CsvWriter` が取得したデータを、`output/` ディレクトリ内にShift-JIS形式のCSVファイルとして保存します。
4.  `GoogleDriveUploader` が、`token.json` を使ってGoogle Driveに認証・接続します。
5.  生成されたCSVファイルを、`.env` で指定した `GOOGLE_DRIVE_FOLDER_ID` のフォルダにアップロードします。
6.  アップロード完了後、ローカルの `output/` ディレクトリに生成されたCSVファイルは自動的に削除されます。
7.  すべての処理の進捗と結果は、コンソールと `pipeline.log` ファイルに出力されます。

---