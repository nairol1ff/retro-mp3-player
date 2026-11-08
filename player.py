import os
import customtkinter as ctk
from pygame import mixer
from tkinter import filedialog

# Строгая темная тема оформления
ctk.set_appearance_mode("dark")

class OlderBrotherPlayerV2(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Инициализация аудио движка
        mixer.init()

        # Параметры окна
        self.title("BR0_PLAYER_v2.1.exe")
        self.geometry("450x600")
        self.resizable(False, False)

        # Логика и данные
        self.music_folder = ""
        self.playlist = []
        self.current_track_index = 0
        self.is_playing = False
        self.track_length = 0
        self.current_pos = 0

        # Олдскульные шрифты
        self.pixel_font_large = ctk.CTkFont(family="Courier", size=18, weight="bold")
        self.pixel_font_main = ctk.CTkFont(family="Courier", size=13, weight="bold")
        self.pixel_font_small = ctk.CTkFont(family="Courier", size=11)

        # Главный корпус
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, border_width=2, border_color="#00ff00", fg_color="#0a0a0a")
        self.main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Шапка
        self.logo_label = ctk.CTkLabel(self.main_frame, text="== CORE_AUDIO_SYSTEM_v2.1 ==", font=self.pixel_font_large, text_color="#00ff00")
        self.logo_label.pack(pady=(15, 10))

        # Зеленый ретро-дисплей
        self.display_frame = ctk.CTkFrame(self.main_frame, corner_radius=0, border_width=1, border_color="#333333", fg_color="#001100", height=90)
        self.display_frame.pack(fill="x", padx=15, pady=5)
        self.display_frame.pack_propagate(False)

        self.track_label = ctk.CTkLabel(self.display_frame, text="STATUS: NO_DISK_LOADED", font=self.pixel_font_main, text_color="#00ff00")
        self.track_label.pack(pady=(15, 5), padx=10)

        self.time_label = ctk.CTkLabel(self.display_frame, text="00:00 / 00:00", font=self.pixel_font_small, text_color="#00ff00")
        self.time_label.pack(pady=0)

        # Неоновый ползунок перемотки
        self.seek_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.seek_frame.pack(fill="x", padx=15, pady=5)

        self.seek_slider = ctk.CTkSlider(self.seek_frame, from_=0, to=100, corner_radius=0, height=12, progress_color="#00aa00", button_color="#00ff00", button_hover_color="#00ff00", fg_color="#222222", command=self.seek_track)
        self.seek_slider.set(0)
        self.seek_slider.pack(fill="x", expand=True)

        # Интерактивный кликабельный треклист
        self.list_frame = ctk.CTkFrame(self.main_frame, corner_radius=0, border_width=1, border_color="#333333", fg_color="#050505")
        self.list_frame.pack(fill="x", padx=15, pady=10)

        self.track_list_view = ctk.CTkScrollableFrame(self.list_frame, height=180, corner_radius=0, fg_color="#050505", label_text=" TRACKLIST_INFO ", label_font=self.pixel_font_small, label_text_color="#00ff00", label_fg_color="#0a0a0a")
        self.track_list_view.pack(fill="both", expand=True)
        
        self.track_buttons = []
        self.show_empty_msg()

        # Регулятор громкости
        self.volume_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.volume_frame.pack(fill="x", padx=25, pady=5)
        
        self.volume_label = ctk.CTkLabel(self.volume_frame, text="VOL:", font=self.pixel_font_small, text_color="#888888")
        self.volume_label.pack(side="left", padx=5)
        
        self.volume_slider = ctk.CTkSlider(self.volume_frame, from_=0, to=1, corner_radius=0, height=12, progress_color="#00aa00", button_color="#00ff00", fg_color="#222222", command=self.change_volume)
        self.volume_slider.set(0.5)
        self.volume_slider.pack(side="right", fill="x", expand=True, padx=5)

        # Физические деки управления
        self.controls_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.controls_frame.pack(pady=10)

        self.btn_prev = ctk.CTkButton(self.controls_frame, text="[ |<< ]", width=65, height=35, corner_radius=0, border_width=1, border_color="#00ff00", fg_color="#111111", font=self.pixel_font_main, text_color="#00ff00", command=self.prev_track)
        self.btn_prev.grid(row=0, column=0, padx=5)

        self.btn_play = ctk.CTkButton(self.controls_frame, text="[ > PLAY ]", width=95, height=35, corner_radius=0, border_width=1, border_color="#00ff00", fg_color="#111111", font=self.pixel_font_main, text_color="#00ff00", command=self.play_music)
        self.btn_play.grid(row=0, column=1, padx=5)

        self.btn_next = ctk.CTkButton(self.controls_frame, text="[ >>| ]", width=65, height=35, corner_radius=0, border_width=1, border_color="#00ff00", fg_color="#111111", font=self.pixel_font_main, text_color="#00ff00", command=self.next_track)
        self.btn_next.grid(row=0, column=2, padx=5)

        # Выбор каталога
        self.btn_browse = ctk.CTkButton(self.main_frame, text="[ СКАНИРОВАТЬ ДИРЕКТОРИЮ ]", corner_radius=0, border_width=1, border_color="#444444", fg_color="#151515", font=self.pixel_font_small, text_color="#aaaaaa", command=self.browse_folder)
        self.btn_browse.pack(pady=(5, 10))

        # Безопасный запуск таймера
        self.update_timer()

    def show_empty_msg(self):
        lbl = ctk.CTkLabel(self.track_list_view, text="Директория пуста. Загрузите файлы.", font=self.pixel_font_small, text_color="#555555")
        lbl.pack(pady=20)
        self.track_buttons.append(lbl)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.music_folder = folder
            self.playlist = [f for f in os.listdir(folder) if f.endswith(".mp3")]
            
            for btn in self.track_buttons:
                btn.destroy()
            self.track_buttons.clear()

            if self.playlist:
                for idx, track in enumerate(self.playlist):
                    # БАГ ИСПРАВЛЕН: Параметр `current_idx=idx` намертво привязывает кнопку к своей песне
                    btn = ctk.CTkButton(
                        self.track_list_view, 
                        text=f"{idx+1:02d}. {track[:35]}", 
                        anchor="w", 
                        corner_radius=0, 
                        fg_color="transparent", 
                        text_color="#00ff00", 
                        font=self.pixel_font_small, 
                        hover_color="#002200", 
                        height=25, 
                        command=lambda current_idx=idx: self.select_track(current_idx)
                    )
                    btn.pack(fill="x", padx=2, pady=1)
                    self.track_buttons.append(btn)
                
                self.current_track_index = 0
                self.load_track()
            else:
                self.show_empty_msg()

    def select_track(self, index):
        if 0 <= index < len(self.playlist):
            self.current_track_index = index
            self.current_pos = 0
            self.load_track()
            mixer.music.play()
            self.is_playing = True
            self.btn_play.configure(text="[ || PAUSE ]", fg_color="#220000", border_color="#ff0000", text_color="#ff0000")

    def load_track(self):
        try:
            track_path = os.path.join(self.music_folder, self.playlist[self.current_track_index])
            mixer.music.load(track_path)
            sound = mixer.Sound(track_path)
            self.track_length = int(sound.get_length())
            self.seek_slider.configure(to=self.track_length)
            self.current_pos = 0
            self.seek_slider.set(0)
            self.track_label.configure(text=f"LOADED: {self.playlist[self.current_track_index][:22]}")
            self.update_time_display()
        except Exception:
            self.track_label.configure(text="ERROR_LOADING_TRACK")

    def play_music(self):
        if not self.playlist:
            return
        
        if not self.is_playing:
            if self.current_pos == 0:
                mixer.music.play()
            else:
                mixer.music.unpause()
            self.btn_play.configure(text="[ || PAUSE ]", fg_color="#220000", border_color="#ff0000", text_color="#ff0000")
            self.track_label.configure(text=f"PLAYING: {self.playlist[self.current_track_index][:22]}")
            self.is_playing = True
        else:
            mixer.music.pause()
            self.btn_play.configure(text="[ > PLAY ]", fg_color="#111111", border_color="#00ff00", text_color="#00ff00")
            self.is_playing = False

    def next_track(self):
        if self.playlist:
            self.select_track((self.current_track_index + 1) % len(self.playlist))

    def prev_track(self):
        if self.playlist:
            self.select_track((self.current_track_index - 1) % len(self.playlist))

    def seek_track(self, value):
        if self.playlist and self.is_playing:
            self.current_pos = int(float(value))
            # Безопасный перезапуск трека с нужной секунды
            mixer.music.play(start=self.current_pos)
            self.update_time_display()

    def change_volume(self, value):
        mixer.music.set_volume(value)

    def update_time_display(self):
        cur_min, cur_sec = divmod(self.current_pos, 60)
        max_min, max_sec = divmod(self.track_length, 60)
        self.time_label.configure(text=f"{cur_min:02d}:{cur_sec:02d} / {max_min:02d}:{max_sec:02d}")

    def update_timer(self):
        if self.is_playing:
            self.current_pos += 1
            if self.current_pos >= self.track_length:
                self.next_track()
            else:
                self.seek_slider.set(self.current_pos)
                self.update_time_display()
        # Стабильный цикл обновления
        self.after(1000, self.update_timer)

if __name__ == "__main__":
    app = OlderBrotherPlayerV2()
    app.mainloop()
