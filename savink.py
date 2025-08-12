# -*- coding: utf-8 -*-

"""
Ứng dụng Quản lý File, Thư Mục và Liên kết
Phiên bản: 0.12.3 Alpha
Tác giả: Minji x AI Assistant x ChatGPT-5o
Ngôn ngữ: Python 3
Thư viện GUI: Tkinter
"""

# --- Thư viện chuẩn ---
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from tkinter import ttk, filedialog, simpledialog, messagebox
import tkinter as tk
import webbrowser

# --- Thư viện bên thứ ba (tùy chọn) ---
try:
    import markdown2
    from tkhtmlview import HTMLLabel
    MARKDOWN_LIBS_AVAILABLE = True
except ImportError:
    MARKDOWN_LIBS_AVAILABLE = False

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


# --- LỚP CẤU HÌNH TRUNG TÂM ---
class AppConfig:
    """Lưu trữ các hằng số và cấu hình cho ứng dụng."""
    APP_TITLE = "Trình quản lý File"
    ROOT_DIR_NAME = "FileManagerRoot"
    SETTINGS_FILE_NAME = "settings.json"
    LOGO_FILE_NAME = "logo.png"
    LOCKED_SUFFIX = ".locked"

    INSTALL_DIR = os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'savink')
    ROOT_DIR = os.path.join(INSTALL_DIR, ROOT_DIR_NAME)
    SETTINGS_FILE_PATH = os.path.join(INSTALL_DIR, SETTINGS_FILE_NAME)
    LOGO_PATH = os.path.join(INSTALL_DIR, LOGO_FILE_NAME)

    LINK_EXT = ".link"
    TODO_EXT = ".todo"
    TEXT_EXT = ".txt"
    MARKDOWN_EXTS = (".md", ".markdown")
    IMAGE_EXTS = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff')
    PDF_EXT = '.pdf'

    DEFAULT_SETTINGS = {
        'theme': 'light',
        'geometry': '1580x720'
    }

    FONT_UI_REGULAR = ('Segoe UI', 10)
    FONT_UI_BOLD = ('Segoe UI', 10, 'bold')
    FONT_EDITOR = ('Consolas', 10)
    COLOR_SELECTED_ITEM = '#0078d7'
    
    ICON_FOLDER = "📁"
    ICON_LINK = "🔗"
    ICON_TODO = "✅"
    ICON_MARKDOWN = "Ⓜ️"
    ICON_PDF = "🅿️"
    ICON_FILE = "📄"
    ICON_LOCKED = "🔒"


