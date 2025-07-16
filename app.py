import gradio as gr
from rembg import remove
from PIL import Image, ImageOps
import io
import os
import tempfile
import zipfile
import logging

# 日志设置
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_path = os.path.join(log_dir, "app.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_path, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# 中文颜色映射
bg_color_map = {
    "透明": "透明",
    "白色": "#ffffff",
    "黑色": "#000000",
    "浅灰": "#f0f0f0",
    "金色": "#ffcc00"
}

def process_and_package(files, size, bg_color_label):
    if not files:
        logging.warning("⚠️ 未上传任何文件")
        return [], "⚠️ 请先上传图标文件", [], None

    bg_color_hex = bg_color_map.get(bg_color_label, "透明")
    results = []
    file_paths = []
    log_output = ""
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "processed_icons.zip")

    with zipfile.ZipFile(zip_path, "w") as zipf:
        for idx, file in enumerate(files):
            try:
                # Step 1: 打开原图
                img = Image.open(file).convert("RGBA")

                # Step 2: 去背景
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                out_bytes = remove(buf.getvalue())
                out_img = Image.open(io.BytesIO(out_bytes)).convert("RGBA")

                # Step 3: 裁剪透明边框
                bbox = out_img.getbbox()
                if bbox:
                    out_img = out_img.crop(bbox)

                # Step 4: 等比例缩放图标到目标尺寸
                out_img.thumbnail((size, size), Image.LANCZOS)

                # Step 5: 居中填充到统一尺寸
                padded = Image.new("RGBA", (size, size), (0, 0, 0, 0))
                x = (size - out_img.width) // 2
                y = (size - out_img.height) // 2
                padded.paste(out_img, (x, y))

                # Step 6: 背景色合成（如果不是透明）
                if bg_color_hex != "透明":
                    bg = Image.new("RGBA", padded.size, bg_color_hex)
                    padded = Image.alpha_composite(bg, padded)

                # Step 7: 保存结果
                filename = f"icon_{idx+1:03}.png"
                file_path = os.path.join(temp_dir, filename)
                padded.save(file_path)

                results.append(padded)
                file_paths.append(file_path)
                zipf.write(file_path, arcname=filename)

                msg = f"✅ {filename} 处理完成（原始尺寸：{img.size} → 裁剪后：{out_img.size}）"
                log_output += msg + "\n"
                logging.info(msg)

            except Exception as e:
                err_msg = f"❌ 第 {idx+1} 张图标处理失败：{str(e)}"
                log_output += err_msg + "\n"
                logging.error(err_msg)

    logging.info(f"📦 ZIP 文件已生成：{zip_path}")
    return results, log_output.strip(), file_paths, zip_path

# 🍎 Apple 风格 + 自适应 CSS
custom_css = """
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', sans-serif;
    background: linear-gradient(135deg, #f8f9fa, #e9ecef);
    color: #1c1c1e;
    padding: 20px;
}

h1, h2, h3, .gr-markdown {
    text-align: center;
    color: #1c1c1e;
    font-weight: 600;
}

#process {
    background: linear-gradient(145deg, #ffffff, #e0e0e0);
    border: 1px solid #ccc;
    border-radius: 12px;
    padding: 12px 24px;
    font-size: 16px;
    font-weight: 600;
    color: #1c1c1e;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    transition: all 0.2s ease-in-out;
}
#process:hover {
    background: linear-gradient(145deg, #f0f0f0, #dcdcdc);
    transform: scale(1.02);
}

#logbox textarea {
    background: rgba(255, 255, 255, 0.6);
    backdrop-filter: blur(10px);
    border-radius: 12px;
    font-family: Menlo, Monaco, Consolas, monospace;
    font-size: 14px;
    color: #333;
    padding: 12px;
    border: 1px solid #ccc;
}

#gallery img {
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    transition: transform 0.2s ease;
}
#gallery img:hover {
    transform: scale(1.03);
}

@media (max-width: 768px) {
    #process {
        width: 100% !important;
        font-size: 18px !important;
    }

    #upload, #slider, #bgcolor {
        width: 100% !important;
    }

    #gallery img {
        width: 100% !important;
        max-width: 100% !important;
    }

    #logbox textarea {
        font-size: 16px !important;
        padding: 16px !important;
    }

    .gr-column {
        width: 100% !important;
        flex: 1 1 100% !important;
    }

    .gr-row {
        flex-direction: column !important;
    }
}
"""

with gr.Blocks(css=custom_css) as demo:
    gr.Markdown("## 🧼 图标去背景工具")

    with gr.Row():
        with gr.Column(scale=1):
            input_files = gr.File(file_types=["image"], file_count="multiple", label="上传图标", elem_id="upload")
            size_slider = gr.Slider(64, 512, value=256, step=32, label="统一输出尺寸", elem_id="slider")
            bg_color = gr.Radio(["透明", "白色", "黑色", "浅灰", "金色"], value="透明", label="背景颜色", elem_id="bgcolor")
            process_btn = gr.Button("🚀 开始批量处理", elem_id="process")
        with gr.Column(scale=2):
            output_gallery = gr.Gallery(label="图标预览", columns=4, height="auto", elem_id="gallery")

    with gr.Row():
        download_files = gr.Files(label="⬇️ 单个图标下载", elem_id="files")
        zip_file = gr.File(label="⬇️ 下载打包 ZIP", elem_id="zip")

    log_box = gr.Textbox(label="处理日志", lines=10, interactive=False, elem_id="logbox")

    process_btn.click(
        fn=process_and_package,
        inputs=[input_files, size_slider, bg_color],
        outputs=[output_gallery, log_box, download_files, zip_file]
    )

demo.launch(server_name="0.0.0.0", server_port=7860)
