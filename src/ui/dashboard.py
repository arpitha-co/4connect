# connect4_vision_robot/ui/dashboard.py
import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

try:
    from PIL import Image, ImageTk
    _HAS_PIL = True
except Exception:
    Image = None
    ImageTk = None
    _HAS_PIL = False


def _find_background_image():
    """Look for a background image in the same folder as this file."""
    base = os.path.dirname(__file__)
    candidates = [
        os.path.join(base, 'background.jpg'),
        os.path.join(base, 'background.png'),
        os.path.join(base, 'connect4.jpg'),
        os.path.join(base, 'connect4.png'),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    # fallback: look for any jpg/png in folder
    for fn in os.listdir(base):
        if fn.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            return os.path.join(base, fn)
    return None


def show_dashboard():
    result = {}

    root = tk.Tk()
    root.title('Connect4 - Settings')
    # Fullscreen window
    try:
        root.attributes('-fullscreen', True)
    except Exception:
        root.state('zoomed')

    # Exit fullscreen on Escape
    root.bind('<Escape>', lambda e: root.destroy())

    # Canvas for background image
    canvas = tk.Canvas(root, highlightthickness=0)
    canvas.pack(fill='both', expand=True)

    bg_path = _find_background_image()
    bg_img_tk = None
    if bg_path and _HAS_PIL:
        try:
            img = Image.open(bg_path)
            # resize to screen
            sw = root.winfo_screenwidth()
            sh = root.winfo_screenheight()
            img = img.resize((sw, sh), Image.LANCZOS)
            bg_img_tk = ImageTk.PhotoImage(img)
            canvas.create_image(0, 0, image=bg_img_tk, anchor='nw')
        except Exception:
            bg_img_tk = None
    elif bg_path:
        try:
            bg_img_tk = tk.PhotoImage(file=bg_path)
            canvas.create_image(0, 0, image=bg_img_tk, anchor='nw')
        except Exception:
            bg_img_tk = None

    # Centered frame for controls (semi-opaque feel by using background color)
    ctrl_frame = ttk.Frame(root, padding=24, style='Card.TFrame')
    # Place as canvas window centered
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    ctrl_window = canvas.create_window(sw//2, sh//2, window=ctrl_frame)

    # Large fonts
    header_font = ('Helvetica', 24, 'bold')
    label_font = ('Helvetica', 14)

    ttk.Style().configure('Card.TFrame', background='#ffffff', relief='raised')

    ttk.Label(ctrl_frame, text='Connect 4 - Game Settings', font=header_font).grid(row=0, column=0, columnspan=2, pady=(0,12))

    # Player name
    ttk.Label(ctrl_frame, text='Player name:', font=label_font).grid(row=1, column=0, sticky='e', padx=(0,10), pady=6)
    name_var = tk.StringVar(value='Human')
    ttk.Entry(ctrl_frame, textvariable=name_var, width=24).grid(row=1, column=1, sticky='w')

    # Player color
    ttk.Label(ctrl_frame, text='Player color:', font=label_font).grid(row=2, column=0, sticky='e', padx=(0,10), pady=6)
    color_var = tk.StringVar(value='Yellow')
    color_menu = ttk.Combobox(ctrl_frame, textvariable=color_var, values=['Yellow', 'Red'], state='readonly', width=22)
    color_menu.grid(row=2, column=1, sticky='w')

    # Difficulty
    ttk.Label(ctrl_frame, text='Difficulty:', font=label_font).grid(row=3, column=0, sticky='e', padx=(0,10), pady=6)
    diff_var = tk.StringVar(value='Medium')
    diff_menu = ttk.Combobox(ctrl_frame, textvariable=diff_var, values=['Easy', 'Medium', 'Hard'], state='readonly', width=22)
    diff_menu.grid(row=3, column=1, sticky='w')

    # Who starts
    ttk.Label(ctrl_frame, text='Who starts:', font=label_font).grid(row=4, column=0, sticky='e', padx=(0,10), pady=6)
    start_var = tk.StringVar(value='Human')
    start_menu = ttk.Combobox(ctrl_frame, textvariable=start_var, values=['Human', 'Robot'], state='readonly', width=22)
    start_menu.grid(row=4, column=1, sticky='w')

    # Optional: choose different background
    def choose_bg():
        p = filedialog.askopenfilename(title='Choose background image', filetypes=[('Images','*.png;*.jpg;*.jpeg;*.gif')])
        nonlocal bg_img_tk
        if p:
            try:
                if _HAS_PIL:
                    img = Image.open(p)
                    img = img.resize((root.winfo_screenwidth(), root.winfo_screenheight()), Image.LANCZOS)
                    bg_img_tk = ImageTk.PhotoImage(img)
                else:
                    bg_img_tk = tk.PhotoImage(file=p)
                canvas.create_image(0, 0, image=bg_img_tk, anchor='nw')
            except Exception:
                pass

    ttk.Button(ctrl_frame, text='Change background', command=choose_bg).grid(row=5, column=0, columnspan=2, pady=(12,6))

    # Buttons
    def on_ok():
        result['player_name'] = name_var.get().strip() or 'Human'
        result['player_color'] = color_var.get()
        result['difficulty'] = diff_var.get()
        result['who_starts'] = start_var.get()
        root.destroy()

    def on_cancel():
        result['cancelled'] = True
        root.destroy()

    btn_frame = ttk.Frame(ctrl_frame)
    btn_frame.grid(row=6, column=0, columnspan=2, pady=(10,0))
    ttk.Button(btn_frame, text='OK', command=on_ok).grid(row=0, column=0, padx=8)
    ttk.Button(btn_frame, text='Cancel', command=on_cancel).grid(row=0, column=1, padx=8)

    root.mainloop()
    return result