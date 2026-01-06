# shutter-count

カメラ画像ファイルからシャッター回数を取得するスクリプトです

## 必要なもの

- Python 3.9+
- [exiftool](https://exiftool.org/)

### exiftoolのインストール

| OS | コマンド |
|----|----------|
| macOS | `brew install exiftool` |
| Ubuntu/Debian | `sudo apt install libimage-exiftool-perl` |
| Windows | [公式サイト](https://exiftool.org/)からダウンロード |

💡 exiftoolをインストールしたくない場合は、下記のDocker経由で実行できます。

## Dockerで使う
### 1. イメージをビルド

```bash
docker build -t shutter-count .
```

### 2. 実行

画像ファイルのあるディレクトリをコンテナにマウントして実行します。

```bash
# 基本形式
docker run --rm -v <画像のあるディレクトリ>:/images shutter-count /images/<ファイル名>

# 例: ~/Pictures/sony にある DSC00001.arw を解析
docker run --rm -v ~/Pictures/sony:/images shutter-count /images/DSC00001.arw

# 例: カレントディレクトリの全ARWファイルを解析
docker run --rm -v "$(pwd)":/images shutter-count /images/*.arw
```

## 使い方

```bash
# 基本
python shutter_count.py image.arw

# 出力例:
# File: image.arw
# Camera: SONY ILCE-7CR
# Shutter Count: 4,365

# 複数ファイル
python shutter_count.py *.arw

# 数値のみ出力
python shutter_count.py -q image.arw

# JSON出力
python shutter_count.py --json image.arw
```

## 対応カメラ

- Sony (α7, α9, α1 など)
- Canon, Nikon, Fujifilm (対応予定)