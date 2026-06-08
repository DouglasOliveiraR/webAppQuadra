from PIL import Image
import os

source_path = r"e:\APP_FUT_V2\frontend\public\assets\logo_peladafc.png"
public_dir = r"e:\APP_FUT_V2\frontend\public"

if os.path.exists(source_path):
    img = Image.open(source_path)
    # Ensure it's RGBA
    img = img.convert("RGBA")
    
    # 192x192
    img_192 = img.resize((192, 192), Image.Resampling.LANCZOS)
    img_192.save(os.path.join(public_dir, "pwa-192x192.png"), format="PNG")
    
    # 512x512
    img_512 = img.resize((512, 512), Image.Resampling.LANCZOS)
    img_512.save(os.path.join(public_dir, "pwa-512x512.png"), format="PNG")
    print("Ícones do PWA gerados com sucesso!")
else:
    print(f"Erro: {source_path} não encontrado.")
