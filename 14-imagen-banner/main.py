import base64
import io
import os
import textwrap
from typing import Literal, Optional

from fastapi import FastAPI, HTTPException, staticfiles
from fastapi.responses import JSONResponse, StreamingResponse
from google.cloud import aiplatform
from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel, validator
from vertexai.generative_models import (
    GenerativeModel,
    HarmBlockThreshold,
    HarmCategory,
)
from vertexai.preview.vision_models import ImageGenerationModel

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


# Google Cloud Project IDとVertex AIのリージョンを設定
PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION")

# Vertex AIの初期化
aiplatform.init(project=PROJECT_ID, location=REGION)

# Vertex AIのモデル名
MODEL_NAME = "gemini-2.0-flash-001"
IMAGEN_MODEL = "imagen-3.0-generate-002"
generation_model = GenerativeModel(
    model_name=MODEL_NAME,
    system_instruction="""
あなたは、卓越したコピーライティングスキルを持つプロのマーケターです。 
受信したリクエスト情報から、商品の魅力を最大限に引き出し、ターゲットに響く広告コピーを生成してください。

特に以下の点を重視してください。

* 簡潔性: 20字以内という制限の中で、商品の最も魅力的な側面を端的に表現してください。
* 訴求力: ターゲット層の興味を引く言葉選び、感情に訴えかける表現を心がけてください。
* 独自性: 他の広告コピーとの差別化を図り、対象の商品ならではの価値を強調してください。
* 正確性: 商品カテゴリや、ターゲット層などの情報を正しく反映してください。
* 行動喚起: 広告を見た人が「もっと詳しく知りたい」「購入したい」と思わせるような表現を検討してください。

広告コピーのトーン＆マナーは、指定された年齢や性別などに最適化してください。 
例えば、10代女性向けであればトレンドや若者言葉を、40代男性向けであれば信頼性や実績を重視するなど、ターゲット層に合わせた言葉遣いを心がけてください。

商品の具体的なメリットや使用シーンを連想させるように配置してください。 
例：「Google Pixel 9 Pro 特価で販売！」「Google の Pixel 9 Pro を手に入れるチャンス！」

生成された広告コピーは、バナー広告に掲載されることを考慮し、視覚的なインパクトも意識してください。
 
期待する出力形式は以下の通りです。

* 広告コピー: 20字以内の広告コピー
* 理由: 広告コピーの意図やポイント
""",
    safety_settings={
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    },
)

# Imagen API クライアントの初期化
image_generation_model = ImageGenerationModel.from_pretrained(IMAGEN_MODEL)


# Imagen API 利用のためのダミー関数 (実際の Imagen API の実装に置き換える)
def generate_image_with_imagen(
    prompt: str,
    negative_prompt: str,
    sampleImageSize: int,
    aspect_ratio: str,  # アスペクト比を指定できるように追加
    sampleCount: int,
    seed=None,
):
    try:
        generate_response = image_generation_model.generate_images(
            prompt=prompt,
            negative_prompt=negative_prompt,
            number_of_images=sampleCount,
            guidance_scale=float(sampleImageSize),
            aspect_ratio=aspect_ratio,  # アスペクト比を指定できるように追加
            # language="ja",  # 日本語でのプロンプトに対応するために追加
            seed=seed,
            # person_generation="allow_all",
            # safety_filter_level="block_fewest",
        )
        images = []
        for index, result in enumerate(generate_response):
            images.append(generate_response[index]._pil_image)
        return images, generate_response
    except Exception as e:
        print(f"Error generating image: {e}")  # エラーログを出力
        raise HTTPException(status_code=500, detail=f"Error generating image: {e}")


def generate_product_info_with_gemini(
    product_category: str, user_age: int, user_gender: str
) -> tuple[str, str]:
    prompt = f"""
        あなたはプロのコピーライターです。ユーザー属性と商品カテゴリから、最適な商品名と画像生成のためのプロンプトを提案してください。
        商品カテゴリ: {product_category}
        ターゲット層: 年齢{user_age}歳、性別{user_gender}
        出力は以下のようなJSON形式にしてください。product_name は日本語で、image_prompt は必ず英語で生成してください。JSON 情報以外は出力に含めないでください。
        {{
            "product_name": "提案する商品名",
            "image_prompt": "画像生成のためのプロンプト。なるべく詳細が分かる表現で生成してください。背景色は白以外にして、画像にテキストが含まれないことも明示して。商品カテゴリとターゲット層に基づいたキャッチーな画像も作成されるよう考慮して。"
        }}
    """
    print("商品名と画像生成プロンプト作成用プロンプト：", prompt)

    parameters = {
        "temperature": 0.5,
        "max_output_tokens": 300,
    }
    response = generation_model.generate_content(
        contents=[prompt],
        generation_config=parameters,
    )
    print("商品名と画像生成プロンプト作成用プロンプト結果：", response.text)

    try:
        response_json = response.text.strip().replace("```json", "").replace("```", "")
        response_dict = eval(response_json)
        product_name = response_dict["product_name"]
        image_prompt = response_dict["image_prompt"]
    except Exception as e:
        print(e)
        raise ValueError(f"Invalid response format: {response_json}")

    return product_name, image_prompt


