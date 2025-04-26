import customtkinter as ctk
from frames import Frames
from watermark_state import WatermarkState

class WatermarkApp:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        
        self.root = ctk.CTk()
        self.root.title("Watermark App")
        self.root.geometry("1000x600")
        self.root.minsize(720, 500)
        self.root.resizable(False, False)
        self.state = WatermarkState()
        
        self.setup_ui()

    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True)

        self.frames = Frames(master=self.main_frame,
                            state=self.state)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = WatermarkApp()
    app.run()
