import os
import pygame
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import random
from mutagen.mp3 import MP3
import time

pygame.mixer.init()

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("🎶 Advanced Python Music Player")
        self.root.geometry("550x600")
        self.root.configure(bg="#2C2F33")

        self.file_path = None
        self.song_length = 0
        self.play_start_time = 0
        self.paused_time = 0
        self.is_playing = False
        self.last_seek = 0

        tk.Label(root, text="🎵 Now Playing:", font=("Arial", 14, "bold"),
                 bg="#2C2F33", fg="#FEE75C").pack(pady=(10, 2))

        self.song_label = tk.Text(root, height=2, width=50, font=("Arial", 11),
                                  bg="#23272A", fg="white", bd=0)
        self.song_label.insert("1.0", "No file loaded. Drag or choose a file.")
        self.song_label.config(state="disabled")
        self.song_label.pack(pady=(0, 10))
        self.song_label.drop_target_register(DND_FILES)
        self.song_label.dnd_bind('<<Drop>>', self.on_drop)

        self.canvas = tk.Canvas(root, width=520, height=60,
                                bg="#23272A", highlightthickness=0)
        self.canvas.pack(pady=(5, 10))

        self.progress = tk.Scale(root, from_=0, to=100, orient="horizontal", length=520,
                                 bg="#2C2F33", fg="white", troughcolor="#7289DA",
                                 command=self.seek_song)
        self.progress.pack(pady=(0, 20))

        tk.Label(root, text="🔊 Volume", font=("Arial", 11, "bold"),
                 bg="#2C2F33", fg="#FEE75C").pack()
        self.volume = tk.DoubleVar(value=0.5)
        self.volume_slider = tk.Scale(root, from_=0, to=1, resolution=0.01,
                                      variable=self.volume, command=self.set_volume,
                                      orient="horizontal", length=520,
                                      bg="#2C2F33", fg="white", troughcolor="#7289DA")
        self.volume_slider.pack(pady=(0, 20))

        for text, cmd in [
            ("🎼 Choose Music", self.choose_file),
            ("▶️ Play", self.play),
            ("⏸ Pause", self.pause),
            ("⏯ Unpause", self.unpause),
            ("⏹ Stop", self.stop),
            ("⏭ Next Music", self.next_music)
        ]:
            tk.Button(self.root, text=text, command=cmd,
                      font=("Arial", 11, "bold"), bg="#7289DA", fg="white",
                      activebackground="#99AAB5", width=40, bd=0, pady=8).pack(pady=4)

        self.update_progress()
        self.animate_visualizer()

    def update_display(self, message):
        self.song_label.config(state="normal")
        self.song_label.delete("1.0", tk.END)
        self.song_label.insert("1.0", message)
        self.song_label.config(state="disabled")

    def choose_file(self):
        path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])
        if path:
            self.load_music(path)

    def on_drop(self, event):
        file = event.data.strip('{}')
        if os.path.isfile(file) and file.lower().endswith(('.mp3', '.wav')):
            self.load_music(file)
            self.play()
        else:
            messagebox.showerror("Invalid File", "Please drop a .mp3 or .wav file.")

    def load_music(self, path):
        self.file_path = path
        self.update_display(os.path.basename(path))
        if path.lower().endswith('.mp3'):
            self.song_length = MP3(path).info.length
        else:
            self.song_length = pygame.mixer.Sound(path).get_length()
        self.progress.config(to=int(self.song_length))
        self.last_seek = 0

    def play(self):
        if not self.file_path:
            messagebox.showinfo("No file", "Please choose or drop a music file first.")
            return
        pygame.mixer.music.load(self.file_path)
        pygame.mixer.music.play(start=self.last_seek)
        pygame.mixer.music.set_volume(self.volume.get())
        self.play_start_time = time.time() - self.last_seek
        self.is_playing = True

    def pause(self):
        if self.is_playing:
            pygame.mixer.music.pause()
            self.paused_time = time.time()
            self.is_playing = False

    def unpause(self):
        if not self.is_playing:
            pygame.mixer.music.unpause()
            pause_duration = time.time() - self.paused_time
            self.play_start_time += pause_duration
            self.is_playing = True

    def stop(self):
        pygame.mixer.music.stop()
        self.last_seek = 0
        self.is_playing = False
        self.progress.set(0)

    def next_music(self):
        self.choose_file()
        self.play()

    def set_volume(self, val):
        pygame.mixer.music.set_volume(float(val))

    def seek_song(self, val):
        if not self.file_path:
            return
        self.last_seek = float(val)
        self.play()

    def get_current_position(self):
        if self.is_playing:
            return time.time() - self.play_start_time
        else:
            return self.last_seek

    def update_progress(self):
        if self.is_playing:
            current_time = self.get_current_position()
            if current_time < self.song_length:
                self.progress.set(current_time)
            else:
                self.progress.set(self.song_length)
        self.root.after(500, self.update_progress)

    def animate_visualizer(self):
        self.canvas.delete("all")
        if self.is_playing:
            for i in range(32):
                x0 = i * 16
                y0 = 60
                y1 = 60 - random.randint(10, 55)
                self.canvas.create_rectangle(x0, y0, x0 + 10, y1, fill="#FEE75C", outline="#FEE75C")
        self.root.after(100, self.animate_visualizer)

# Run the application
root = TkinterDnD.Tk()
app = MusicPlayer(root)
root.mainloop()

