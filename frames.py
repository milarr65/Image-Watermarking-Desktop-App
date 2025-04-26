from textwrap import fill
import customtkinter as ctk
from image_tools import *
import pprint

class Frames(ctk.CTkFrame):
    def __init__(self, master, state, **kwargs):
        super().__init__(master, **kwargs)
        self.state = state # watermark state instance
        self.fonts = get_system_fonts_json()
        

        # //////////// LEFT FRAME-OPTIONS MENU /////////////////
        self.left_frame = ctk.CTkFrame(master, width=334)
        self.left_frame.pack(side="left", fill="y", padx=20, pady=20)
        self.left_frame.pack_propagate(False)

        #-------------- Text input ---------------
        title = ctk.CTkLabel(self.left_frame, text="Your text", font=ctk.CTkFont(size=16))
        text_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.input_text = ctk.CTkEntry(text_frame, 
                                      placeholder_text="Type here...")
        accept_button = ctk.CTkButton(text_frame,
                                      text="Accept",
                                      command=self.handle_accept,
                                      width=100)
        
        title.pack(pady=(20, 5), fill="x")
        text_frame.pack(padx=10, pady=(0, 20), fill="x")
        self.input_text.pack(side="left", fill="x", expand=True)
        accept_button.pack(side="right")

        #------------------- Opacity input ----------------------
        self.opacity_label = ctk.CTkLabel(self.left_frame, text="Opacity", font=ctk.CTkFont(size=16))
        self.opacity_slider = ctk.CTkSlider(self.left_frame, 
                                            from_=10, to=255,
                                            number_of_steps=245, 
                                            command=self.handle_opacity)

        self.opacity_label.pack(pady=(0, 10), fill="x", padx=10)
        self.opacity_slider.pack(pady=(0, 20), fill="x", padx=10)
        self.opacity_slider.set(self.state.opacity)

        #---------------------- Font chooser --------------------------------
        font_names = [font for font in self.fonts.keys()]

        self.font_label = ctk.CTkLabel(self.left_frame, text="Font & Weight", font=ctk.CTkFont(size=16))
        self.font_label.pack(padx=10, fill="x", pady=20)
        
        font_menus_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        font_menus_frame.pack(padx=10, pady=(0, 25), fill="x")

        self.font_menu = ctk.CTkComboBox(font_menus_frame,
                                        values=font_names, 
                                        command=self.handle_font,
                                        state="readonly")
        self.font_menu.set("")
        
        # current_font = self.font_menu.get()
        # self.weights_list = list(self.fonts[current_font].keys())

        self.weight_menu = ctk.CTkComboBox(font_menus_frame,
                                        # values=self.weights_list, 
                                        command=self.handle_fontWeight,
                                        state="readonly")
        self.weight_menu.set("")
        
       
        self.font_menu.pack(side="left", fill="x", expand=True)
        self.weight_menu.pack(side="right", fill="x")

        #---------------------- Font Size ----------------------------------
        self.size_label = ctk.CTkLabel(self.left_frame, 
                                  text="Text Size", 
                                  font=ctk.CTkFont(size=16))
        self.size_slider = ctk.CTkSlider(self.left_frame, 
                                         from_=12, to=150, 
                                         number_of_steps=138, 
                                         command=self.handle_font_size)
        
        self.size_label.pack(padx=10, fill="x", pady=(0, 10))
        self.size_slider.pack(padx=10, fill="x", pady=(0, 20))
        self.size_slider.set(self.state.font_size)

        #-------------------- Text Position -------------------------------------
        pos_label = ctk.CTkLabel(self.left_frame, 
                                 text="Positon", 
                                 font=ctk.CTkFont(size=16))
        self.pos_menu = ctk.CTkOptionMenu(self.left_frame, 
                                          values=["Top", "Center", "Bottom", "Left", "Right", "Top Left", "Top Right", "Bottom left", "Bottom right"], 
                                          command=self.handle_position)

        pos_label.pack(pady=(0, 10), fill="x", padx=10)
        self.pos_menu.pack(pady=(0, 20), fill="x", padx=10)


        # //////////// RIGHT FRAME-IMAGE PREVIEW /////////////////

        self.preview_frame = ctk.CTkFrame(master)
        self.preview_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        #------------------ Image Preview --------------------------
        self.preview_label = ctk.CTkLabel(self.preview_frame, text="No image uploaded", anchor="center")
        self.preview_label.pack(expand=True)

        buttons_frame = ctk.CTkFrame(self.preview_frame, fg_color="transparent")
        buttons_frame.pack(padx=10, pady=(0, 10), fill="x")

        #--------------------- Save as button ----------------------- 
        self.save_button = ctk.CTkButton(buttons_frame, 
                                         text="Save as", 
                                         command=self.save_current_img)
        self.save_button.pack(side="right", expand=True)

        #---------------------- Upload button -------------------------
        self.upload_button = ctk.CTkButton(buttons_frame, text="Upload Image", command=self.upload_file)
        self.upload_button.pack(side="left", expand=True)