# --- LỚP ỨNG DỤNG CHÍNH ---
class FileManagerApp(tk.Tk):
    """Lớp chính của ứng dụng quản lý file."""

    def __init__(self):
        super().__init__()
        self._load_settings()
        self._ensure_root_exists()
        self._initialize_state()
        self._create_widgets()
        self._setup_window()
        self._setup_bindings()
        self.populate_view(self.current_path)

    def _initialize_state(self):
        self.current_path = AppConfig.ROOT_DIR
        self.clipboard_path = None
        self.clipboard_operation = None
        self.editing_file_path = None
        self.editor_widget = None
        self.initial_content = None
        self.current_theme = self.settings.get('theme', AppConfig.DEFAULT_SETTINGS['theme'])

        self.image_viewer_data = {
            "canvas": None, "canvas_image_id": None, "original_image": None,
            "displayed_image": None, "zoom_level": 1.0, "image_pos": [0, 0],
            "drag_start": None, "info_label": None
        }
        self.pdf_viewer_data = {
            "doc": None, "photo_image": None, "current_page": 0, "total_pages": 0,
            "canvas": None, "page_label": None, "prev_button": None, "next_button": None,
            "zoom_level": 1.0, "image_pos": [0, 0], "drag_start": None,
            "canvas_page_id": None, "info_label": None
        }
        self.markdown_view_modes = {}

    def _setup_window(self):
        self.title(f"{AppConfig.APP_TITLE} - [{AppConfig.ROOT_DIR_NAME}]")
        self.geometry(self.settings.get('geometry', AppConfig.DEFAULT_SETTINGS['geometry']))

        try:
            if os.path.exists(AppConfig.LOGO_PATH):
                logo_image = Image.open(AppConfig.LOGO_PATH)
                photo_image = ImageTk.PhotoImage(logo_image)
                self.iconphoto(False, photo_image)
            else:
                 print(f"Cảnh báo: Không tìm thấy file logo tại '{AppConfig.LOGO_PATH}' để đặt icon cho cửa sổ.")
        except Exception as e:
            print(f"Lỗi khi tải logo cửa sổ: {e}")

        self.protocol("WM_DELETE_WINDOW", self.on_close_window)
        self.style = ttk.Style(self)
        self.apply_theme()

    def _create_widgets(self):
        self.create_main_menu()
        self.create_toolbar()
        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True)
        list_frame = ttk.Frame(main_pane, padding="5")
        self.item_view = ttk.Treeview(list_frame, columns=("type", "size", "modified"), show="tree headings")
        self.item_view.heading("#0", text="Tên", anchor='w')
        self.item_view.heading("type", text="Loại")
        self.item_view.heading("size", text="Kích thước")
        self.item_view.heading("modified", text="Ngày sửa")
        self.item_view.column("#0", width=135, anchor='w', stretch=tk.YES)
        self.item_view.column("type", width=65, anchor='w')
        self.item_view.column("size", width=20, anchor='e')
        self.item_view.column("modified", width=50, anchor='w')
        list_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.item_view.yview)
        self.item_view.configure(yscrollcommand=list_scrollbar.set)
        self.item_view.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        main_pane.add(list_frame, weight=3)
        self.content_frame = ttk.Frame(main_pane, padding="5")
        main_pane.add(self.content_frame, weight=5)
        self.create_status_bar()

    def _setup_bindings(self):
        self.item_view.bind("<<TreeviewSelect>>", self.on_item_select)
        self.item_view.bind("<Double-1>", self.on_double_click); self.item_view.bind("<Return>", self.on_double_click)
        self.item_view.bind("<Button-3>", self.show_context_menu)
        self.bind_all("<F5>", lambda e: self.populate_view(self.current_path))
        self.bind_all("<Control-s>", self.handle_save_shortcut)
        self.bind_all("<Control-w>", lambda e: self.on_close_window())
        self.item_view.bind("<Control-c>", self.handle_copy_shortcut)
        self.item_view.bind("<Control-x>", self.handle_cut_shortcut)
        self.bind("<Control-v>", self.handle_paste_shortcut)

    def _ensure_root_exists(self):
        try:
            if not os.path.exists(AppConfig.ROOT_DIR): os.makedirs(AppConfig.ROOT_DIR)
        except OSError as e:
            messagebox.showerror("Lỗi nghiêm trọng", f"Không thể tạo thư mục gốc!\n{e}"); self.quit()

    def _load_settings(self):
        """Tải cài đặt từ file settings.json, nếu không có thì tạo mới."""
        try:
            with open(AppConfig.SETTINGS_FILE_PATH, 'r', encoding='utf-8') as f:
                self.settings = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.settings = AppConfig.DEFAULT_SETTINGS.copy()
            self._save_settings()

    def _save_settings(self):
        """Lưu các cài đặt hiện tại vào file settings.json."""
        try:
            os.makedirs(AppConfig.INSTALL_DIR, exist_ok=True)
            with open(AppConfig.SETTINGS_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
        except OSError as e:
            print(f"Cảnh báo: Không thể lưu cài đặt. Lỗi: {e}")

    def create_toolbar(self):
        toolbar = ttk.Frame(self, padding=(5, 5, 5, 0)); toolbar.pack(side=tk.TOP, fill=tk.X)
        self.up_button = ttk.Button(toolbar, text="⬆️ Đi lên", command=self.go_up)
        self.up_button.pack(side=tk.LEFT, padx=(0, 5))
        refresh_button = ttk.Button(toolbar, text="🔄 Làm mới", command=lambda: self.populate_view(self.current_path))
        refresh_button.pack(side=tk.LEFT, padx=2)
        self.address_bar = ttk.Entry(toolbar, font=AppConfig.FONT_UI_REGULAR)
        self.address_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.address_bar.bind("<Return>", lambda e: self.populate_view(self.address_bar.get()))

    def create_main_menu(self):
        menu_bar = tk.Menu(self); self.config(menu=menu_bar)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Làm mới", accelerator="F5", command=lambda: self.populate_view(self.current_path))
        file_menu.add_separator(); file_menu.add_command(label="Thoát", accelerator="Ctrl+W", command=self.on_close_window)
        menu_bar.add_cascade(label="Tệp", menu=file_menu)
        settings_menu = tk.Menu(menu_bar, tearoff=0)
        settings_menu.add_command(label="Chuyển giao diện Sáng/Tối", command=self.toggle_theme)
        menu_bar.add_cascade(label="Cài đặt", menu=settings_menu)
        
    def create_status_bar(self):
        status_frame = ttk.Frame(self, padding=(2, 4)); status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_label = ttk.Label(status_frame, text="Sẵn sàng", anchor='w'); self.status_label.pack(fill=tk.X)

    def _has_unsaved_changes(self) -> bool:
        if self.editor_widget and self.initial_content is not None:
            return self.editor_widget.get("1.0", "end-1c") != self.initial_content
        return False

    def _prompt_if_unsaved_changes(self) -> bool:
        if self._has_unsaved_changes():
            file_name = os.path.basename(self._get_display_name(self.editing_file_path))
            response = messagebox.askyesnocancel("Thay đổi chưa được lưu", f"Bạn có muốn lưu các thay đổi cho file '{file_name}' không?", parent=self)
            if response is True: return self.save_current_file()
            if response is False: return True
            return False
        return True

    def save_current_file(self) -> bool:
        if not self.editing_file_path or not self.editor_widget: return False
        current_content = self.editor_widget.get("1.0", "end-1c")
        if current_content == self.initial_content: return True
        try:
            with open(self.editing_file_path, "w", encoding="utf-8") as f: f.write(current_content)
            self.initial_content = current_content
            self.status_label.config(text=f"Đã lưu file: {os.path.basename(self._get_display_name(self.editing_file_path))}")
            self.populate_view(self.current_path)
            return True
        except Exception as e:
            messagebox.showerror("Lỗi Lưu File", f"Không thể lưu file:\n{e}"); return False

    def on_close_window(self):
        if self._prompt_if_unsaved_changes():
            self.settings['geometry'] = self.winfo_geometry()
            self._save_settings()
            self.quit()

    def populate_view(self, path: str):
        abs_path = os.path.abspath(path)
        if abs_path != self.current_path and not self._prompt_if_unsaved_changes():
            self.address_bar.delete(0, tk.END); self.address_bar.insert(0, self.current_path); return
        
        selected_path = self._get_path_from_item_id(self.item_view.selection()[0]) if self.item_view.selection() else None
        for item in self.item_view.get_children(): self.item_view.delete(item)

        try:
            self.current_path = abs_path
            self.address_bar.delete(0, tk.END); self.address_bar.insert(0, self.current_path)
            is_root = os.path.normpath(self.current_path) == os.path.normpath(AppConfig.ROOT_DIR)
            self.up_button.config(state=tk.DISABLED if is_root else tk.NORMAL)
            items = sorted(os.listdir(self.current_path), key=lambda x: (not os.path.isdir(os.path.join(self.current_path, x)), x.lower()))
            for item_name in items:
                item_path = os.path.join(self.current_path, item_name)
                try:
                    stats = os.stat(item_path)
                    size = self._format_size(stats.st_size) if not os.path.isdir(item_path) else ""
                    mod_time = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M')
                    display_name = self._get_display_name(item_name)
                    symbol = self._get_item_symbol(item_name)
                    lock_icon = f" {AppConfig.ICON_LOCKED}" if self._is_path_locked(item_name) else ""
                    item_id = self.item_view.insert(
                        "", "end",
                        text=f" {symbol} {display_name}{lock_icon}",
                        values=(self._get_file_type_description(item_name), size, mod_time),
                        tags=(item_path,)
                    )
                    if item_path == selected_path:
                        self.item_view.selection_set(item_id); self.item_view.focus(item_id)
                except FileNotFoundError: continue
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể truy cập thư mục: {e}"); self.go_up()

    def go_up(self):
        if not self._prompt_if_unsaved_changes(): return
        parent_dir = os.path.dirname(self.current_path)
        if os.path.normpath(parent_dir) != os.path.normpath(self.current_path) and parent_dir.startswith(os.path.normpath(AppConfig.ROOT_DIR)):
            self.populate_view(parent_dir)

    def on_item_select(self, event=None):
        selected_items = self.item_view.selection()
        def _revert_selection():
            for item_id in self.item_view.get_children():
                if self._get_path_from_item_id(item_id) == self.editing_file_path:
                    self.item_view.selection_set(item_id); break
        
        if not selected_items:
            if self.editing_file_path and not self._prompt_if_unsaved_changes():
                _revert_selection(); return
            self._clear_content_frame(); return
        
        path = self._get_path_from_item_id(selected_items[0])
        if path != self.editing_file_path and not self._prompt_if_unsaved_changes():
            _revert_selection(); return
        self.status_label.config(text=f"Đã chọn: {path}"); self.display_content_preview(path)

    def on_double_click(self, event):
        selected_items = self.item_view.selection()
        if not selected_items: return
        path = self._get_path_from_item_id(selected_items[0])
        if os.path.isdir(path):
            if self._is_path_locked(path):
                messagebox.showinfo("Bị khóa", "Không thể vào thư mục đã bị khóa."); return
            if not self._prompt_if_unsaved_changes(): return
            self.populate_view(path)
        else: self.open_item_externally(path)

    def _clear_content_frame(self):
        for widget in self.content_frame.winfo_children(): widget.destroy()
        self.editing_file_path = None; self.initial_content = None; self.editor_widget = None
        for key in self.image_viewer_data: self.image_viewer_data[key] = None if key != 'zoom_level' else 1.0
        if self.pdf_viewer_data.get("doc"): self.pdf_viewer_data["doc"].close()
        for key in self.pdf_viewer_data:
            if key in ["current_page", "total_pages"]:
                self.pdf_viewer_data[key] = 0
            elif key == "zoom_level":
                self.pdf_viewer_data[key] = 1.0
            elif key == "image_pos":
                 self.pdf_viewer_data[key] = [0, 0]
            else:
                self.pdf_viewer_data[key] = None

    def display_content_preview(self, path: str):
        self._clear_content_frame()
        self.editing_file_path = path; is_locked = self._is_path_locked(path)
        display_name = self._get_display_name(os.path.basename(path))

        if os.path.isdir(path): self._display_directory_info(display_name, path); return

        file_ext = os.path.splitext(display_name)[1].lower()
        if file_ext in (AppConfig.LINK_EXT, AppConfig.TODO_EXT):
            self._display_special_file(display_name, path, is_locked)
        elif file_ext == AppConfig.PDF_EXT and PYMUPDF_AVAILABLE:
            self._display_pdf_preview(display_name, path, is_locked)
        elif file_ext in AppConfig.IMAGE_EXTS and PIL_AVAILABLE:
            self._display_image_preview(display_name, path, is_locked)
        elif file_ext in AppConfig.MARKDOWN_EXTS:
            self._display_markdown_preview(display_name, path, is_locked)
        else: self._display_text_editor(display_name, path, is_locked)
    
    def _display_directory_info(self, name: str, path: str):
        self.editing_file_path = None
        ttk.Label(self.content_frame, text=f"Thư mục: {name}", font=("Segoe UI", 14, "bold")).pack(anchor='w', padx=10, pady=10)
        try:
            num_items = len(os.listdir(path))
            ttk.Label(self.content_frame, text=f"Chứa {num_items} mục.", font=AppConfig.FONT_UI_REGULAR).pack(anchor='w', padx=10)
        except OSError:
            ttk.Label(self.content_frame, text="Không thể truy cập nội dung.", foreground="red").pack(anchor='w', padx=10)

    def _display_special_file(self, display_name: str, path: str, is_locked: bool):
        ext = os.path.splitext(path)[1].lower()
        ManagerClass = LinkManager if ext == AppConfig.LINK_EXT else TodoManager
        manager_widget = ManagerClass(self.content_frame, path, display_name, self.style, is_locked)
        manager_widget.pack(fill=tk.BOTH, expand=True)

    def _display_text_editor(self, display_name: str, path: str, is_locked: bool):
        editor_toolbar = ttk.Frame(self.content_frame); editor_toolbar.pack(fill=tk.X, padx=10, pady=(10, 5))
        ttk.Label(editor_toolbar, text=f"File: {display_name}", font=("Segoe UI", 12)).pack(side=tk.LEFT)
        if not is_locked:
            ttk.Button(editor_toolbar, text="Lưu", command=self.save_current_file).pack(side=tk.RIGHT, padx=2)
        ttk.Separator(self.content_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=5)
        
        editor_frame = ttk.Frame(self.content_frame)
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.editor_widget = tk.Text(editor_frame, wrap=tk.WORD, undo=True, bg=self.style.lookup('Treeview', 'background'), 
                                     fg=self.style.lookup('TLabel', 'foreground'), insertbackground=self.style.lookup('TLabel', 'foreground'),
                                     borderwidth=0, highlightthickness=0, font=AppConfig.FONT_EDITOR)
        scrollbar = ttk.Scrollbar(editor_frame, command=self.editor_widget.yview)
        self.editor_widget['yscrollcommand'] = scrollbar.set
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y); self.editor_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        try:
            with open(path, 'r', encoding='utf-8') as f: self.initial_content = f.read()
        except UnicodeDecodeError:
            self.initial_content = "[File nhị phân hoặc mã hóa không được hỗ trợ.]"; is_locked = True
        except Exception as e:
            self.initial_content = f"[Lỗi khi đọc file: {e}]"; is_locked = True
        
        self.editor_widget.insert('1.0', self.initial_content)
        if is_locked: self.editor_widget.config(state=tk.DISABLED)

    def _display_pdf_preview(self, display_name, path, is_locked):
        try:
            doc = fitz.open(path)
            self.pdf_viewer_data["doc"] = doc
            self.pdf_viewer_data["total_pages"] = len(doc)
        except Exception as e:
            ttk.Label(self.content_frame, text=f"Lỗi mở file PDF: {e}", foreground="red").pack(padx=10, pady=10)
            return

        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Toolbar ---
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        self.pdf_viewer_data["prev_button"] = ttk.Button(toolbar, text="⬅ Trang trước", command=lambda: self._navigate_pdf(-1))
        self.pdf_viewer_data["prev_button"].pack(side=tk.LEFT)
        self.pdf_viewer_data["page_label"] = ttk.Label(toolbar, text="Trang X / Y", anchor=tk.CENTER)
        self.pdf_viewer_data["page_label"].pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.pdf_viewer_data["next_button"] = ttk.Button(toolbar, text="Trang sau ➡", command=lambda: self._navigate_pdf(1))
        self.pdf_viewer_data["next_button"].pack(side=tk.RIGHT)

        # --- Canvas ---
        canvas = tk.Canvas(main_frame, background=self.style.lookup('Treeview', 'background'), highlightthickness=0)
        self.pdf_viewer_data["canvas"] = canvas
        canvas.pack(fill=tk.BOTH, expand=True)

        # --- Control Frame ---
        ctl_frame = ttk.Frame(main_frame)
        ctl_frame.pack(fill=tk.X, pady=(4, 0))
        ttk.Button(ctl_frame, text="+", width=3, command=lambda: self._zoom_pdf(1.25)).pack(side=tk.RIGHT, padx=2)
        ttk.Button(ctl_frame, text="-", width=3, command=lambda: self._zoom_pdf(0.8)).pack(side=tk.RIGHT)
        ttk.Button(ctl_frame, text="Fit", command=self._fit_pdf_to_canvas).pack(side=tk.RIGHT, padx=6)
        ttk.Button(ctl_frame, text="Reset", command=self._reset_pdf_zoom).pack(side=tk.RIGHT)
        
        info_label = ttk.Label(main_frame, text="", font=("Segoe UI", 9), anchor='w', justify='left')
        self.pdf_viewer_data['info_label'] = info_label
        info_label.pack(fill=tk.X, pady=(4, 0))

        # --- Event Bindings ---
        canvas.bind("<MouseWheel>", self._on_pdf_mousewheel)
        canvas.bind("<Button-4>", self._on_pdf_mousewheel) # Linux scroll up
        canvas.bind("<Button-5>", self._on_pdf_mousewheel) # Linux scroll down
        canvas.bind("<ButtonPress-1>", self._on_pdf_drag_start)
        canvas.bind("<B1-Motion>", self._on_pdf_drag_move)
        canvas.bind("<ButtonRelease-1>", self._on_pdf_drag_end)
        canvas.bind("<Configure>", lambda e: self._fit_pdf_to_canvas())

        canvas.bind("<Left>", lambda e: self._navigate_pdf(-1))
        canvas.bind("<Right>", lambda e: self._navigate_pdf(1))
        canvas.focus_set()

        self._fit_pdf_to_canvas()

    def _fit_pdf_to_canvas(self):
        pdf_data = self.pdf_viewer_data
        if not pdf_data.get("doc") or not pdf_data.get("canvas"): return
        canvas = pdf_data['canvas']
        canvas_w, canvas_h = canvas.winfo_width(), canvas.winfo_height()
        if canvas_w <= 1 or canvas_h <= 1:
            self.after(50, self._fit_pdf_to_canvas)
            return

        page = pdf_data["doc"].load_page(pdf_data["current_page"])
        page_w, page_h = page.rect.width, page.rect.height

        scale = min(canvas_w / page_w, canvas_h / page_h)
        pdf_data['zoom_level'] = scale
        
        new_w, new_h = int(page_w * scale), int(page_h * scale)
        pdf_data['image_pos'] = [max((canvas_w - new_w) // 2, 0), max((canvas_h - new_h) // 2, 0)]
        self._render_pdf_page()

    def _reset_pdf_zoom(self):
        self._fit_pdf_to_canvas() # Fit is a good reset state
        # Or alternatively, to reset to 100% real size:
        # pdf_data = self.pdf_viewer_data
        # pdf_data['zoom_level'] = 1.0 
        # # Center it
        # canvas = pdf_data['canvas']
        # canvas_w, canvas_h = canvas.winfo_width(), canvas.winfo_height()
        # page = pdf_data["doc"].load_page(pdf_data["current_page"])
        # page_w, page_h = page.rect.width, page.rect.height
        # pdf_data['image_pos'] = [(canvas_w - page_w) // 2, (canvas_h - page_h) // 2]
        # self._render_pdf_page()

    def _zoom_pdf(self, factor, center=None):
        pdf_data = self.pdf_viewer_data
        if not pdf_data.get("doc") or not pdf_data.get("canvas"): return
        
        old_zoom = pdf_data['zoom_level']
        new_zoom = max(0.1, min(old_zoom * factor, 10.0)) # Cap zoom level
        if abs(new_zoom - old_zoom) < 1e-6: return

        canvas = pdf_data['canvas']
        if center is None:
            center = (canvas.winfo_width() // 2, canvas.winfo_height() // 2)
        
        # Pan to keep the point under the cursor stable
        img_point_x = (center[0] - pdf_data['image_pos'][0]) / old_zoom
        img_point_y = (center[1] - pdf_data['image_pos'][1]) / old_zoom
        
        pdf_data['zoom_level'] = new_zoom
        pdf_data['image_pos'][0] = center[0] - img_point_x * new_zoom
        pdf_data['image_pos'][1] = center[1] - img_point_y * new_zoom
        
        self._render_pdf_page()

    def _on_pdf_mousewheel(self, event):
        factor = 1.1 if (event.delta > 0 if hasattr(event, 'delta') else str(event.num) == '4') else 0.9
        self._zoom_pdf(factor, center=(event.x, event.y))
        return "break"

    def _on_pdf_drag_start(self, event):
        self.pdf_viewer_data['drag_start'] = (event.x, event.y)
        self.pdf_viewer_data['canvas'].config(cursor="fleur")

    def _on_pdf_drag_end(self, event):
        self.pdf_viewer_data['drag_start'] = None
        self.pdf_viewer_data['canvas'].config(cursor="")

    def _on_pdf_drag_move(self, event):
        pdf_data, ds = self.pdf_viewer_data, self.pdf_viewer_data['drag_start']
        if not ds or not pdf_data['canvas_page_id']: return
        
        dx, dy = event.x - ds[0], event.y - ds[1]
        pdf_data['image_pos'][0] += dx
        pdf_data['image_pos'][1] += dy
        
        pdf_data['canvas'].move(pdf_data['canvas_page_id'], dx, dy)
        self.pdf_viewer_data['drag_start'] = (event.x, event.y)
        
    def _navigate_pdf(self, delta: int):
        pdf_data = self.pdf_viewer_data
        new_page = pdf_data["current_page"] + delta
        if pdf_data["doc"] and 0 <= new_page < pdf_data["total_pages"]:
            pdf_data["current_page"] = new_page
            # Reset zoom and fit the new page to the canvas
            self._fit_pdf_to_canvas()

    def _render_pdf_page(self):
        pdf_data = self.pdf_viewer_data
        if not pdf_data.get("doc") or not pdf_data.get("canvas"):
            return

        page_num = pdf_data["current_page"]
        page = pdf_data["doc"].load_page(page_num)
        
        # Render page using a zoom matrix for better quality
        mat = fitz.Matrix(pdf_data["zoom_level"], pdf_data["zoom_level"])
        pix = page.get_pixmap(matrix=mat, alpha=False)
        
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        pdf_data["photo_image"] = ImageTk.PhotoImage(image=img)
        
        canvas = pdf_data["canvas"]
        canvas.delete("all") # Clear previous content
        
        pdf_data["canvas_page_id"] = canvas.create_image(
            *pdf_data["image_pos"], anchor='nw', image=pdf_data["photo_image"], tags="PDF_PAGE"
        )
        canvas.config(scrollregion=canvas.bbox("all"))

        # Update labels and buttons
        pdf_data["page_label"].config(text=f"Trang {page_num + 1} / {pdf_data['total_pages']}")
        pdf_data["prev_button"].config(state=tk.NORMAL if page_num > 0 else tk.DISABLED)
        pdf_data["next_button"].config(state=tk.NORMAL if page_num < pdf_data["total_pages"] - 1 else tk.DISABLED)
        if pdf_data['info_label']:
            page_rect = page.rect
            info = f"Kích thước gốc: {page_rect.width:.0f}x{page_rect.height:.0f}pt | Hiển thị: {pix.width}x{pix.height}px ({pdf_data['zoom_level']*100:.0f}%)"
            pdf_data['info_label'].config(text=info)

    def _display_image_preview(self, display_name, path, is_locked):
        preview_frame = ttk.Frame(self.content_frame); preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        try:
            img = Image.open(path)
            if getattr(img, "is_animated", False): img.seek(0)
            self.image_viewer_data['original_image'] = img.convert("RGBA") if img.mode != 'RGBA' else img.copy()
        except Exception as e:
            ttk.Label(preview_frame, text=f"[Không thể mở ảnh: {e}]").pack(); return
        
        canvas = tk.Canvas(preview_frame, background=self.style.lookup('Treeview', 'background'), highlightthickness=0)
        self.image_viewer_data['canvas'] = canvas; canvas.pack(fill=tk.BOTH, expand=True)

        ctl_frame = ttk.Frame(preview_frame); ctl_frame.pack(fill=tk.X, pady=(4,0))
        ttk.Button(ctl_frame, text="+", width=3, command=lambda: self._zoom_image(1.25)).pack(side=tk.RIGHT, padx=2)
        ttk.Button(ctl_frame, text="-", width=3, command=lambda: self._zoom_image(0.8)).pack(side=tk.RIGHT)
        ttk.Button(ctl_frame, text="Fit", command=self._fit_image_to_canvas).pack(side=tk.RIGHT, padx=6)
        ttk.Button(ctl_frame, text="Reset", command=lambda: self._zoom_image(1.0 / self.image_viewer_data['zoom_level'])).pack(side=tk.RIGHT)
        
        info_label = ttk.Label(preview_frame, text="", font=("Segoe UI", 9), anchor='w', justify='left')
        self.image_viewer_data['info_label'] = info_label; info_label.pack(fill=tk.X, pady=(4,0))
        
        open_state = tk.DISABLED if is_locked else tk.NORMAL
        ttk.Button(preview_frame, text="Mở ngoài", command=lambda p=path: self.open_item_externally(p), state=open_state).pack(side=tk.RIGHT, pady=(6,0))

        canvas.bind("<MouseWheel>", self._on_image_mousewheel); canvas.bind("<Button-4>", self._on_image_mousewheel)
        canvas.bind("<Button-5>", self._on_image_mousewheel); canvas.bind("<ButtonPress-1>", self._on_image_drag_start)
        canvas.bind("<B1-Motion>", self._on_image_drag_move); canvas.bind("<ButtonRelease-1>", self._on_image_drag_end)
        canvas.bind("<Configure>", lambda e: self._fit_image_to_canvas())

    def _update_canvas_image(self):
        img_data = self.image_viewer_data
        if not img_data['original_image'] or not img_data['canvas']: return

        canvas = img_data['canvas']; orig_w, orig_h = img_data['original_image'].size
        zoom = img_data['zoom_level']; new_w, new_h = max(1, int(orig_w * zoom)), max(1, int(orig_h * zoom))
        try: resample = Image.Resampling.LANCZOS
        except AttributeError: resample = Image.ANTIALIAS
        resized_img = img_data['original_image'].resize((new_w, new_h), resample)

        img_data['displayed_image'] = ImageTk.PhotoImage(resized_img); canvas.delete("IMG_TAG")
        img_data['canvas_image_id'] = canvas.create_image(*img_data['image_pos'], image=img_data['displayed_image'], anchor='nw', tags="IMG_TAG")
        canvas.config(scrollregion=(0, 0, new_w, new_h))

        if img_data['info_label']:
            fmt = getattr(img_data['original_image'], "format", "N/A")
            info = f"Kích thước gốc: {orig_w}x{orig_h}px | Hiển thị: {new_w}x{new_h}px ({zoom*100:.0f}%) | Định dạng: {fmt}"
            img_data['info_label'].config(text=info)

    def _fit_image_to_canvas(self):
        img_data = self.image_viewer_data
        if not img_data['original_image'] or not img_data['canvas']: return
        canvas = img_data['canvas']; canvas_w, canvas_h = canvas.winfo_width(), canvas.winfo_height()
        if canvas_w <= 1 or canvas_h <= 1: self.after(50, self._fit_image_to_canvas); return

        img_w, img_h = img_data['original_image'].size; scale = min(canvas_w / img_w, canvas_h / img_h, 1.0)
        img_data['zoom_level'] = scale
        new_w, new_h = int(img_w * scale), int(img_h * scale)
        img_data['image_pos'] = [max((canvas_w - new_w) // 2, 0), max((canvas_h - new_h) // 2, 0)]
        self._update_canvas_image()

    def _zoom_image(self, factor, center=None):
        img_data = self.image_viewer_data
        if not img_data['original_image'] or not img_data['canvas']: return
        old_zoom = img_data['zoom_level']; new_zoom = max(0.05, min(old_zoom * factor, 15.0))
        if abs(new_zoom - old_zoom) < 1e-6: return

        canvas = img_data['canvas']
        if center is None: center = (canvas.winfo_width() // 2, canvas.winfo_height() // 2)
        img_point_x = (center[0] - img_data['image_pos'][0]) / old_zoom
        img_point_y = (center[1] - img_data['image_pos'][1]) / old_zoom
        img_data['zoom_level'] = new_zoom
        img_data['image_pos'][0] = center[0] - img_point_x * new_zoom
        img_data['image_pos'][1] = center[1] - img_point_y * new_zoom
        self._update_canvas_image()

    def _on_image_mousewheel(self, event):
        factor = 1.1 if (event.delta > 0 if hasattr(event, 'delta') else str(event.num) == '4') else 0.9
        self._zoom_image(factor, center=(event.x, event.y))

    def _on_image_drag_start(self, event): self.image_viewer_data['drag_start'] = (event.x, event.y)
    def _on_image_drag_end(self, event): self.image_viewer_data['drag_start'] = None
    def _on_image_drag_move(self, event):
        img_data, ds = self.image_viewer_data, self.image_viewer_data['drag_start']
        if not ds or not img_data['canvas_image_id']: return
        dx, dy = event.x - ds[0], event.y - ds[1]
        img_data['image_pos'][0] += dx; img_data['image_pos'][1] += dy
        img_data['canvas'].move(img_data['canvas_image_id'], dx, dy)
        self.image_viewer_data['drag_start'] = (event.x, event.y)

    def _display_markdown_preview(self, display_name, path, is_locked):
        is_render_mode = self.markdown_view_modes.get(path, MARKDOWN_LIBS_AVAILABLE)
        toolbar = ttk.Frame(self.content_frame); toolbar.pack(fill=tk.X, padx=10, pady=(10, 5))
        ttk.Label(toolbar, text=f"Markdown: {display_name}", font=("Segoe UI", 12)).pack(side=tk.LEFT)
        toggle_text = "Chỉnh sửa" if is_render_mode else "Xem trước"
        ttk.Button(toolbar, text=toggle_text, command=lambda p=path: self.toggle_markdown_view(p)).pack(side=tk.RIGHT)
        if not is_render_mode and not is_locked:
            ttk.Button(toolbar, text="Khôi phục", command=self.revert_current_file).pack(side=tk.RIGHT, padx=4)
            ttk.Button(toolbar, text="Lưu", command=self.save_current_file).pack(side=tk.RIGHT, padx=4)
        ttk.Separator(self.content_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=5)
        if is_render_mode and MARKDOWN_LIBS_AVAILABLE:
            preview_frame = ttk.Frame(self.content_frame); preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
            try:
                with open(path, 'r', encoding='utf-8') as f: md_content = f.read()
                self.initial_content = md_content
                html_content = markdown2.markdown(md_content, extras=["fenced-code-blocks", "tables", "spoiler", "break-on-newline", "task_list"])
                html_view = HTMLLabel(preview_frame, html=html_content, background=self.style.lookup('Treeview', 'background'), 
                                      foreground=self.style.lookup('TLabel', 'foreground'), link_color=AppConfig.COLOR_SELECTED_ITEM)
                scrollbar = ttk.Scrollbar(preview_frame, orient="vertical", command=html_view.yview)
                html_view.configure(yscrollcommand=scrollbar.set)
                scrollbar.pack(side="right", fill="y"); html_view.pack(side=tk.LEFT, fill="both", expand=True)
            except Exception as e: self._display_text_editor(display_name, path, is_locked)
        else: self._display_text_editor(display_name, path, is_locked)

    def toggle_markdown_view(self, path):
        if not path or not path.lower().endswith(AppConfig.MARKDOWN_EXTS): return
        if not self.markdown_view_modes.get(path, MARKDOWN_LIBS_AVAILABLE) and not self._prompt_if_unsaved_changes(): return
        self.markdown_view_modes[path] = not self.markdown_view_modes.get(path, MARKDOWN_LIBS_AVAILABLE)
        self.display_content_preview(path)

    def revert_current_file(self):
        if not self.editing_file_path or not self.editor_widget: return
        try:
            with open(self.editing_file_path, 'r', encoding='utf-8') as f: content = f.read()
            self.editor_widget.config(state=tk.NORMAL); self.editor_widget.delete("1.0", "end")
            self.editor_widget.insert("1.0", content); self.initial_content = content
            self.status_label.config(text="Đã khôi phục nội dung từ file.")
        except Exception as e: messagebox.showerror("Lỗi", f"Không thể khôi phục: {e}")

    def show_context_menu(self, event):
        item_id = self.item_view.identify_row(event.y); context_menu = tk.Menu(self, tearoff=0)
        if item_id:
            if not self._prompt_if_unsaved_changes(): return
            self.item_view.selection_set(item_id)
            path = self._get_path_from_item_id(item_id); is_locked = self._is_path_locked(path)
            action_state = tk.DISABLED if is_locked else tk.NORMAL
            if not os.path.isdir(path): context_menu.add_command(label="Mở ngoài", command=lambda p=path: self.open_item_externally(p), font=AppConfig.FONT_UI_BOLD)
            if is_locked: context_menu.add_command(label=f"🔓 Mở khóa", command=lambda p=path: self.unlock_item(p))
            else: context_menu.add_command(label=f"🔒 Khóa", command=lambda p=path: self.lock_item(p))
            context_menu.add_separator()
            context_menu.add_command(label="Sao chép", accelerator="Ctrl+C", command=lambda p=path: self.copy_item(p))
            context_menu.add_command(label="Cắt", accelerator="Ctrl+X", command=lambda p=path: self.cut_item(p), state=action_state)
            context_menu.add_command(label="Xóa", command=lambda p=path: self.delete_item(p), state=action_state)
            context_menu.add_command(label="Đổi tên...", command=lambda p=path: self.rename_item(p), state=action_state)
            context_menu.add_command(label="Di chuyển tới...", command=lambda p=path: self.move_item_dialog(p), state=action_state)
            context_menu.add_separator()
        dest_dir = self.current_path; is_dest_locked = self._is_path_locked(dest_dir)
        paste_state = tk.NORMAL if self.clipboard_path and not is_dest_locked else tk.DISABLED
        create_state = tk.DISABLED if is_dest_locked else tk.NORMAL
        context_menu.add_command(label="Dán", accelerator="Ctrl+V", command=lambda: self.paste_item(dest_dir), state=paste_state)
        create_menu = tk.Menu(context_menu, tearoff=0)
        create_menu.add_command(label="Thư mục", command=lambda: self.create_folder(dest_dir), state=create_state)
        create_menu.add_separator()
        create_menu.add_command(label="Tệp Liên kết (.link)", command=lambda: self.create_file(dest_dir, AppConfig.LINK_EXT), state=create_state)
        create_menu.add_command(label="Danh sách Công việc (.todo)", command=lambda: self.create_file(dest_dir, AppConfig.TODO_EXT), state=create_state)
        create_menu.add_command(label="Tệp Văn bản (.txt)", command=lambda: self.create_file(dest_dir, AppConfig.TEXT_EXT), state=create_state)
        create_menu.add_command(label="Tệp Markdown (.md)", command=lambda: self.create_file(dest_dir, AppConfig.MARKDOWN_EXTS[0]), state=create_state)
        context_menu.add_cascade(label="Tạo mới", menu=create_menu, state=create_state)
        context_menu.post(event.x_root, event.y_root)

    def lock_item(self, path):
        if path == self.editing_file_path and self._has_unsaved_changes():
            messagebox.showwarning("Hành động bị chặn", "Không thể khóa file đang có thay đổi chưa được lưu."); return
        if not path.endswith(AppConfig.LOCKED_SUFFIX):
            try: os.rename(path, path + AppConfig.LOCKED_SUFFIX); self.populate_view(self.current_path)
            except Exception as e: messagebox.showerror("Lỗi", f"Không thể khóa: {e}")
    def unlock_item(self, path):
        if path.endswith(AppConfig.LOCKED_SUFFIX):
            new_path = self._get_display_name(path)
            try: os.rename(path, new_path); self.populate_view(self.current_path); self.after(100, lambda: self.display_content_preview(new_path))
            except Exception as e: messagebox.showerror("Lỗi", f"Không thể mở khóa: {e}")
    def copy_item(self, path): self.clipboard_path = path; self.clipboard_operation = 'copy'; self.status_label.config(text=f"Đã sao chép: {os.path.basename(self._get_display_name(path))}")
    def cut_item(self, path):
        if path == self.editing_file_path and self._has_unsaved_changes():
            messagebox.showwarning("Hành động bị chặn", "Không thể cắt file đang có thay đổi chưa được lưu."); return
        self.clipboard_path = path; self.clipboard_operation = 'cut'; self.status_label.config(text=f"Đã cắt: {os.path.basename(self._get_display_name(path))}")
    def paste_item(self, dest_dir):
        if not self._prompt_if_unsaved_changes(): return
        if not self.clipboard_path or not os.path.exists(self.clipboard_path): return
        dest_path = os.path.join(dest_dir, os.path.basename(self.clipboard_path))
        if os.path.normpath(dest_path) == os.path.normpath(self.clipboard_path): return
        try:
            if self.clipboard_operation == 'cut':
                shutil.move(self.clipboard_path, dest_path)
                if self.clipboard_path == self.editing_file_path: self.editing_file_path = dest_path
            elif os.path.isdir(self.clipboard_path): shutil.copytree(self.clipboard_path, dest_path, dirs_exist_ok=True)
            else: shutil.copy2(self.clipboard_path, dest_path)
            self.clipboard_path, self.clipboard_operation = None, None; self.populate_view(self.current_path)
        except Exception as e: messagebox.showerror("Lỗi Dán", f"Không thể dán: {e}")
    def rename_item(self, path):
        old_name = os.path.basename(self._get_display_name(path))
        new_name = simpledialog.askstring("Đổi tên", "Nhập tên mới:", initialvalue=old_name)
        if new_name and new_name != old_name:
            new_path = os.path.join(os.path.dirname(path), new_name)
            if self._is_path_locked(path): new_path += AppConfig.LOCKED_SUFFIX
            try: 
                os.rename(path, new_path)
                if path == self.editing_file_path: self.editing_file_path = new_path
                self.populate_view(self.current_path)
            except Exception as e: messagebox.showerror("Lỗi", f"Không thể đổi tên: {e}")
    def delete_item(self, path):
        if messagebox.askyesno("Xác nhận", f"Xóa '{os.path.basename(self._get_display_name(path))}'?"):
            try:
                if os.path.isdir(path): shutil.rmtree(path)
                else: os.remove(path)
                if path == self.editing_file_path: self._clear_content_frame()
                self.populate_view(self.current_path)
            except Exception as e: messagebox.showerror("Lỗi", f"Không thể xóa: {e}")
    def move_item_dialog(self, source_path):
        if not self._prompt_if_unsaved_changes(): return
        dest_dir = filedialog.askdirectory(parent=self, title="Chọn thư mục đích", initialdir=AppConfig.ROOT_DIR)
        if dest_dir and os.path.abspath(dest_dir).startswith(os.path.abspath(AppConfig.ROOT_DIR)):
            if self._is_path_locked(dest_dir):
                messagebox.showwarning("Bị khóa", "Không thể di chuyển vào thư mục đã bị khóa."); return
            try:
                shutil.move(source_path, dest_dir)
                if source_path == self.editing_file_path: self.editing_file_path = os.path.join(dest_dir, os.path.basename(source_path))
                self.populate_view(self.current_path)
            except Exception as e: messagebox.showerror("Lỗi di chuyển", f"{e}")
    def create_folder(self, parent_dir):
        if not self._prompt_if_unsaved_changes(): return
        name = simpledialog.askstring("Tạo Thư mục", "Nhập tên:")
        if name:
            try: os.makedirs(os.path.join(parent_dir, name)); self.populate_view(self.current_path)
            except Exception as e: messagebox.showerror("Lỗi", f"Không thể tạo: {e}")
    def create_file(self, parent_dir, extension):
        if not self._prompt_if_unsaved_changes(): return
        prompts = { ".link": "Tạo Tệp Liên kết", ".todo": "Tạo Danh sách Công việc", ".txt": "Tạo Tệp Văn bản", ".md": "Tạo Tệp Markdown"}
        title = prompts.get(extension, "Tạo Tệp mới")
        file_name = simpledialog.askstring(title, f"Nhập tên tệp (không cần {extension}):")
        if file_name:
            new_path = os.path.join(parent_dir, file_name + extension)
            if os.path.exists(new_path): messagebox.showwarning("Tồn tại", "Tệp đã tồn tại."); return
            try:
                with open(new_path, 'w', encoding='utf-8') as f:
                    if extension in [".link", ".todo"]: json.dump([], f)
                self.populate_view(self.current_path)
            except Exception as e: messagebox.showerror("Lỗi", f"Không thể tạo tệp: {e}")
    def _get_path_from_item_id(self, item_id) -> str: return self.item_view.item(item_id, "tags")[0]
    def _is_path_locked(self, path: str) -> bool: return path.endswith(AppConfig.LOCKED_SUFFIX)
    def _get_display_name(self, path: str) -> str: return path[:-len(AppConfig.LOCKED_SUFFIX)] if self._is_path_locked(path) else path
    def _format_size(self, size_bytes: int) -> str:
        if size_bytes == 0: return "0 B"
        import math
        p = int(math.floor(math.log(size_bytes, 1024))) if size_bytes > 0 else 0
        return f"{size_bytes / (1024**p):.1f} {('B', 'KB', 'MB', 'GB', 'TB')[p]}"
    def _get_item_symbol(self, item_name: str) -> str:
        display_name = self._get_display_name(item_name)
        if os.path.isdir(os.path.join(self.current_path, item_name)): return AppConfig.ICON_FOLDER
        ext = os.path.splitext(display_name)[1].lower()
        symbol_map = {AppConfig.LINK_EXT: AppConfig.ICON_LINK, AppConfig.TODO_EXT: AppConfig.ICON_TODO, AppConfig.PDF_EXT: AppConfig.ICON_PDF, **{md: AppConfig.ICON_MARKDOWN for md in AppConfig.MARKDOWN_EXTS}}
        return symbol_map.get(ext, AppConfig.ICON_FILE)
    def _get_file_type_description(self, item_name: str) -> str:
        if os.path.isdir(os.path.join(self.current_path, item_name)): return "Thư mục"
        display_name = self._get_display_name(item_name); ext = os.path.splitext(display_name)[1].lower()
        descriptions = {AppConfig.LINK_EXT: "Tệp liên kết", AppConfig.TODO_EXT: "Danh sách công việc", AppConfig.TEXT_EXT: "Tài liệu văn bản", AppConfig.PDF_EXT: "Tài liệu PDF", **{md: "Tài liệu Markdown" for md in AppConfig.MARKDOWN_EXTS}, **{img: "Tệp hình ảnh" for img in AppConfig.IMAGE_EXTS}}
        return descriptions.get(ext, f"Tệp ({ext})" if ext else "Tệp")
    def toggle_theme(self): 
        self.current_theme = 'dark' if self.current_theme == 'light' else 'light'; 
        self.settings['theme'] = self.current_theme
        self._save_settings()
        self.apply_theme()

    def apply_theme(self):
        is_light = self.current_theme == 'light'
        bg, fg, tree_bg = ('#f0f0f0', 'black', 'white') if is_light else ('#333333', 'white', '#444444')
        self.style.theme_use('clam'); self.style.configure('.', background=bg, foreground=fg, font=AppConfig.FONT_UI_REGULAR)
        self.style.configure('TLabel', background=bg, foreground=fg); self.style.configure('TButton', padding=5)
        self.style.configure('TEntry', fieldbackground=tree_bg, foreground=fg, insertcolor=fg)
        self.style.configure('TFrame', background=bg); self.style.configure('Treeview', background=tree_bg, foreground=fg, fieldbackground=tree_bg, rowheight=25, font=AppConfig.FONT_UI_REGULAR)
        self.style.map('Treeview', background=[('selected', AppConfig.COLOR_SELECTED_ITEM)]); self.style.configure('Treeview.Heading', font=AppConfig.FONT_UI_BOLD)
        if self.item_view.selection(): self.on_item_select()
    def open_item_externally(self, path: str):
        if self._is_path_locked(path): messagebox.showinfo("Bị khóa", f"Không thể mở '{os.path.basename(path)}' vì đã bị khóa."); return
        try:
            if sys.platform == "win32": os.startfile(os.path.realpath(path))
            elif sys.platform == "darwin": subprocess.run(["open", path])
            else: subprocess.run(["xdg-open", path])
        except Exception as e: messagebox.showerror("Lỗi", f"Không thể mở mục: {e}")
    def handle_save_shortcut(self, event=None): self.save_current_file(); return "break"
    def handle_copy_shortcut(self, event=None):
        if self.item_view.selection(): self.copy_item(self._get_path_from_item_id(self.item_view.selection()[0]))
    def handle_cut_shortcut(self, event=None):
        if self.item_view.selection(): self.cut_item(self._get_path_from_item_id(self.item_view.selection()[0]))
    def handle_paste_shortcut(self, event=None): self.paste_item(self.current_path)

class LinkManager(ttk.Frame):
    def __init__(self, parent, file_path, display_name, style, is_locked, **kwargs):
        super().__init__(parent, **kwargs)
        self.file_path, self.display_name, self.style, self.is_locked = file_path, display_name, style, is_locked
        self.links_data = []
        self.load_data(); self.create_widgets()
    def load_data(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read(); self.links_data = json.loads(content) if content else []
        except (FileNotFoundError, json.JSONDecodeError): self.links_data = []
    def save_data(self):
        self.links_data.sort(key=lambda x: x['label'].lower())
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.links_data, f, indent=4, ensure_ascii=False)
        self.refresh_list()
    def create_widgets(self):
        lock_symbol = f" {AppConfig.ICON_LOCKED}" if self.is_locked else ""
        ttk.Label(self, text=f"File: {self.display_name}{lock_symbol}", font=("Segoe UI", 14, "bold")).pack(side=tk.TOP, anchor='w', pady=(10, 10), padx=10)
        control_frame = ttk.Frame(self); control_frame.pack(fill=tk.X, pady=5, padx=10)
        btn_state = tk.DISABLED if self.is_locked else tk.NORMAL
        ttk.Button(control_frame, text="Thêm Liên kết", command=self.add_link, state=btn_state).pack(side=tk.RIGHT)
        tree_frame = ttk.Frame(self); tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.tree = ttk.Treeview(tree_frame, columns=("Label", "URL", "Hashtags"), show="headings")
        self.tree.heading("Label", text="Tên"); self.tree.heading("URL", text="URL"); self.tree.heading("Hashtags", text="Hashtags")
        self.tree.column("Label", width=200); self.tree.column("URL", width=300)
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set); scrollbar.pack(side=tk.RIGHT, fill=tk.Y); self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", lambda e: self.open_selected_link()); self.tree.bind("<Button-3>", self.show_context_menu)
        self.refresh_list()
    def refresh_list(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for item in sorted(self.links_data, key=lambda x: x['label'].lower()):
            self.tree.insert("", "end", values=(item["label"], item["url"], ", ".join(item.get("hashtags", []))), iid=item['label'])
    def add_link(self):
        dialog = LinkEditorDialog(self, title="Thêm Liên kết")
        if dialog.result: self.links_data.append(dialog.result); self.save_data()
    def find_link_by_label(self, label): return next((item for item in self.links_data if item['label'] == label), None)
    def open_selected_link(self):
        if self.tree.selection(): webbrowser.open_new_tab(self.find_link_by_label(self.tree.selection()[0])['url'])
    def edit_selected_link(self):
        if not self.tree.selection(): return
        original_data = self.find_link_by_label(self.tree.selection()[0])
        if not original_data: return
        dialog = LinkEditorDialog(self, title="Sửa Liên kết", initial_data=original_data)
        if dialog.result: original_data.update(dialog.result); self.save_data()
    def delete_selected_link(self):
        if not self.tree.selection(): return
        label_to_delete = self.tree.selection()[0]
        if messagebox.askyesno("Xác nhận Xóa", f"Bạn có chắc muốn xóa liên kết '{label_to_delete}' không?", parent=self):
            self.links_data = [item for item in self.links_data if item['label'] != label_to_delete]; self.save_data()
    def show_context_menu(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id: return
        self.tree.selection_set(item_id)
        context_menu = tk.Menu(self, tearoff=0); action_state = tk.DISABLED if self.is_locked else tk.NORMAL
        context_menu.add_command(label="Mở trong Trình duyệt", command=self.open_selected_link, font=AppConfig.FONT_UI_BOLD)
        context_menu.add_separator()
        context_menu.add_command(label="Sửa Liên kết...", command=self.edit_selected_link, state=action_state)
        context_menu.add_command(label="Xóa Liên kết", command=self.delete_selected_link, state=action_state)
        context_menu.post(event.x_root, event.y_root)

class LinkEditorDialog(simpledialog.Dialog):
    def __init__(self, parent, title=None, initial_data=None):
        self.initial_data = initial_data or {}; super().__init__(parent, title)
    def body(self, master):
        ttk.Label(master, text="Tên hiển thị:").grid(row=0, sticky=tk.W, pady=2)
        ttk.Label(master, text="URL:").grid(row=1, sticky=tk.W, pady=2)
        ttk.Label(master, text="Hashtags (phẩy cách):").grid(row=2, sticky=tk.W, pady=2)
        self.label_entry = ttk.Entry(master, width=50); self.url_entry = ttk.Entry(master, width=50)
        self.hashtags_entry = ttk.Entry(master, width=50)
        self.label_entry.grid(row=0, column=1, padx=5, pady=2); self.url_entry.grid(row=1, column=1, padx=5, pady=2)
        self.hashtags_entry.grid(row=2, column=1, padx=5, pady=2)
        self.label_entry.insert(0, self.initial_data.get("label", "")); self.url_entry.insert(0, self.initial_data.get("url", "https://"))
        self.hashtags_entry.insert(0, ", ".join(self.initial_data.get("hashtags", []))); return self.label_entry
    def validate(self):
        if not self.label_entry.get().strip() or not self.url_entry.get().strip():
            messagebox.showwarning("Thiếu thông tin", "Tên hiển thị và URL là bắt buộc.", parent=self); return 0
        return 1
    def apply(self):
        label = self.label_entry.get().strip(); url = self.url_entry.get().strip()
        if not url.startswith(('http://', 'https://', 'file://')) and '://' not in url: url = 'http://' + url
        hashtags = [h.strip() for h in self.hashtags_entry.get().strip().split(',') if h.strip()]
        self.result = {"label": label, "url": url, "hashtags": hashtags}

class TodoManager(ttk.Frame):
    def __init__(self, parent, file_path, display_name, style, is_locked, **kwargs):
        super().__init__(parent, **kwargs)
        self.file_path, self.display_name, self.style, self.is_locked = file_path, display_name, style, is_locked
        self.tasks = []; self.task_widgets_map = {}; self.load_tasks(); self.create_widgets()
    def load_tasks(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read(); self.tasks = json.loads(content) if content else []
        except (FileNotFoundError, json.JSONDecodeError): self.tasks = []
    def save_tasks(self):
        with open(self.file_path, 'w', encoding='utf-8') as f: json.dump(self.tasks, f, indent=4, ensure_ascii=False)
        self.refresh_display()
    def create_widgets(self):
        lock_symbol = f" {AppConfig.ICON_LOCKED}" if self.is_locked else ""
        ttk.Label(self, text=f"Công việc: {self.display_name}{lock_symbol}", font=("Segoe UI", 14, "bold")).pack(side=tk.TOP, anchor='w', pady=(10, 10), padx=10)
        control_frame = ttk.Frame(self); control_frame.pack(fill=tk.X, pady=5, padx=10)
        btn_state = tk.DISABLED if self.is_locked else tk.NORMAL
        ttk.Button(control_frame, text="Thêm Công việc", command=self.add_task, state=btn_state).pack(side=tk.RIGHT)
        canvas_frame = ttk.Frame(self); canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.canvas = tk.Canvas(canvas_frame, borderwidth=0, background=self.style.lookup('Treeview', 'background'), highlightthickness=0)
        self.tasks_frame = ttk.Frame(self.canvas); scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set); scrollbar.pack(side="right", fill="y"); self.canvas.pack(side="left", fill="both", expand=True)
        canvas_window = self.canvas.create_window((0,0), window=self.tasks_frame, anchor="nw")
        self.tasks_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(canvas_window, width=e.width))
        self.refresh_display()
    def refresh_display(self):
        for widget in self.tasks_frame.winfo_children(): widget.destroy()
        self.task_widgets_map.clear()
        for i, task_data in enumerate(sorted(self.tasks, key=lambda t: t['done'])): self.create_task_widget(i, task_data)
    def create_task_widget(self, index, task_data):
        task_frame = ttk.Frame(self.tasks_frame, padding=5); task_frame.pack(fill=tk.X, expand=True)
        original_index = self.tasks.index(task_data)
        var = tk.BooleanVar(value=task_data["done"])
        check = ttk.Checkbutton(task_frame, variable=var, command=lambda idx=original_index: self.toggle_task(idx)); check.pack(side=tk.LEFT)
        label_font = ('Segoe UI', 10)
        label = ttk.Label(task_frame, text=task_data["text"], font=label_font, wraplength=self.winfo_width() - 150)
        if task_data["done"]: label.config(font=(label_font[0], label_font[1], 'overstrike'), foreground="gray")
        label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        btn_state = tk.DISABLED if self.is_locked else tk.NORMAL
        ttk.Button(task_frame, text="Xóa", width=5, command=lambda idx=original_index: self.delete_task(idx), state=btn_state).pack(side=tk.RIGHT)
        ttk.Button(task_frame, text="Sửa", width=5, command=lambda idx=original_index: self.edit_task(idx), state=btn_state).pack(side=tk.RIGHT, padx=2)
    def add_task(self):
        task_text = simpledialog.askstring("Thêm công việc", "Nhập nội dung:")
        if task_text: self.tasks.append({"text": task_text, "done": False}); self.save_tasks()
    def edit_task(self, task_index):
        new_text = simpledialog.askstring("Sửa công việc", "Chỉnh sửa:", initialvalue=self.tasks[task_index]["text"])
        if new_text and new_text.strip(): self.tasks[task_index]["text"] = new_text.strip(); self.save_tasks()
    def delete_task(self, task_index):
        if messagebox.askyesno("Xác nhận", "Xóa công việc này?"): del self.tasks[task_index]; self.save_tasks()
    def toggle_task(self, task_index): self.tasks[task_index]["done"] = not self.tasks[task_index]["done"]; self.save_tasks()

if __name__ == "__main__":
    app = FileManagerApp()
    app.mainloop()
