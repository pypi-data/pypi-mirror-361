# IconGenerator

IconGeneratorは、多様なスタイルのアイコンを生成できるPythonパッケージです。  
GitHubのユーザアイコン風の画像も生成可能で、プロジェクトやアプリケーションのアイコン作成を手軽に行えます。

---

## 主な特徴

- 多彩なアイコンパターン生成（幾何学模様、ランダムカラーなど）  
- GitHubユーザアイコン風（Identicon風）アイコン生成機能  
- シンプルなAPI設計で使いやすい

---

## インストール

```bash
pip install icon-generator
```

---

## 使い方

```python
import uuid
from icon_generator import GitIconGenerator

unique_id = uuid.uuid4()
generator = GitIconGenerator(unique_id)
img_io = generator.generate_on_memory()

# バイナリデータとして取得
png_binary = img_io.getvalue()

# ファイルに書き込み
with open("icon.png", "wb") as f:
    f.write(png_binary)

```