# //////////// FUNCTIONS /////////////////
    
    def upload_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")]
        )
        
        if file_path:
            with Image.open(file_path) as img:
                self.state.current_image = img.copy()
                self.state.edited_image = img.copy()

        self.state.position = calc_position("center", self.state)
        self.state.font_path = self.fonts["Arial"]["medium"]

        # UPDATE MENUS
        self.font_menu.set("Arial")
        self.weights_list = [weight for weight in self.fonts["Arial"].keys()]
        self.weight_menu.configure(values=self.weights_list)
        self.weight_menu.set(self.weights_list[0])
        self.pos_menu.set("Center")
        self.size_label.configure(text=f"Text Size: {self.state.font_size}")

        self.state.apply_watermark() 
        self.state.show_preview(self.preview_label)

    def handle_accept(self):
        text = self.input_text.get()
        self.state.text = text
        
        self.state.apply_watermark()
        self.state.show_preview(self.preview_label)    

    def handle_opacity(self, value):
        opacity = value #get opacity from ctk widget
        if type(opacity) == float:
            opacity = math.floor(opacity) #make it int if it's a float

        self.state.opacity = opacity # Update state

        self.state.apply_watermark() #generate new image and update state
        self.state.show_preview(self.preview_label) # re-render image preview

    def handle_font(self, value):
        font = value # get font name as str
        
        self.weights_list = list(self.fonts[font].keys()) #list[str] of font's weights
        weight = self.weights_list[0] #default to first weight of the font
        
        # UPDATE MENUS
        self.weight_menu.configure(values=self.weights_list) 
        self.weight_menu.set(weight)

        try:
            self.state.font_path = self.fonts[font][weight]
            # print(F"FONT WEIGHTS: {self.weights_list}")
        
        except Exception as e:
            print(f"Error fetching font weight: {e}")

        self.state.apply_watermark()
        self.state.show_preview(self.preview_label) 

    def handle_fontWeight(self, value):
        self.state.font_path = self.fonts[self.font_menu.get()][value]

        self.state.apply_watermark()
        self.state.show_preview(self.preview_label)
    
    def handle_font_size(self, value):
        font_size = value
        if type(font_size) == float:
            font_size = math.floor(font_size) # Convert to int

        self.state.font_size = font_size # Update state
        self.size_label.configure(text=f"Text Size: {self.state.font_size}")

        self.state.apply_watermark() #generate new image and update state
        self.state.show_preview(self.preview_label) # re-render image preview    
        
    def handle_position(self, value):
        position = value.lower()
        coords = calc_position(position, self.state)
        anchors = {"top left": "lt", "left":"lm", "bottom left": "ls",
                   "top": "mt", "center": "mm", "bottom": "ms",
                   "top right": "rt", "right": "rm", "bottom right": "rs"}
        self.state.position = coords
        self.state.text_anchor = anchors[position]

        self.state.apply_watermark() #generate new image and update state
        self.state.show_preview(self.preview_label) # re-render image preview  

    def save_current_img(self):
        try:
            save_image(self.state.edited_image)
        except Exception as e:
            print(f"Failed to save image: {e}")