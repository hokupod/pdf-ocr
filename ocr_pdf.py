import os
import tempfile
import base64
import json
from openai import OpenAI
from pdf2image import convert_from_path
import io
import argparse
from dotenv import load_dotenv

def process_pdf_with_ocr(api_key, input_pdf_path, dpi=300, format='png'):
    """
    PDFをGemini Flash 2.0 OCRで処理し、テキスト情報を抽出する

    Args:
        api_key (str): OpenRouter API キー
        input_pdf_path (str): 入力PDFのパス
        dpi (int): PDFからイメージへの変換時のDPI（解像度）
        format (str): 変換する画像フォーマット
    """
    # OpenAI APIクライアントの初期化（OpenRouter経由でGemini Flash 2.0にアクセス）
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )

    # 一時ディレクトリの作成
    with tempfile.TemporaryDirectory() as temp_dir:
        # PDFをイメージに変換（高解像度で）
        images = convert_from_path(
            input_pdf_path,
            dpi=dpi,  # 高解像度に設定
            fmt=format,  # 画像フォーマット
            grayscale=False,  # カラーで変換
            transparent=False,  # 透明度なし
            use_cropbox=True,  # クロップボックスを使用
            size=(None, None)  # 元のサイズを維持
        )

        # OCR結果を保存するための辞書
        ocr_results = {"pages": []}

        # 各ページを処理
        for i, image in enumerate(images):
            # イメージをバイトストリームに変換
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            image_bytes = img_byte_arr.read()

            # Base64エンコード
            image_data = base64.b64encode(image_bytes).decode('utf-8')

            try:
                # Gemini Flash 2.0でテキスト抽出
                ocr_response = client.chat.completions.create(
                    model="google/gemini-2.0-flash-001",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a professional OCR engine. Extract all visible text exactly as it appears. Preserve line breaks, spacing, special characters and formatting. Do not interpret or correct the text."
                        },
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Extract text verbatim from this image maintaining original layout including columns, tables, and mathematical notations."
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/png;base64,{image_data}"}
                                }
                            ]
                        }
                    ],
                    max_tokens=4096,
                    temperature=0.1  # 創造性を最低に設定
                )

                # 抽出されたテキスト
                extracted_text = ocr_response.choices[0].message.content

                # デバッグ用にOCR結果を出力
                print(f"\n===== ページ {i+1} のOCR結果 =====")
                print(extracted_text)
                print("================================\n")

                # OCR結果を辞書に追加
                page_result = {
                    "index": i+1,
                    "text": extracted_text,
                    "raw_response": str(ocr_response)
                }

                ocr_results["pages"].append(page_result)

            except Exception as e:
                print(f"ページ {i+1} の処理中にエラーが発生しました: {e}")

    return ocr_results

def main():
    # .envファイルから環境変数を読み込む
    load_dotenv()

    # 環境変数からAPIキーを取得
    env_api_key = os.getenv("OPENROUTER_API_KEY")

    parser = argparse.ArgumentParser(description='Gemini Flash 2.0 OCRを使用してPDFのテキスト抽出を行います')
    parser.add_argument('--api-key', help='OpenRouter API キー（指定がない場合は環境変数から取得）')
    parser.add_argument('input_pdf', help='入力PDFファイルのパス')
    parser.add_argument('--dpi', type=int, default=300, help='PDFからイメージへの変換時のDPI（解像度）')
    parser.add_argument('--format', choices=['png', 'jpeg', 'tiff'], default='png', help='変換する画像フォーマット')

    args = parser.parse_args()

    # コマンドラインオプションのAPIキーを優先、なければ環境変数から取得
    api_key = args.api_key if args.api_key else env_api_key

    if not api_key:
        print("エラー: OpenRouter APIキーが指定されていません。--api-keyオプションで指定するか、.envファイルにOPENROUTER_API_KEYを設定してください。")
        return

    # 出力ディレクトリの設定（入力ファイルと同じディレクトリ）
    input_path = os.path.abspath(args.input_pdf)
    output_dir = os.path.dirname(input_path)  # 変更箇所

    # 念のためディレクトリ存在確認（既に存在する場合は何もしない）
    os.makedirs(output_dir, exist_ok=True)

    # JSONファイルのパス生成
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    json_output_path = os.path.join(output_dir, f"{base_name}_ocr.json")

    # OCR処理実行
    ocr_results = process_pdf_with_ocr(api_key, args.input_pdf, args.dpi, args.format)

    # JSON保存
    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump(ocr_results, f, ensure_ascii=False, indent=2)

    print(f"処理が完了しました。OCR結果ファイル: {json_output_path}")
    print("\n注意: OCR結果が期待通りでない場合は、以下を試してください:")
    print("1. --dpi オプションで解像度を上げる (例: --dpi 600)")
    print("2. --format オプションで別の画像フォーマットを試す (例: --format jpeg)")
    print("3. Gemini Flash 2.0の制限や対応言語を確認する")

if __name__ == "__main__":
    main()
