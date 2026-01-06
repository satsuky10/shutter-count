# shutter-count

カメラ画像ファイルからシャッター回数を取得するスクリプト。

## 必要なもの

- Python 3.9+
- [exiftool](https://exiftool.org/)

### exiftoolのインストール

```bash
# macOS
brew install exiftool

# Ubuntu/Debian
sudo apt install libimage-exiftool-perl
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

※ すべてのカメラがシャッター回数をEXIFに記録するわけではありません。
