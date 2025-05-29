# STORES THE CURRENT STATE OF THE WATERMARK
# USEFUL TO UPDATE GUI DYNAMICALLY
from image_tools import *
import customtkinter as ctk
from PIL import Image
import pprint

class WatermarkState():
  def __init__(self) -> None:
    self.text = "Sample"
    self.opacity = 128 # 0-255 opacity in rgb - 128 is 50%
    self.font_path = str = None #Font path eg: arial.ttf
    self.font_size = 72 # 12-150 size in px
    self.position = tuple = None # (x, y) pixel coordinates to place text
    self.text_anchor = "ms"
    self.current_image: Image #PIL IMAGE
    self.edited_image: Image  #PIL IMAGE
    self.ctk_image: ctk.CTkImage  #CTKIMAGE VERSION OF CURRENT IMAGE

  def show_preview(self, preview_label:ctk.CTkLabel):
    """Updates ctk label widget to show the image being edited currently."""
    try:
      dimentions = get_new_size(self.edited_image)
      self.ctk_image = ctk.CTkImage(self.edited_image, size=dimentions)
      preview_label.configure(image=self.ctk_image, text="")
    
    except Exception as e:
      print(f"show preview: {e}")
 
  def apply_watermark(self):
    """Updates edited_image and ctk_image. Uses ctk image to display in GUI."""
    try:
      final_image = generate_watermark(self)
      
      if final_image:
        self.edited_image = final_image
        dimentions = get_new_size(self.edited_image)
        self.ctk_image = ctk.CTkImage(self.edited_image, size=dimentions)
    
    except Exception as e:
      print(f"apply watermark error: {e}")

  def update_state(self, **kwargs):
    pass
  
  def reset(self):
    pass




