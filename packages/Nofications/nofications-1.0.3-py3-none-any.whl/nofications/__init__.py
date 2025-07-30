import tkinter as tk
import multiprocessing
import time
import queue

class NotificationManager:
    def __init__(self):
        self.queue = multiprocessing.Queue()

    def show_notification(self, message, duration=2):
        self.queue.put((message, duration))
        # Start GUI process only when showing first notification
        if not hasattr(self, 'gui_process') or not self.gui_process.is_alive():
            self.gui_process = multiprocessing.Process(target=self._run)
            self.gui_process.start()

    def _run(self):
        root = tk.Tk()
        root.withdraw()

        def check_queue():
            try:
                while not self.queue.empty():
                    msg, duration = self.queue.get()
                    show_popup(msg, duration)
            except Exception:
                pass
            root.after(100, check_queue)

        def show_popup(msg, duration):
            popup = tk.Toplevel(root)
            popup.overrideredirect(True)
            popup.attributes("-topmost", True)
            popup.configure(bg='black')
            popup.lift()

            font = ("Arial", 16, "bold")
            padding_x, padding_y, radius = 40, 30, 20

            # Estimate size
            temp = tk.Label(root, text=msg, font=font)
            temp.update_idletasks()
            width = temp.winfo_reqwidth() + padding_x
            height = temp.winfo_reqheight() + padding_y
            temp.destroy()

            sw, sh = popup.winfo_screenwidth(), popup.winfo_screenheight()
            x = (sw - width) // 2
            y_target = sh - height - 50
            y_start = sh + height

            popup.geometry(f"{width}x{height}+{x}+{y_start}")

            canvas = tk.Canvas(popup, width=width, height=height, bg='black', highlightthickness=0)
            canvas.pack()

            canvas.create_rectangle(radius, 0, width - radius, height, fill='black', outline='black')
            canvas.create_rectangle(0, radius, width, height - radius, fill='black', outline='black')
            canvas.create_arc(0, 0, radius*2, radius*2, start=90, extent=90, fill='black', outline='black')
            canvas.create_arc(width - radius*2, 0, width, radius*2, start=0, extent=90, fill='black', outline='black')
            canvas.create_arc(0, height - radius*2, radius*2, height, start=180, extent=90, fill='black', outline='black')
            canvas.create_arc(width - radius*2, height - radius*2, width, height, start=270, extent=90, fill='black', outline='black')

            label = tk.Label(canvas, text=msg, fg='white', bg='black', font=font)
            label.place(relx=0.5, rely=0.5, anchor='center')

            for i in range(10):
                y = y_start - (y_start - y_target) * (i + 1) / 10
                popup.geometry(f"{width}x{height}+{x}+{int(y)}")
                popup.update()
                time.sleep(0.03)

            time.sleep(duration)

            for i in range(10):
                y = y_target + (y_start - y_target) * (i + 1) / 10
                popup.geometry(f"{width}x{height}+{x}+{int(y)}")
                popup.update()
                time.sleep(0.03)

            popup.destroy()

        check_queue()
        root.mainloop()