def generate_banner_text_with_gemini(
    product_name: str, user_age: int, user_gender: str
) -> str:
    prompt = f"""
        あなたはプロのコピーライターです。小売業者の商品を訴求する広告コピーを考えてください。
        商品名: {product_name}
        ターゲット層: 年齢{user_age}歳、性別{user_gender}
        バナー広告に掲載するため、20字以内で魅力的な広告コピーを提案してください。絵文字は使わないで。
        出力形式はマークダウンではなくテキストで、理由や説明などの詳細は省いて、広告コピーのみを出力してください。
    """
    print("バナーテキスト作成プロンプト：", prompt)

    parameters = {
        "temperature": 0.5,
        "max_output_tokens": 100,
    }
    response = generation_model.generate_content(
        contents=[prompt],
        generation_config=parameters,
    )
    print("バナーテキスト作成結果：", response.text)

    return response.text.strip().replace("。", "")


def overlay_text_on_image(image: Image.Image, text: str) -> Image.Image:
    try:
        font_path = "NotoSansJP-Bold.ttf"
        font = ImageFont.truetype(font_path, size=48)
        draw = ImageDraw.Draw(image)
        wrapped_text = textwrap.fill(text, width=20)

        # Get text bounding box
        bbox = draw.textbbox((0, 100), wrapped_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Calculate text position
        x = (image.width - text_width) / 2
        y = (image.height - text_height) / 2

        # Draw text with white fill and bold effect (workaround)
        draw.text((x, y), wrapped_text, font=font, fill="white")

        return image
    except IOError as e:
        print(f"Error loading font: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading font: {e}")
    except Exception as e:
        print(f"Error overlaying text: {e}")
        raise HTTPException(status_code=500, detail=f"Error overlaying text: {e}")


app = FastAPI()


class BannerRequest(BaseModel):
    product_category: str
    user_age: int
    user_gender: str
    aspect_ratio: Literal["1:1", "9:16", "16:9", "4:3", "3:4"] = (
        "16:9"  # Default aspect ratio
    )
    output_format: Optional[Literal["png", "pdf"]] = "png"  # デフォルトはpng

    @validator("aspect_ratio")
    def validate_aspect_ratio(cls, v):
        allowed_ratios = ["1:1", "9:16", "16:9", "4:3", "3:4"]
        if v not in allowed_ratios:
            raise ValueError(f"Invalid aspect ratio. Must be one of: {allowed_ratios}")
        return v


@app.post("/generate_banner")
async def generate_banner(request: BannerRequest):
    # 1. Geminiによる商品名とプロンプトの生成
    try:
        product_name, image_prompt = generate_product_info_with_gemini(
            request.product_category, request.user_age, request.user_gender
        )
    except Exception as e:
        return JSONResponse(status_code=400, content={"detail": str(e)})

    # 2. 画像生成 (Imagen API)
    # generated_image = generate_image_with_imagen(image_prompt)
    images, generate_response = generate_image_with_imagen(
        prompt=image_prompt,
        negative_prompt=None,
        sampleImageSize="1536",
        aspect_ratio=request.aspect_ratio,
        sampleCount=1,
        seed=None,
    )
    if not images:
        raise HTTPException(status_code=500, detail="Image generation failed")
    generated_image = images[0]  # 最初の画像を取得

    # 3. テキスト生成 (Gemini API)
    banner_text = generate_banner_text_with_gemini(
        product_name, request.user_age, request.user_gender
    )

    # 4. 画像とテキストの合成 (Pillow)
    output_image = overlay_text_on_image(generated_image, banner_text)

    # 5. 画像を保存 (またはメモリ上で扱う)
    image_bytes = io.BytesIO()
    output_image.save(image_bytes, format="PNG")
    image_bytes.seek(0)

    # 6. 画像とテキストをJSONで返す
    if request.output_format == "png":
        # 6a. PNGとしてJSONで返す
        return JSONResponse(
            content={
                "output_format": "png",  # output_formatをレスポンスに含める
                "banner_text": banner_text,
                "image_bytes": base64.b64encode(image_bytes.getvalue()).decode("utf-8"),
            }
        )
    elif request.output_format == "pdf":
        try:
            # 6b. PDFとして返す
            pdf_buffer = io.BytesIO()
            c = canvas.Canvas(pdf_buffer, pagesize=letter)
            width, height = letter

            # Metadata
            c.setAuthor("Gemini")  # 作者
            c.setTitle(banner_text)  # 表題
            c.setSubject("generated-banner")  # 件名

            # Draw the image

            # 画像をPDFに描画
            c.drawImage(
                ImageReader(image_bytes),
                0,
                0,
                width=width,
                height=height,
                preserveAspectRatio=True,
                mask="auto",
            )  # PDFに合わせて画像をリサイズ

            c.save()
            pdf_buffer.seek(0)

            return StreamingResponse(
                pdf_buffer,
                media_type="application/pdf",
                headers={"Content-Disposition": "attachment;filename=banner.pdf"},
            )
        except Exception as e:
            print(f"Error generating PDF: {e}")
            raise HTTPException(
                status_code=500,
                detail=e,
            )
    else:
        raise HTTPException(
            status_code=400, detail="Invalid output format.  Must be 'png' or 'pdf'."
        )


app.mount("/", staticfiles.StaticFiles(directory="static", html=True), name="static")
