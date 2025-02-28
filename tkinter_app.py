import tkinter as tk
from tkinter import ttk, scrolledtext, font as tkfont, messagebox
import asyncio
import time
import threading
import pyperclip
from trans import translate_text
from pypinyin import pinyin, Style

class TranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("English-Chinese Translator")
        self.root.geometry("950x750")
        self.root.configure(bg="#f0f0f0")
        
        # Set theme and styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', font=('Helvetica', 10, 'bold'))
        style.configure('TLabel', font=('Helvetica', 10))
        style.configure('Copy.TButton', font=('Helvetica', 9))
        style.configure('TLabelframe', font=('Helvetica', 10, 'bold'))
        style.configure('TLabelframe.Label', font=('Helvetica', 10, 'bold'))
        style.configure('Info.TFrame', background='#e8f4f8')
        
        # Configure the grid
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(1, weight=3)  # Main text areas (larger)
        self.root.rowconfigure(2, weight=1)  # Pinyin area (smaller)
        self.root.rowconfigure(3, weight=0)  # Info area
        
        # Create custom fonts
        self.custom_font = tkfont.Font(family="Helvetica", size=12)
        self.pinyin_font = tkfont.Font(family="Helvetica", size=11, slant="italic")
        self.info_font = tkfont.Font(family="Helvetica", size=9)
        
        # Language selection
        self.lang_frame = ttk.Frame(root, padding="10 10 10 10")
        self.lang_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        self.src_lang_var = tk.StringVar(value="en")
        self.dest_lang_var = tk.StringVar(value="zh")
        self.show_pinyin_var = tk.BooleanVar(value=True)
        self.auto_translate_var = tk.BooleanVar(value=True)
        self.auto_translate_delay = 1000  # ms
        self.translate_timer = None
        self.last_typed_time = 0
        self.translation_counter = 0
        
        # Left side controls
        left_controls = ttk.Frame(self.lang_frame)
        left_controls.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(left_controls, text="Source Language:").pack(side=tk.LEFT, padx=5)
        self.src_lang_combo = ttk.Combobox(left_controls, textvariable=self.src_lang_var,
                                         values=["en", "zh"], width=5, state="readonly")
        self.src_lang_combo.pack(side=tk.LEFT, padx=5)
        
        self.swap_btn = ttk.Button(left_controls, text="⇄", command=self.swap_languages, width=3)
        self.swap_btn.pack(side=tk.LEFT, padx=20)
        
        ttk.Label(left_controls, text="Target Language:").pack(side=tk.LEFT, padx=5)
        self.dest_lang_combo = ttk.Combobox(left_controls, textvariable=self.dest_lang_var,
                                          values=["en", "zh"], width=5, state="readonly")
        self.dest_lang_combo.pack(side=tk.LEFT, padx=5)
        
        # Right side controls
        right_controls = ttk.Frame(self.lang_frame)
        right_controls.pack(side=tk.RIGHT, padx=5)
        
        # Auto-translate checkbox
        self.auto_translate_check = ttk.Checkbutton(right_controls, text="Auto-translate", 
                                                 variable=self.auto_translate_var)
        self.auto_translate_check.pack(side=tk.RIGHT, padx=10)
        
        # Show pinyin checkbox
        self.show_pinyin_check = ttk.Checkbutton(right_controls, text="Show Pinyin",
                                              variable=self.show_pinyin_var,
                                              command=self.toggle_pinyin)
        self.show_pinyin_check.pack(side=tk.RIGHT, padx=10)
        
        # Source text area with copy button
        self.src_container = ttk.Frame(root)
        self.src_container.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        
        self.src_frame = ttk.LabelFrame(self.src_container, text="Source Text", padding="5 5 5 5")
        self.src_frame.pack(fill=tk.BOTH, expand=True)
        
        self.src_text = scrolledtext.ScrolledText(self.src_frame, wrap=tk.WORD, font=self.custom_font)
        self.src_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.src_btn_frame = ttk.Frame(self.src_frame)
        self.src_btn_frame.pack(fill=tk.X, pady=2)
        
        self.src_copy_btn = ttk.Button(self.src_btn_frame, text="Copy", style="Copy.TButton",
                                     command=lambda: self.copy_to_clipboard(self.src_text))
        self.src_copy_btn.pack(side=tk.RIGHT, padx=5)
        
        self.src_clear_btn = ttk.Button(self.src_btn_frame, text="Clear", style="Copy.TButton",
                                      command=lambda: self.clear_specific(self.src_text))
        self.src_clear_btn.pack(side=tk.RIGHT, padx=5)
        
        # Translated text area with copy button
        self.dest_container = ttk.Frame(root)
        self.dest_container.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")
        
        self.dest_frame = ttk.LabelFrame(self.dest_container, text="Translation", padding="5 5 5 5")
        self.dest_frame.pack(fill=tk.BOTH, expand=True)
        
        self.dest_text = scrolledtext.ScrolledText(self.dest_frame, wrap=tk.WORD, font=self.custom_font)
        self.dest_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.dest_btn_frame = ttk.Frame(self.dest_frame)
        self.dest_btn_frame.pack(fill=tk.X, pady=2)
        
        self.dest_copy_btn = ttk.Button(self.dest_btn_frame, text="Copy", style="Copy.TButton",
                                      command=lambda: self.copy_to_clipboard(self.dest_text))
        self.dest_copy_btn.pack(side=tk.RIGHT, padx=5)
        
        self.dest_clear_btn = ttk.Button(self.dest_btn_frame, text="Clear", style="Copy.TButton",
                                       command=lambda: self.clear_specific(self.dest_text))
        self.dest_clear_btn.pack(side=tk.RIGHT, padx=5)
        
        # Pinyin area
        self.pinyin_frame = ttk.LabelFrame(root, text="Pinyin", padding="5 5 5 5")
        self.pinyin_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        
        self.pinyin_text = scrolledtext.ScrolledText(self.pinyin_frame, wrap=tk.WORD,
                                                  height=4, font=self.pinyin_font)
        self.pinyin_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.pinyin_btn_frame = ttk.Frame(self.pinyin_frame)
        self.pinyin_btn_frame.pack(fill=tk.X, pady=2)
        
        self.pinyin_copy_btn = ttk.Button(self.pinyin_btn_frame, text="Copy", style="Copy.TButton",
                                       command=lambda: self.copy_to_clipboard(self.pinyin_text))
        self.pinyin_copy_btn.pack(side=tk.RIGHT, padx=5)
        
        if not self.show_pinyin_var.get():
            self.pinyin_frame.grid_remove()
        
        # Info area
        self.info_frame = ttk.Frame(root, style='Info.TFrame', padding="10 5 10 5")
        self.info_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        
        # Left info - translation stats
        self.stats_frame = ttk.Frame(self.info_frame)
        self.stats_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.char_count_var = tk.StringVar(value="Characters: 0")
        self.word_count_var = tk.StringVar(value="Words: 0")
        self.trans_count_var = tk.StringVar(value="Translations: 0")
        
        ttk.Label(self.stats_frame, textvariable=self.char_count_var, font=self.info_font).pack(side=tk.LEFT, padx=15)
        ttk.Label(self.stats_frame, textvariable=self.word_count_var, font=self.info_font).pack(side=tk.LEFT, padx=15)
        ttk.Label(self.stats_frame, textvariable=self.trans_count_var, font=self.info_font).pack(side=tk.LEFT, padx=15)
        
        # Right info - translation time
        self.time_frame = ttk.Frame(self.info_frame)
        self.time_frame.pack(side=tk.RIGHT)
        
        self.time_var = tk.StringVar(value="Last translation: 0.00s")
        ttk.Label(self.time_frame, textvariable=self.time_var, font=self.info_font).pack(side=tk.RIGHT, padx=10)
        
        # Control buttons
        self.button_frame = ttk.Frame(root, padding="5 10 5 10")
        self.button_frame.grid(row=4, column=0, columnspan=2, pady=5)
        
        self.translate_button = ttk.Button(self.button_frame, text="Translate Now",
                                        command=self.translate, width=15)
        self.translate_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = ttk.Button(self.button_frame, text="Clear All",
                                     command=self.clear_text, width=15)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # Help button
        self.help_button = ttk.Button(self.button_frame, text="Help", width=8, 
                                   command=self.show_help)
        self.help_button.pack(side=tk.RIGHT, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(root, textvariable=self.status_var,
                                  relief=tk.SUNKEN, anchor=tk.W, padding="5 2 5 2")
        self.status_bar.grid(row=5, column=0, columnspan=2, sticky="ew")
        self.status_var.set("Ready")
        
        # Bind events
        self.src_text.bind("<Control-Return>", lambda event: self.translate())
        self.src_text.bind("<KeyRelease>", self.key_released)
        self.src_text.bind("<<Modified>>", self.update_char_count)
        
    def key_released(self, event):
        """Handle text changes and trigger auto-translation"""
        if not self.auto_translate_var.get():
            return
            
        # Cancel previous timer if it exists
        if self.translate_timer:
            self.root.after_cancel(self.translate_timer)
            
        # Update character and word count
        self.update_counts()
        
        # Start a new timer
        self.translate_timer = self.root.after(self.auto_translate_delay, self.translate)
    
    def update_counts(self):
        """Update character and word counts in the UI"""
        text = self.src_text.get("1.0", tk.END).strip()
        char_count = len(text)
        word_count = len(text.split()) if text else 0
        
        self.char_count_var.set(f"Characters: {char_count}")
        self.word_count_var.set(f"Words: {word_count}")
    
    def update_char_count(self, event=None):
        """Update character count when text is modified"""
        self.src_text.edit_modified(False)  # Reset the modified flag
        self.update_counts()
        
    def swap_languages(self):
        src = self.src_lang_var.get()
        dest = self.dest_lang_var.get()
        self.src_lang_var.set(dest)
        self.dest_lang_var.set(src)
        # Swap text
        src_text = self.src_text.get("1.0", tk.END).strip()
        dest_text = self.dest_text.get("1.0", tk.END).strip()
        
        self.src_text.delete("1.0", tk.END)
        self.dest_text.delete("1.0", tk.END)
        
        if dest_text:
            self.src_text.insert(tk.END, dest_text)
        if src_text:
            self.dest_text.insert(tk.END, src_text)
        
        # Update pinyin if needed
        if self.show_pinyin_var.get():
            if src == "zh":
                self.generate_pinyin(dest_text)
            elif dest == "zh":
                self.generate_pinyin(src_text)
            else:
                self.pinyin_text.delete("1.0", tk.END)
        
        # Update counts
        self.update_counts()
        
    def toggle_pinyin(self):
        if self.show_pinyin_var.get():
            self.pinyin_frame.grid()
            dest_text = self.dest_text.get("1.0", tk.END).strip()
            if dest_text and self.dest_lang_var.get() == "zh":
                self.generate_pinyin(dest_text)
        else:
            self.pinyin_frame.grid_remove()
    
    def generate_pinyin(self, chinese_text):
        if not chinese_text:
            return
        
        try:
            # Generate pinyin with tone marks
            pinyin_result = pinyin(chinese_text, style=Style.TONE)
            pinyin_text = ' '.join([item[0] for item in pinyin_result])
            
            self.pinyin_text.delete("1.0", tk.END)
            self.pinyin_text.insert(tk.END, pinyin_text)
        except Exception as e:
            self.pinyin_text.delete("1.0", tk.END)
            self.pinyin_text.insert(tk.END, f"Error generating pinyin: {str(e)}")
        
    def copy_to_clipboard(self, text_widget):
        """Copy the content of the specified text widget to clipboard"""
        text = text_widget.get("1.0", tk.END).strip()
        if text:
            pyperclip.copy(text)
            self.status_var.set("Text copied to clipboard")
            # Change status back after 2 seconds
            self.root.after(2000, lambda: self.status_var.set("Ready"))
    
    def clear_specific(self, text_widget):
        """Clear only the specified text widget"""
        text_widget.delete("1.0", tk.END)
        if text_widget == self.src_text:
            self.update_counts()
        elif text_widget == self.pinyin_text:
            pass
        self.status_var.set("Text cleared")
        
    def clear_text(self):
        """Clear all text areas"""
        self.src_text.delete("1.0", tk.END)
        self.dest_text.delete("1.0", tk.END)
        self.pinyin_text.delete("1.0", tk.END)
        self.status_var.set("All text cleared")
        self.update_counts()
        
    def translate(self):
        """Translate text from source to destination language"""
        src_text = self.src_text.get("1.0", tk.END).strip()
        if not src_text:
            self.status_var.set("Error: No text to translate")
            return
        
        src_lang = self.src_lang_var.get()
        dest_lang = self.dest_lang_var.get()
        
        self.status_var.set("Translating...")
        self.translate_button.config(state=tk.DISABLED)
        self.root.update()
        
        # Run translation in a separate thread to avoid blocking UI
        threading.Thread(target=self._perform_translation, args=(src_text, src_lang, dest_lang), daemon=True).start()
    
    def _perform_translation(self, text, src_lang, dest_lang):
        """Internal method to perform translation asynchronously"""
        try:
            start_time = time.time()
            translation = asyncio.run(translate_text(text, src_lang, dest_lang))
            end_time = time.time()
            
            # Update UI on the main thread
            self.root.after(0, lambda: self._update_translation_ui(translation, start_time, end_time, dest_lang))
            
        except Exception as e:
            # Update error on the main thread
            self.root.after(0, lambda: self._handle_translation_error(str(e)))
    
    def _update_translation_ui(self, translation, start_time, end_time, dest_lang):
        """Update UI with translation results"""
        self.dest_text.delete("1.0", tk.END)
        self.dest_text.insert(tk.END, translation)
        
        # Generate pinyin if target language is Chinese and pinyin is shown
        if dest_lang == "zh" and self.show_pinyin_var.get():
            self.generate_pinyin(translation)
        else:
            self.pinyin_text.delete("1.0", tk.END)
        
        time_taken = end_time - start_time
        self.translation_counter += 1
        
        # Update information
        self.time_var.set(f"Last translation: {time_taken:.2f}s")
        self.trans_count_var.set(f"Translations: {self.translation_counter}")
        self.status_var.set(f"Translation completed in {time_taken:.2f} seconds")
        
        # Re-enable the translate button
        self.translate_button.config(state=tk.NORMAL)
    
    def _handle_translation_error(self, error_message):
        """Handle translation errors"""
        self.status_var.set(f"Error: {error_message}")
        self.translate_button.config(state=tk.NORMAL)
    
    def show_help(self):
        """Show help information"""
        help_text = """
English-Chinese Translator Help

Features:
- Auto-translate: Automatically translates after typing
- Copy buttons: Copy text from any panel to clipboard
- Pinyin: Shows pronunciation for Chinese characters
- Keyboard shortcut: Ctrl+Enter to translate immediately

Tips:
- For longer texts, turn off auto-translation
- Swap button exchanges languages and text
- Character and word counts update in real time
        """
        messagebox.showinfo("Translator Help", help_text)

def main():
    root = tk.Tk()
    app = TranslatorApp(root)
    # Set icon and window properties
    root.minsize(850, 650)
    try:
        root.iconbitmap("icon.ico")  # If you have an icon file
    except:
        pass
    root.mainloop()

if __name__ == "__main__":
    main()
