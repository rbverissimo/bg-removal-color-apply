import os
import numpy as np
from PIL import Image

def process_logos_threshold():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(base_dir, "original_files")
    output_dir = os.path.join(base_dir, "output_files")
    
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
    
    if not files:
        print(f"No files found in: {input_dir}")
        return

    colors = {
        "EDECEB": (237, 236, 235), # Light Gray
        "C9CFD8": (201, 207, 216), # Steel Blue
        "transparent": None        # Will use original image colors
    }

    # -- THRESHOLD TUNING --
    # These values determine where the transparency starts and ends.
    DARK_TEXT_MAX = 120   # Pixels darker than this become 100% solid
    LIGHT_BG_MIN = 170    # Pixels lighter than this become 100% transparent

    for filename in files:
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue
            
        print(f"\nProcessing '{filename}'...")
        input_path = os.path.join(input_dir, filename)
        base_name = os.path.splitext(filename)[0]

        img_gray = Image.open(input_path).convert("L")
        img_np = np.array(img_gray, dtype=np.float32)

        alpha = (LIGHT_BG_MIN - img_np) / (LIGHT_BG_MIN - DARK_TEXT_MAX)
        
        alpha = np.clip(alpha, 0, 1)
        
        alpha_mask = (alpha * 255).astype(np.uint8)
        mask_img = Image.fromarray(alpha_mask, mode='L')
        
        original_img = Image.open(input_path).convert("RGBA")

        for hex_name, rgb in colors.items():
            if hex_name == "transparent":
                # Keep the original dark blue color, just swap the background for our new mask
                final_img = original_img.copy()
                final_img.putalpha(mask_img)
            else:
                # For EDECEB and C9CFD8, create a solid color block and stamp it using the mask
                solid_color_layer = Image.new("RGBA", original_img.size, (rgb[0], rgb[1], rgb[2], 255))
                final_img = Image.new("RGBA", original_img.size, (0, 0, 0, 0))
                final_img.paste(solid_color_layer, mask=mask_img)
            
            output_name = f"{base_name}_{hex_name}.png"
            output_path = os.path.join(output_dir, output_name)
            final_img.save(output_path, "PNG")
            print(f" -> Saved: {output_name}")

if __name__ == "__main__":
    process_logos_threshold()