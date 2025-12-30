import tkinter as tk
import requests
import threading
import os, sys
import ctypes
import webbrowser
from PIL import Image, ImageTk
import customtkinter as ctk
from dotenv import load_dotenv
import re

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

myappid = "DajDon.Picasso.1"
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

def _try_load(path):
    try:
        if os.path.exists(path):
            load_dotenv(path, override=True)
            return True
    except Exception:
        pass
    return False

def load_api_key():
    if os.getenv("GROQ_API_KEY"):
        return os.getenv("GROQ_API_KEY")

    candidates = ("api_key.env", ".env", "api_key.txt")
    base_dirs = [os.getcwd(), os.path.dirname(__file__)]
    if getattr(sys, "_MEIPASS", None):
        base_dirs.insert(0, sys._MEIPASS)
    exe_dir = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else None
    if exe_dir and exe_dir not in base_dirs:
        base_dirs.append(exe_dir)

    for b in base_dirs:
        for c in candidates:
            p = os.path.join(b, c)
            if _try_load(p):
                val = os.getenv("GROQ_API_KEY")
                if val:
                    return val
            try:
                if os.path.exists(p):
                    with open(p, "r", encoding="utf-8") as f:
                        text = f.read().strip()
                        m = re.search(r'GROQ_API_KEY\s*=\s*["\']?(.+?)["\']?\\s*$', text, re.M)
                        if m:
                            return m.group(1).strip()
                        if text and "\n" not in text and len(text) > 10:
                            return text
            except Exception:
                pass

    return None

API_KEY = load_api_key()
API_URL = "https://api.groq.com/openai/v1/chat/completions"

root = tk.Tk()
root.title("Picasso AI")
root.geometry("600x500")
root.config(bg="#0a0e27")
root.resizable(False, False)

try:
    root.update()
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    set_window_attribute = ctypes.windll.dwmapi.DwmSetWindowAttribute
    hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
    rendering_policy = ctypes.c_int(2)
    set_window_attribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(rendering_policy), ctypes.sizeof(rendering_policy))
except:
    pass

versionnum = tk.Label(root, text="v1.0", fg="white", bg="#0a0e27", font=("Arial, 12"))
versionnum.place(x=550, y=470)

icon = tk.PhotoImage(file=resource_path("assets\\picasso.png"))
root.iconphoto(True, icon)

downimg = Image.open(resource_path("assets\\picassodown.png"))
downimg = downimg.resize((200, 200))
downimg = ImageTk.PhotoImage(downimg)
image_label = tk.Label(root, image=downimg, bg="#0a0e27")
image_label.place(x=185, y=360)

send_img = Image.open(resource_path("assets/send.png"))
send_img = send_img.resize((130, 90)) 
send_img = ImageTk.PhotoImage(send_img)

infimg = Image.open(resource_path("assets/info.png"))
infimg = infimg.resize((30, 30)) 
infimg = ImageTk.PhotoImage(infimg)

chat = [
    {"role": "system", "content": "Te egy hasznos AI asszisztens vagy, akit Picasso-nak hívnak. Segítőkész vagy és természetes módon válaszolsz a kérdésekre. Csak akkor említsd a nevedet, ha konkrétan megkérdezik. FONTOS: Mindig ugyanazon a nyelven válaszolj, amilyen nyelven a felhasználó kérdez. Ha magyarul kérdeznek, magyarul válaszolj. Ha angolul kérdeznek, angolul válaszolj, és így tovább."}
]

chatwin = ctk.CTkTextbox(
    root,
    width=560,
    height=320,
    fg_color="#1e1b4b",
    text_color="white",
    corner_radius=12,
    border_color="white",
    border_width=2,
    state="disabled"
)
chatwin.place(x=20, y=20)

def on_mouse_wheel(event):
    chatwin.yview_scroll(int(-1*(event.delta/120)), "units")
chatwin.bind("<MouseWheel>", on_mouse_wheel)

def add_message(msg, sender="Picasso"):
    chatwin.configure(state="normal")
    chatwin.insert("end", f"{sender}: {msg}\n\n")
    chatwin.configure(state="disabled")
    chatwin.see("end")

msgbox = ctk.CTkEntry(
    root,
    fg_color="#1e1b4b",
    text_color="white",
    border_color="white",
    width=430,
    height=27,
    placeholder_text="How Is Your Day?"
)
msgbox.place(x=50, y=380)

def api(short_response=False):
    try:
        if not API_KEY:
            add_message("Error: Missing API key. Set the api key in the .env file", sender="Error")
            return

        messages = chat.copy()
        if short_response:
            messages.append({"role": "system", "content": "Adj rövid, tömör választ (maximum 1 mondat)."})
        
        r = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={"model": "llama-3.3-70b-versatile", "messages": messages},
            timeout=30
        )

        if r.status_code != 200:
            add_message(f"Error: API hiba ({r.status_code}): {r.text}", sender="Error")
            return

        ai = r.json()["choices"][0]["message"]["content"]
        chat.append({"role": "assistant", "content": ai})
        add_message(ai, sender="Picasso")
    except Exception as e:
        add_message(f"Error: {e}", sender="Error")

def send(short_response=False):
    msg = msgbox.get()
    if not msg:
        return
    add_message(msg, sender="You")
    msgbox.delete(0, tk.END)
    chat.append({"role": "user", "content": msg})
    threading.Thread(target=lambda: api(short_response), daemon=True).start()

def on_enter(event):
    send(short_response=False)
    return "break"

def on_ctrl_enter(event):
    send(short_response=True)
    return "break"

def info_open():
    webbrowser.open("https://dajdon.hu/picasso")

asks = tk.Label(root, text="Ask Something", font=("Segoe UI", 12, "bold"), fg="white", bg="#0a0e27", anchor="center", justify="center")
asks.place(x=225, y=350) 

send_button = ctk.CTkButton(
    root,
    text="Send",
    width=51,
    height=28,
    fg_color="#1e1b4b",
    text_color="white",
    corner_radius=8,
    hover_color="#262255",
    border_color="white",
    border_width=2,
    command=lambda: send(short_response=False)
)
send_button.place(x=497, y=380)

if not API_KEY:
    send_button.configure(state="disabled")

info = tk.Button(root, image=infimg, command=info_open, bg="#0a0e27", bd=0, highlightthickness=0, activebackground="#0a0e27")
info.place(x=15, y=465)  

msgbox.bind("<Return>", on_enter)
msgbox.bind("<Control-Return>", on_ctrl_enter)

root.mainloop()