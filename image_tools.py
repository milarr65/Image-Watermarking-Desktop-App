import os
import math
import pprint
import json
import glob
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from collections import defaultdict


FONT_DIRS = [
    "/usr/share/fonts",            # Linux
    "/Library/Fonts",              # macOS
    "~/Library/Fonts",             # macOS (user)
    "C:\\Windows\\Fonts"           # Windows
]

def weight_name(weight):
    weight = int(weight)
    if weight <= 250:
        return "light"
    elif weight <= 350:
        return "regular"
    elif weight <= 450:
        return "medium"
    elif weight <= 650:
        return "bold"
    else:
        return "black"

def is_italic(font):
    try:
        # OS/2 table: bit 0 of fsSelection set = italic
        if font["OS/2"].fsSelection & 0x01:
            return True
        # macStyle: bit 1 = italic
        if font["head"].macStyle & 0x02:
            return True
    except Exception:
        pass

    # Fallback: check name
    try:
        name = font["name"].getName(2, 3, 1, 1033)
        if name and "italic" in str(name).lower():
            return True
    except Exception:
        pass

    return False

def get_system_fonts_json(save_path="system_fonts.json"):
    system_fonts = defaultdict(dict)
    font_files = []

    for directory in FONT_DIRS:
        expanded = os.path.expanduser(directory)
        font_files.extend(glob.glob(f"{expanded}/**/*.ttf", recursive=True))
        font_files.extend(glob.glob(f"{expanded}/**/*.otf", recursive=True))

    for font_path in font_files:
        try:
            font = TTFont(font_path, lazy=True)
            name_table = font["name"]
            os2_table = font["OS/2"]

            family = name_table.getName(1, 3, 1, 1033) or name_table.getName(1, 1, 0, 0)
            family = str(family) if family else None

            weight_class = os2_table.usWeightClass
            weight = weight_name(weight_class)
            italic = is_italic(font)

            if family:
                key = f"{weight}-italic" if italic else weight
                system_fonts[family][key] = font_path

        except Exception as e:
            continue  # Skip unreadable/broken fonts
    
    sorted_fonts = dict(sorted(system_fonts.items()))
    # Save to JSON (this is for debbuging)
    # with open(save_path, "w", encoding="utf-8") as f:
    #     json.dump(sorted_fonts, f, indent=2, ensure_ascii=False)

    # print(f"✅ Font data saved to {save_path}")
    return dict(sorted_fonts)

def save_image(image:Image.Image):
    """Saves image with watermark. Returns None."""
    try:
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")

        file_path = filedialog.asksaveasfilename(
            initialdir=downloads_path,
            defaultextension=".png",  # or .jpg, etc.
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")],
            title="Save watermarked image as..."
        )
        if not file_path:
            print("Save canceled")
            return
        
        # Convert to RGB if needed for JPG
        if file_path.lower().endswith(".jpg") or file_path.lower().endswith(".jpeg"):
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")
        
        image.save(rf"{file_path}")
        print(f"Imaged saved to: {file_path}")
    
    except Exception as e:
        print(f"Error saving image: {e}")

def create_text_layer(state):
    """Uses PIL to make a transparent base and places text on it. Also handles text's opacity"""

    # Create transparent background to place text over it
    text_layer = Image.new("RGBA", state.edited_image.size, (255, 255, 255, 0))
    
    # Parameters to use
    draw = ImageDraw.Draw(text_layer)
    font = ImageFont.truetype(font=state.font_path, 
                              size=state.font_size)
    rgba_color = (255, 255, 255, state.opacity)

    # Place text in the desired position
    draw.text(state.position, text=state.text, fill=rgba_color, font=font, anchor=state.text_anchor)

    return text_layer

def apply_text_layer(base_image, text_layer):
    """Places text over user's image."""

    # Both have to be RGBA
    base_rgba = base_image.convert("RGBA")
    return Image.alpha_composite(base_rgba, text_layer)

def generate_watermark(state):
    """Calls previous functions to generate the final version of user's image with watermark. Returns a PIL Image object."""

    try:
        img = state.current_image
        #resized_img = img.resize(size=get_new_size(img), resample=Image.Resampling.LANCZOS)
        text_layer = create_text_layer(state)  
        final_img = apply_text_layer(img, text_layer) 
        
        return final_img
    
    except Exception as e:
        print(f"generate watermark Error: {e}")
        return None

def get_new_size(img): 
    """Calculates a reduced size in px of user's image to be able to fit it inside the image preview widget in the gui. Returns a tuple(width, height) """
    
    try:
        default_width = 450
        default_height = 470
        if img.width > img.height: # Horizontal img
            percent_taken = default_width * 100 / img.width
            auto_height = percent_taken * img.height / 100
            
            final_h = int(math.ceil(auto_height))
            final_w = int(default_width)

            return (final_w, final_h)
            
        elif img.width < img.height: # Vertical img
            percent_taken = default_height * 100 / img.height
            auto_width = percent_taken * img.width / 100

            final_h = int(default_height)
            final_w = int(math.ceil(auto_width))

            return (final_w, final_h)
        
        elif img.width == img.height: # Square img
            percent_taken = default_width * 100 / img.width
            auto_height = percent_taken * img.height / 100
            
            final_h = int(math.ceil(auto_height))
            final_w = final_h

            return (final_w, final_h)


    except Exception as e:
        print(f"get_new_size Error: {e}")
    
def calc_position(user_choice:str, state):
    """Calculates the available text positions based on the dimensions of the image and maps the user's choice to the corresponding pixel coordinates. Returns a tuple (x, y) representing the position in pixels."""
    
    percent = 10
    w = state.edited_image.width 
    h = state.edited_image.height 

    #img size after 10% reduction
    new_w = w - (percent * w / 100) 
    new_h = h - (percent * h / 100) 

    #Pixel equivalent of percent
    w_pixels_taken = w - new_w 
    h_pixels_taken = h - new_h 

    #margins and center coords
    left_m = w_pixels_taken / 2
    right_m = w - left_m 
    x_center = left_m + new_w / 2 

    top_m = h_pixels_taken / 2
    bottom_m = h - top_m 
    y_center = top_m + new_h / 2 
    
    coords = () 

    match user_choice:
        case "top left":
            coords = (left_m, top_m)
        case "top":
            coords = (x_center, top_m)
        case "top right":
            coords = (right_m, top_m)
        case "left":
            coords = (left_m, y_center)
        case "center":
            coords = (x_center, y_center)
        case "right":
            coords = (right_m, y_center)
        case "bottom left":
            coords = (left_m, bottom_m) 
        case "bottom":
            coords = (x_center, bottom_m)
        case "bottom right":
            coords = (right_m, bottom_m)
        case _:
            return "Invalid input"
    
    return coords
