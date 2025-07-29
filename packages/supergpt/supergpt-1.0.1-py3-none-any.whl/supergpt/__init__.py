import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from google import genai

# 🔐 Tạo client Gemini
client = genai.Client(api_key="AIzaSyDsymWos5JIG7Ial7MlWc1-67DBz4Paubw")  # ← Thay bằng key thật

# 🧠 Hàm gửi câu hỏi tới AI
def send_message(event=None):
    prompt = input_box.get().strip()
    if not prompt:
        return
    add_message("Bạn 👦", prompt, align="right")
    input_box.delete(0, tk.END)
    try:
        add_message("Gemini 🤖", "Đang suy nghĩ...", align="left", temp_tag="pending")
        root.after(100, lambda: get_ai_response(prompt))
    except Exception as e:
        update_pending(f"Lỗi: {str(e)}")

# 🔁 Lấy phản hồi từ AI
def get_ai_response(prompt):
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        update_pending(response.text.strip())
    except Exception as e:
        update_pending(f"Lỗi: {str(e)}")

# 🧱 Hàm thêm tin nhắn vào cửa sổ chat
def add_message(sender, message, align="left", temp_tag=None):
    chat_box.config(state=tk.NORMAL)
    if align == "right":
        chat_box.insert(tk.END, f"{sender}:\n", "user_tag")
        chat_box.insert(tk.END, f"{message}\n\n", "user_msg")
    else:
        if temp_tag:
            chat_box.insert(tk.END, f"{sender}:\n", "ai_tag")
            tag_start = chat_box.index(tk.END)
            chat_box.insert(tk.END, f"{message}\n\n", temp_tag)
            tag_indices[temp_tag] = tag_start
        else:
            chat_box.insert(tk.END, f"{sender}:\n", "ai_tag")
            chat_box.insert(tk.END, f"{message}\n\n", "ai_msg")
    chat_box.config(state=tk.DISABLED)
    chat_box.yview(tk.END)

# 🔧 Cập nhật tin nhắn đang chờ
def update_pending(new_text):
    chat_box.config(state=tk.NORMAL)
    tag = "pending"
    if tag in tag_indices:
        start = tag_indices[tag]
        end = f"{start} lineend +1c"
        chat_box.delete(start, end)
        chat_box.insert(start, f"{new_text}\n\n", "ai_msg")
        del tag_indices[tag]
    chat_box.config(state=tk.DISABLED)
    chat_box.yview(tk.END)

# 🪟 Giao diện chính
root = tk.Tk()
root.title("LâmBot 🤖 Gemini Chat")
root.geometry("600x600")
root.config(bg="#ffffff")

# 💬 Khung chat cuộn
chat_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Segoe UI", 11), bg="#f9f9f9", state=tk.DISABLED)
chat_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# 🧠 Style
chat_box.tag_config("user_tag", foreground="#2b2b2b", font=("Segoe UI", 10, "bold"), justify="right")
chat_box.tag_config("user_msg", background="#dcf8c6", foreground="black", font=("Segoe UI", 11), justify="right", lmargin1=50, rmargin=10)
chat_box.tag_config("ai_tag", foreground="#007bff", font=("Segoe UI", 10, "bold"))
chat_box.tag_config("ai_msg", background="#eef1f5", font=("Segoe UI", 11), lmargin1=10, rmargin=50)
chat_box.tag_config("pending", background="#ffffff", foreground="gray", font=("Segoe UI", 11, "italic"))

tag_indices = {}

# 🔽 Ô nhập + nút gửi
input_frame = tk.Frame(root, bg="#ffffff")
input_frame.pack(fill=tk.X, padx=10, pady=5)

input_box = tk.Entry(input_frame, font=("Segoe UI", 12))
input_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
input_box.bind("<Return>", send_message)

send_btn = tk.Button(input_frame, text="🧠 Gửi", font=("Segoe UI", 11), bg="#4caf50", fg="white", command=send_message)
send_btn.pack(side=tk.RIGHT)

root.mainloop()