import sys
import time
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as font
import webbrowser
from pynput import keyboard
import threading

from src.connect_server import retrieve_data as retrieve, set_score as score
from src.utils import threaded







class App_Multi(tk.Frame):
	def __init__(self, parent, controller):
		"""Initialisation de l'objet"""
		# On crée une frame Tkinter
		tk.Frame.__init__(self, parent)
		self.controller = controller

		self.written = []
		self.sentence = ""
		self.start_time = None
		self.thread = False

		# On crée quatre packs pour formatter l'affichage
		frame1, frame2, frame3, frame4, frame5 = ttk.Frame(self), ttk.Frame(self), ttk.Frame(self), ttk.Frame(self), ttk.Frame(self)

		# Définition des widgets
		self.label_hello = ttk.Label(frame1, text="Commencez quand vous êtes prêt")
		self.text_entry = tk.Text(frame2, wrap=tk.WORD, width=50, height=10)
		self.label_you = ttk.Label(frame4, text="aaa")
		self.label_advers = ttk.Label(frame4, text="aaa")
		self.github_icon = ttk.Label(self, image=self.master.master.github_icon, cursor="hand2")
		self.back_button = ttk.Label(self, image=self.master.master.back_button, cursor="hand2")
		self.reskin = ttk.Label(self, image=self.master.master.reskin, cursor="hand2")
		self.github_icon.bind("<Button-1>", lambda _: webbrowser.open_new("https://github.com/SkohTV/KeyboardMaster"))
		self.back_button.bind("<Button-1>", lambda _: self.back())
		self.reskin.bind("<Button-1>", lambda _: self.master.master.change_skin())
		self.gamemodes_var = []
		self.gamemodes_array = []

		# On peuple self.gamemodes_var et self.gamemodes_array avec les modes de jeu
		for index, elem in enumerate(("easy", "insane")):
			self.gamemodes_var.append(tk.BooleanVar())
			self.gamemodes_array.append(ttk.Checkbutton(frame3, text=elem, variable=self.gamemodes_var[index], onvalue=True, offvalue=False))

		# Changement de certains paramètres de style (police & couleur)
		self.label_hello["font"] = font.Font(family="Verdana", weight="bold", size=20)
		self.text_entry["font"] = font.Font(size=12)
		self.text_entry.tag_configure("empty", foreground="white")
		self.text_entry.tag_configure("good", foreground="green")
		self.text_entry.tag_configure("wrong", foreground="red")
		self.text_entry.tag_configure("wrong-space", background="red")
		self.text_entry.insert(tk.END, "")
		self.text_entry.configure(state="disabled")

		# Placement des widgets dans la fenêtre
		self.label_hello.pack(pady=20)
		self.text_entry.pack(side=tk.LEFT)
		self.label_you.pack(side=tk.LEFT, padx=20)
		self.label_advers.pack(side=tk.LEFT, padx=20)
		[i.pack(side=tk.TOP, anchor=tk.W, pady=8) for i in self.gamemodes_array]
		[i.set(False) for i in self.gamemodes_var]
		self.github_icon.place(x=5, y=360)
		self.back_button.place(x=5, y=20)
		self.reskin.place(x=660, y=360)

		# On pack les 4 frames
		frame1.pack()
		frame2.pack()
		frame4.pack(side=tk.BOTTOM, pady=30)
		frame5.pack(side=tk.BOTTOM)
		frame3.place(x=600, y=(100 - frame3.winfo_height()/2), anchor=tk.NW)

		self.master.master.bind("<<StartMulti>>", self.on_arrive)


	@threaded
	def listen_keypresses(self):

		def on_press(key):
			if key == keyboard.Key.space:
				key = " "
			elif key == keyboard.Key.backspace:
				key = "backspace"
			else:
				try:
					key = key.char
				except AttributeError:
					return

			if key == "backspace":
				if self.written:
					for i in ("good", "wrong", "empty", "wrong-space"):
						self.text_entry.tag_remove(i, f"1.{len(self.written)-1}", f"1.{len(self.written)}")
					self.written.pop()
				return

			elif len(self.written) < len(self.sentence):
				if self.start_time is None:
					self.start_time = time.time()
					self.label_hello.config(text="Écrivez le plus vite possible !")
				else:
					try:
						self.label_you.configure(text=f"{self.master.master.user.name} : {len(self.written) / (time.time() - self.start_time) : .3f}cps")
					except ZeroDivisionError:
						pass

				self.written.append(key)

			for i in ("good", "wrong", "empty", "wrong-space"):
				self.text_entry.tag_remove(i, f"1.{len(self.written)-1}", f"1.{len(self.written)}")

			if key == self.sentence[len(self.written)-1]:
				self.text_entry.tag_add("good", f"1.{len(self.written)-1}", f"1.{len(self.written)}")
			else:
				if self.sentence[len(self.written)-1] == " " or not self.sentence[len(self.written)-1].isalnum():
					self.text_entry.tag_add("wrong-space", f"1.{len(self.written)-1}", f"1.{len(self.written)}")
				else:
					self.text_entry.tag_add("wrong", f"1.{len(self.written)-1}", f"1.{len(self.written)}")

			if len(self.written) >= len(self.sentence):
				wrong = len(self.sentence)
				for index, elem in enumerate(self.sentence):
					if elem == self.written[index]:
						wrong -= 1
				if wrong == 0:
					current_time = time.time()
					self.label_hello.config(text=f"Votre score est de : {len(self.written) / (current_time - self.start_time) : .3f}cps")
					self.thread = False

		with keyboard.Listener(on_press=on_press) as listener:
			def stop_event():
				self.thread = True
				while self.thread:
					time.sleep(0.01)
				listener.stop()

			threading.Thread(target=stop_event).start()
			listener.join()
			print("Stopped")


	@threaded
	def send_ms(self):
		while (self.thread):
			val = 0 if not self.start_time else round(len(self.written) / (time.time() - self.start_time), 3) * 1000
			res = score(self.master.master.user, self.master.master.match_res["gameID"], val)
			time.sleep(0.25)

	@threaded
	def receive_ms(self):
		while (self.thread):
			res = retrieve(self.master.master.user, self.master.master.match_res["gameID"])
			if "player" in res:
				self.label_advers.config(text=f"{res['player']} : {int(res['playerms']) / 1000 : .3f}cps")
			time.sleep(0.25)


	def text_update(self, text):
		self.text_entry.configure(state="normal")
		self.text_entry.delete("1.0", tk.END)
		self.text_entry.insert(tk.END, text)
		self.text_entry.configure(state="disabled")


	def back(self):
		self.reset()
		self.master.master.external_show_frame("App_Main")


	def reset(self):
		self.thread = False
		self.written = []
		self.sentence = ""
		self.start_time = None
		self.label_you.config(text="")
		self.label_hello.config(text="Commencez quand vous êtes prêt")
		self.text_update("")


	def on_arrive(self, _):
		self.thread = True
		print(self.master.master.match_res)
		self.sentence = self.master.master.match_res["sentence"]
		self.text_update(self.sentence)
		self.label_you.config(text=f"{self.master.master.user.name} : {0 : .3f}cps")
		self.label_advers.config(text="...")
		self.listen_keypresses()
		self.send_ms()
		self.receive_ms()