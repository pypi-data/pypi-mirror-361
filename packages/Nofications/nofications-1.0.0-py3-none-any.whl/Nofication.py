
try:
    import tkinter as tk
except ImportError:
    raise RuntimeError("Tkinter is required but not available. Please install the Tk GUI libraries.")

try:
    import threading
except ImportError:
    raise RuntimeError("Threading is required but not available. Please install the Threading libraries.")

try:
    import time
except ImportError:
    raise RuntimeError("Time is required but not available. Please install the Time libraries.")

try:
    import queue
except ImportError:
    raise RuntimeError("Queue is required but not available. Please install the Queue libraries.")





class NotificationManager:
    def __init__(self):
        self.queue = queue.Queue()
        threading.Thread(target=self._run, daemon=True).start()

    def show_notification(self, message, duration=2):
        self.queue.put((message, duration))

    def _run(self):
        root = tk.Tk()
        root.withdraw()

        def next_banner():
            if self.queue.empty():
                root.after(100, next_banner)
                return

            msg, duration = self.queue.get()
            popup = tk.Toplevel(root)
            popup.overrideredirect(True)
            popup.attributes("-topmost", True)
            popup.configure(bg='black')
            popup.lift()

            font = ("Arial", 16, "bold")
            padding_x = 40
            padding_y = 30
            radius = 20

            # Calculate dimensions based on message
            dummy = tk.Tk()
            dummy.withdraw()
            temp_label = tk.Label(dummy, text=msg, font=font)
            temp_label.update_idletasks()
            text_width = temp_label.winfo_reqwidth()
            text_height = temp_label.winfo_reqheight()
            dummy.destroy()

            width = text_width + padding_x
            height = text_height + padding_y
            screen_width = popup.winfo_screenwidth()
            screen_height = popup.winfo_screenheight()
            x = (screen_width - width) // 2
            y_target = screen_height - height - 50
            y_start = screen_height + height

            popup.geometry(f"{width}x{height}+{x}+{y_start}")

            canvas = tk.Canvas(popup, width=width, height=height, bg='black', highlightthickness=0)
            canvas.pack()

            # 👉 Draw rectangles first
            canvas.create_rectangle(radius, 0, width - radius, height, fill='black', outline='black')
            canvas.create_rectangle(0, radius, width, height - radius, fill='black', outline='black')

            # 👉 Then draw corner arcs on top for visible rounded corners
            canvas.create_arc(0, 0, radius * 2, radius * 2, start=90, extent=90, fill='black', outline='black')
            canvas.create_arc(width - radius * 2, 0, width, radius * 2, start=0, extent=90, fill='black', outline='black')
            canvas.create_arc(0, height - radius * 2, radius * 2, height, start=180, extent=90, fill='black', outline='black')
            canvas.create_arc(width - radius * 2, height - radius * 2, width, height, start=270, extent=90, fill='black', outline='black')

            # Add the message label
            label = tk.Label(canvas, text=msg, fg='white', bg='black', font=font)
            label.place(relx=0.5, rely=0.5, anchor='center')

            # Slide in from bottom
            steps = 10
            for i in range(steps):
                y = y_start - (y_start - y_target) * (i + 1) / steps
                popup.geometry(f"{width}x{height}+{x}+{int(y)}")
                popup.update()
                time.sleep(0.03)

            time.sleep(duration)

            # Slide out
            for i in range(steps):
                y = y_target + (y_start - y_target) * (i + 1) / steps
                popup.geometry(f"{width}x{height}+{x}+{int(y)}")
                popup.update()
                time.sleep(0.03)

            popup.destroy()
            root.after(100, next_banner)

        next_banner()
        root.mainloop()
