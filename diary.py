"""
MemoryBook Pro — Blue Themed Edition
------------------------------------
- Pleasant pastel blue UI
- Login / Signup system
- Image attachments and gallery view
- Background customization
- Proper deletion of selected entries
- Animated page transitions
Requires: customtkinter, pillow
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox, Toplevel
from PIL import Image, ImageTk
import os, json, uuid, shutil
from datetime import datetime

# --------------------------
# Config / Storage helpers
# --------------------------
ctk.set_appearance_mode("light")  # Always light mode for soft colors
ctk.set_default_color_theme("blue")

USERS_FILE = "users.json"
IMAGES_DIR = "user_images"
THUMBS_DIR = os.path.join(IMAGES_DIR, "thumbs")
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(THUMBS_DIR, exist_ok=True)


def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_users(data):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def user_entries_file(username):
    return f"{username}_entries.json"


def load_entries(username):
    path = user_entries_file(username)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_entries(username, entries):
    with open(user_entries_file(username), "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)


def copy_and_thumb(src_path):
    """Copy image to folder and create thumbnail"""
    try:
        ext = os.path.splitext(src_path)[1]
        dest_name = f"{uuid.uuid4().hex}{ext}"
        dest_path = os.path.join(IMAGES_DIR, dest_name)
        shutil.copy(src_path, dest_path)
        im = Image.open(dest_path)
        im.thumbnail((220, 160))
        thumb_path = os.path.join(THUMBS_DIR, dest_name)
        im.save(thumb_path)
        return dest_path, thumb_path
    except Exception as e:
        print("copy_and_thumb error:", e)
        return None, None


# --------------------------
# Main App
# --------------------------
class MemoryBookPro(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1100x720")
        self.title("MemoryBook Pro — Blue Edition")
        self.resizable(True, True)

        self.user = None
        self.entries = []
        self.current_idx = -1
        self.bg_image_obj = None
        self.bg_path = None
        self.memories = []  # ✅ store all loaded memories for editing support

        self.create_login_screen()

    # --------------------------
    # Login / Signup
    # --------------------------
    def create_login_screen(self):
        self.clear_screen()
        frame = ctk.CTkFrame(self, corner_radius=12, fg_color=("#F4F7FA", "#A7C7E7"))
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(frame, text="📘 MemoryBook Pro", font=("Georgia", 28, "bold")).pack(pady=(18, 6))
        ctk.CTkLabel(frame, text="Cherish your memories beautifully", font=("Arial", 12)).pack(pady=(0, 12))

        self.login_user = ctk.CTkEntry(frame, placeholder_text="Username", width=340)
        self.login_user.pack(pady=(6, 6))
        self.login_pass = ctk.CTkEntry(frame, placeholder_text="Password", show="*", width=340)
        self.login_pass.pack(pady=(6, 12))

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=(6, 6))
        ctk.CTkButton(btn_frame, text="Login", command=self.do_login, width=140).pack(side="left", padx=8)
        ctk.CTkButton(btn_frame, text="Sign Up", fg_color="#4CAF50", command=self.do_signup, width=140).pack(side="left")

    def do_signup(self):
        username = self.login_user.get().strip()
        password = self.login_pass.get().strip()
        if not username or not password:
            messagebox.showwarning("Missing", "Enter username and password.")
            return
        users = load_users()
        if username in users:
            messagebox.showerror("Exists", "Username already exists.")
            return
        users[username] = password
        save_users(users)
        messagebox.showinfo("Created", "Account created! Please login.")

    def do_login(self):
        u = self.login_user.get().strip()
        p = self.login_pass.get().strip()
        users = load_users()
        if u in users and users[u] == p:
            self.user = u
            self.load_main_ui()
        else:
            messagebox.showerror("Invalid", "Incorrect username or password.")

    # --------------------------
    # Main UI
    # --------------------------
    def load_main_ui(self):
        self.clear_screen()
        self.entries = load_entries(self.user)
        self.entries.sort(key=lambda e: e.get("date", ""), reverse=False)

        # background label
        self.bg_label = ctk.CTkLabel(self, text="")
        self.bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)

        # sidebar
        left = ctk.CTkFrame(self, width=300, corner_radius=0, fg_color=("#FFFFFF", "#A7C7E7"))
        left.pack(side="left", fill="y", padx=12, pady=12)

        ctk.CTkLabel(left, text=f"Welcome, {self.user}", font=("Georgia", 16, "bold")).pack(anchor="w", pady=(6, 8))
        ctk.CTkButton(left, text="➕ Add Memory", command=self.add_memory_popup, width=220).pack(pady=6)
        ctk.CTkButton(left, text="🖼️ Gallery View", command=self.open_gallery, width=220).pack(pady=6)
        ctk.CTkButton(left, text="🖌️ Set Background", command=self.set_background, width=220).pack(pady=6)
        ctk.CTkButton(left, text="🔄 Refresh", command=self.refresh_entries, width=220).pack(pady=6)
        ctk.CTkButton(left, text="🚪 Logout", fg_color="#E57373", command=self.logout, width=220).pack(pady=(24, 6))

        # preview area
        center = ctk.CTkFrame(self, corner_radius=10, fg_color=("#FFFFFF", "#A7C7E7"))
        center.pack(side="left", fill="both", expand=True, padx=6, pady=12)

        nav = ctk.CTkFrame(center, fg_color="transparent")
        nav.pack(fill="x", pady=(6, 8))
        ctk.CTkButton(nav, text="⟨ Prev", command=lambda: self.navigate(-1)).pack(side="left", padx=8)
        ctk.CTkButton(nav, text="Next ⟩", command=lambda: self.navigate(1)).pack(side="left",padx=8)
        ctk.CTkButton(nav, text="✏️ Edit", fg_color="#4A90E2", command=self.edit_current).pack(side="left", padx=8)
        ctk.CTkButton(nav, text="🗑️ Delete", fg_color="#E57373", command=self.delete_current).pack(side="right", padx=8)

        self.preview_container = ctk.CTkFrame(center, corner_radius=10, fg_color=("#FFFFFF", "#A7C7E7"))
        self.preview_container.pack(fill="both", expand=True, padx=12, pady=6)

        # right list
        right = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color=("#FFFFFF", "#A7C7E7"))
        right.pack(side="right", fill="y", padx=12, pady=12)
        ctk.CTkLabel(right, text="All Memories", font=("Georgia", 14, "bold")).pack(anchor="w", pady=(6, 6))
        self.listbox = ctk.CTkScrollableFrame(right, width=240, height=560)
        self.listbox.pack()

        self.refresh_entries()

    # --------------------------
    # Background
    # --------------------------
    def set_background(self):
        path = filedialog.askopenfilename(title="Choose background", filetypes=[("Images", "*.jpg *.png *.jpeg")])
        if not path:
            return
        try:
            img = Image.open(path)
            w, h = self.winfo_width(), self.winfo_height()
            img = img.resize((w, h), Image.LANCZOS)
            self.bg_image_obj = ImageTk.PhotoImage(img)
            self.bg_label.configure(image=self.bg_image_obj)
            self.bg_path = path
        except Exception as e:
            messagebox.showerror("Error", f"Cannot set background: {e}")

    # --------------------------
    # Add memory
    # --------------------------
    def add_memory_popup(self):
        win = ctk.CTkToplevel(self)
        win.geometry("640x680")
        win.title("Add Memory")
        win.attributes("-topmost", True)
        win.after(10, lambda: win.attributes("-topmost", False))
        win.lift()
        win.focus_force()
        win.grab_set() 
        

        title_e = ctk.CTkEntry(win, placeholder_text="Title", width=560)
        title_e.pack(pady=(14, 8))
        text_box = ctk.CTkTextbox(win, width=560, height=320)
        text_box.pack(pady=(6,8))

        attach_frame = ctk.CTkFrame(win, fg_color="transparent")
        attach_frame.pack(pady=(6, 6))
        attached = []
        

        def attach():
            files = filedialog.askopenfilenames(filetypes=[("Images", "*.jpg *.jpeg *.png *.gif")])
            for f in files:
                dest, thumb = copy_and_thumb(f)
                if dest:
                    attached.append(dest)
            ctk.CTkLabel(attach_frame, text=f"{len(attached)} images attached").pack()

        def save():
            title = title_e.get().strip()
            text = text_box.get("0.0", "end").strip()
            if not title and not text and not attached:
                messagebox.showwarning("Empty", "Write something or attach images.")
                return
            entry = {
                "id": uuid.uuid4().hex,
                "date": datetime.now().strftime("%B %d, %Y — %I:%M %p"),
                "title": title or "Untitled",
                "text": text,
                "images": attached
            }
            entries = load_entries(self.user)
            entries.append(entry)
            save_entries(self.user, entries)
            win.destroy()
            self.refresh_entries()
            messagebox.showinfo("Saved", "Memory saved!")

        ctk.CTkButton(win, text="Attach Images", command=attach, width=160).pack(pady=6)
        ctk.CTkButton(win, text="Save Memory", fg_color="#4CAF50", command=save, width=160).pack(pady=6)

    # --------------------------
    # Refresh entries
    # --------------------------
    def refresh_entries(self):
        self.entries = load_entries(self.user)
        self.memories = self.entries  # ✅ keep same list for editing
        self.entries.sort(key=lambda e: e.get("date", ""), reverse=False)
        for w in self.listbox.winfo_children():
            w.destroy()
        for idx, e in enumerate(reversed(self.entries)):
            frame = ctk.CTkFrame(self.listbox, fg_color=("#FFFFFF", "#A7C7E7"), corner_radius=10)
            frame.pack(fill="x", pady=6, padx=6)
            label = ctk.CTkLabel(
    frame,
    text=f"{e.get('date', 'Unknown Date').split('—')[0].strip()} - {e.get('title', 'Untitled')}",
    anchor="w",
    wraplength=200
)
            label.pack(fill="x", padx=8, pady=6)

            btn = ctk.CTkButton(frame, text="Open", width=80,
                                command=lambda i=(len(self.entries) - 1 - idx): self.show_with_animation(i, direction=0))
            btn.pack(padx=8, pady=(0, 6), anchor="e")

        self.current_idx = len(self.entries) - 1
        self.show_with_animation(self.current_idx, direction=0)

    # --------------------------
    # Show entry (with delete fix)
    # --------------------------
    def show_with_animation(self, target_idx, direction=1):
        if target_idx < 0 or target_idx >= len(self.entries):
            return
        old_frame = getattr(self, "_active_preview", None)
        new_frame = ctk.CTkFrame(self.preview_container, fg_color=("#FFFFFF", "#A7C7E7"), corner_radius=12)
        new_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        e = self.entries[target_idx]
        top = ctk.CTkFrame(new_frame, fg_color="transparent")
        top.pack(fill="x", pady=8, padx=12)
        ctk.CTkLabel(top, text=e.get("title", "Untitled"), font=("Georgia", 20, "bold")).pack(anchor="w")
        ctk.CTkLabel(top, text=e.get("date", ""), font=("Arial", 11, "italic")).pack(anchor="w", pady=(0, 6))

        txt = ctk.CTkTextbox(new_frame, wrap="word")
        txt.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        txt.insert("0.0", e.get("text", ""))
        txt.configure(state="disabled")

        strip = ctk.CTkFrame(new_frame, fg_color="transparent")
        strip.pack(fill="x", padx=12, pady=(0, 12))
        for img_path in e.get("images", []) or []:
            if not os.path.exists(img_path):
                continue
            thumb_path = os.path.join(THUMBS_DIR, os.path.basename(img_path))
            if not os.path.exists(thumb_path):
                try:
                    im = Image.open(img_path)
                    im.thumbnail((180, 140))
                    im.save(thumb_path)
                except Exception:
                    thumb_path = img_path
            im = Image.open(thumb_path)
            ph = ImageTk.PhotoImage(im)
            lbl = ctk.CTkLabel(strip, image=ph, text="")
            lbl.image = ph
            lbl.pack(side="left", padx=8)
            lbl.bind("<Button-1>", lambda ev, p=img_path: self.open_image_popup(p))

        if old_frame:
            old_frame.destroy()
        self._active_preview = new_frame
        self.current_idx = target_idx

    # --------------------------
    # Delete entry (fixed)
    # --------------------------
    def delete_current(self):
        if not self.entries or self.current_idx < 0:
            messagebox.showwarning("None", "No entry selected.")
            return

        actual_idx = len(self.entries) - 1 - self.current_idx
        e = self.entries[actual_idx]

        if messagebox.askyesno("Delete", f"Delete memory '{e.get('title', 'Untitled')}'?"):
            del self.entries[actual_idx]
            save_entries(self.user, self.entries)
            self.refresh_entries()
            messagebox.showinfo("Deleted", "Memory deleted successfully.")
        
            # --------------------------
    # Edit existing memory
    # --------------------------
    def edit_current(self):
        if not self.entries or self.current_idx < 0:
            messagebox.showwarning("None", "No memory selected to edit.")
            return

        e = self.entries[self.current_idx]

        win = ctk.CTkToplevel(self)
        win.geometry("640x680")
        win.title("Edit Memory")
        win.lift()
        win.focus_force()
        win.grab_set()

        title_e = ctk.CTkEntry(win, width=560)
        title_e.insert(0, e.get("title", "Untitled"))
        title_e.pack(pady=(14, 8))

        text_box = ctk.CTkTextbox(win, width=560, height=320)
        text_box.insert("0.0", e.get("text", ""))
        text_box.pack(pady=(6, 8))

        attached = e.get("images", []).copy()

        attach_frame = ctk.CTkFrame(win, fg_color="transparent")
        attach_frame.pack(pady=(6, 6))

        def attach():
            files = filedialog.askopenfilenames(filetypes=[("Images", "*.jpg *.jpeg *.png *.gif")])
            for f in files:
                dest, thumb = copy_and_thumb(f)
                if dest:
                    attached.append(dest)
            ctk.CTkLabel(attach_frame, text=f"{len(attached)} images attached").pack()

        def save_changes():
            e["title"] = title_e.get().strip() or "Untitled"
            e["text"] = text_box.get("0.0", "end").strip()
            e["images"] = attached
            save_entries(self.user, self.entries)
            self.refresh_entries()
            win.destroy()
            messagebox.showinfo("Updated", "Memory updated successfully!")

        ctk.CTkButton(win, text="Attach More Images", command=attach, width=160).pack(pady=6)
        ctk.CTkButton(win, text="Save Changes", fg_color="#4CAF50", command=save_changes, width=160).pack(pady=6)

            
        # --------------------------
    # Navigation between memories
    # --------------------------
    def navigate(self, direction):
        """Move forward/backward through memories"""
        if not self.entries:
            return

        new_idx = self.current_idx + direction
        if 0 <= new_idx < len(self.entries):
            self.show_with_animation(new_idx, direction)
        else:
            messagebox.showinfo("End", "No more memories in that direction.")


    # --------------------------
    # Other Utilities
    # --------------------------
    def open_image_popup(self, path):
        if not os.path.exists(path):
            messagebox.showerror("Missing", "Image not found.")
            return
        win = ctk.CTkToplevel(self)
        win.title("Photo")
        img = Image.open(path)
        img.thumbnail((1100, 700))
        ph = ImageTk.PhotoImage(img)
        lbl = ctk.CTkLabel(win, image=ph)
        lbl.image = ph
        lbl.pack()

    def open_gallery(self):
        images = []
        for e in self.entries:
            for p in e.get("images", []) or []:
                if os.path.exists(p):
                    images.append(p)
        if not images:
            messagebox.showinfo("No images", "No images found for your memories.")
            return

        gwin = ctk.CTkToplevel(self)
        gwin.geometry("900x700")
        gwin.title("Photo Gallery")
        grid_frame = ctk.CTkScrollableFrame(gwin, width=860, height=660)
        grid_frame.pack(padx=12, pady=12)

        cols, row, col = 4, 0, 0
        for p in images:
            thumb_path = os.path.join(THUMBS_DIR, os.path.basename(p))
            if not os.path.exists(thumb_path):
                im = Image.open(p)
                im.thumbnail((220, 160))
                im.save(thumb_path)
            im = Image.open(thumb_path)
            ph = ImageTk.PhotoImage(im)
            frame = ctk.CTkFrame(grid_frame, width=200, height=140, corner_radius=12, fg_color=("#FFFFFF", "#A7C7E7"))
            frame.grid(row=row, column=col, padx=8, pady=8)
            lbl = ctk.CTkLabel(frame, image=ph, text="")
            lbl.image = ph
            lbl.pack()
            lbl.bind("<Button-1>", lambda ev, path=p: self.open_image_popup(path))
            col += 1
            if col >= cols:
                col = 0
                row += 1

    def logout(self):
        self.user = None
        self.entries = []
        self.current_idx = -1
        self.create_login_screen()

    def clear_screen(self):
        for w in self.winfo_children():
            w.destroy()


if __name__ == "__main__":
    app = MemoryBookPro()
    app.mainloop()
