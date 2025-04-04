# PDF OCR with Gemini Flash 2.0

OpenRouter経由でGemini Flash 2.0を使用し、PDF文書のOCR処理を行うツール

## 特徴
- 高解像度でのPDF→画像変換（デフォルト300DPI）
- 複数ページ対応のバッチ処理
- JSON形式での構造化出力
- 生のAPIレスポンスのオプション保存
- 多言語テキスト抽出対応

## 動作要件
- Python 3.8+
- Tesseract OCR（システムにインストール必須）
- Poppler（Windowsの場合はPATHを通す必要あり）

## インストール
```bash
# 依存パッケージのインストール
pip install python-dotenv openai pdf2image
```

## 使用方法
### 基本コマンド
```bash
python ocr_pdf.py input.pdf
```

### オプション引数
| オプション | 説明 | デフォルト値 |
|-----------|------|-------------|
| `--api-key` | OpenRouter APIキー | 環境変数`OPENROUTER_API_KEY` |
| `--dpi` | 画像変換解像度（300-1200推奨） | 300 |
| `--format` | 変換画像フォーマット（png/jpeg/tiff） | png |
| `--include-raw` | 生APIレスポンスを出力に含める | オフ |

### 使用例
```bash
# 高解像度で処理（600DPI）
python ocr_pdf.py document.pdf --dpi 600

# JPEG形式で処理し生レスポンスを保存
python ocr_pdf.py document.pdf --format jpeg --include-raw
```

## 出力形式
`入力ファイル名_ocr.json` として保存されるJSON構造:
```json
{
  "pages": [
    {
      "index": 1,
      "text": "抽出されたテキスト...",
      "raw_response": "API生レスポンス..." // --include-raw指定時のみ含まれる
    }
  ]
}
```

## トラブルシューティング
- **文字認識精度が低い場合**  
  `--dpi`値を上げて高解像度で再試行（例：`--dpi 600`）

- **特殊文字/数式が正しく認識されない場合**  
  `--format tiff`でロスレス形式を試す

- **メモリエラーが発生する場合**  
  DPI値を下げるか、PDFをページ単位で分割

## 注意事項
- OpenRouter APIキーは[OpenRouter公式サイト](https://openrouter.ai/)で取得
- 処理時間はPDFのページ数と解像度に比例して増加
- 高DPI設定時はシステムメモリを十分に確保

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
