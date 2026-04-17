#!/usr/bin/env python3
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

from cheat_splitter_core import output_subfolder_name, split_cheat_file, suggest_output_dir

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD  # type: ignore
except Exception:
    DND_FILES = None
    TkinterDnD = None


class CheatSplitterApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Switch Cheat Splitter")
        self.root.geometry("860x560")

        self.file_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.unified_output_var = tk.StringVar()
        self.backup_var = tk.BooleanVar(value=True)
        self.group_in_parent_var = tk.BooleanVar(value=True)
        self.use_default_parent_name_var = tk.BooleanVar(value=True)
        self.use_unified_output_var = tk.BooleanVar(value=False)
        self.parent_name_var = tk.StringVar()
        self.output_overridden = False

        self._build_ui()

    def _build_ui(self) -> None:
        frame = tk.Frame(self.root, padx=12, pady=12)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Cheat File (.txt)").grid(row=0, column=0, sticky="w")
        tk.Entry(frame, textvariable=self.file_var).grid(row=1, column=0, sticky="ew", padx=(0, 8))
        tk.Button(frame, text="Browse...", command=self.pick_file, width=12).grid(row=1, column=1, sticky="ew")

        if TkinterDnD is not None and DND_FILES is not None:
            drop = tk.Label(
                frame,
                text="Drag and drop cheat file here",
                relief="groove",
                bd=2,
                padx=8,
                pady=12,
            )
            drop.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(8, 10))
            drop.drop_target_register(DND_FILES)
            drop.dnd_bind("<<Drop>>", self.on_drop)
        else:
            tk.Label(
                frame,
                text="Drag/drop disabled (install tkinterdnd2). Use Browse instead.",
                fg="#666",
            ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(8, 10))

        tk.Label(frame, text="Output Folder").grid(row=3, column=0, sticky="w")
        tk.Entry(frame, textvariable=self.output_var).grid(row=4, column=0, sticky="ew", padx=(0, 8))
        tk.Button(frame, text="Select...", command=self.pick_output_dir, width=12).grid(row=4, column=1, sticky="ew")
        tk.Checkbutton(
            frame,
            text="Use unified output path for all files",
            variable=self.use_unified_output_var,
            command=self.refresh_output_mode_state,
        ).grid(row=5, column=0, columnspan=2, sticky="w")
        tk.Label(frame, text="Unified Output Path").grid(row=6, column=0, sticky="w")
        self.unified_output_entry = tk.Entry(frame, textvariable=self.unified_output_var)
        self.unified_output_entry.grid(row=7, column=0, sticky="ew", padx=(0, 8))
        self.unified_output_button = tk.Button(frame, text="Select...", command=self.pick_unified_output_dir, width=12)
        self.unified_output_button.grid(row=7, column=1, sticky="ew")

        tk.Label(
            frame,
            text="Default: /path_to_cheat_file/game_name_or_id",
            fg="#666",
        ).grid(row=8, column=0, columnspan=2, sticky="w", pady=(4, 8))

        tk.Checkbutton(
            frame,
            text="Rename original 'cheats' folder to 'cheats_backup'",
            variable=self.backup_var,
        ).grid(row=9, column=0, columnspan=2, sticky="w")
        tk.Checkbutton(
            frame,
            text="For custom output, create parent folder (game_name_or_id)",
            variable=self.group_in_parent_var,
            command=self.refresh_parent_name_state,
        ).grid(row=10, column=0, columnspan=2, sticky="w")
        tk.Checkbutton(
            frame,
            text="Use default parent folder name",
            variable=self.use_default_parent_name_var,
            command=self.refresh_parent_name_state,
        ).grid(row=11, column=0, columnspan=2, sticky="w")
        tk.Label(frame, text="Parent Folder Name").grid(row=12, column=0, sticky="w")
        self.parent_name_entry = tk.Entry(frame, textvariable=self.parent_name_var)
        self.parent_name_entry.grid(row=13, column=0, columnspan=2, sticky="ew")

        tk.Button(frame, text="Split Cheats", command=self.run_split, height=2).grid(
            row=14,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(10, 10),
        )

        tk.Label(frame, text="Logs").grid(row=15, column=0, sticky="w")
        self.log_box = ScrolledText(frame, height=16, wrap="word")
        self.log_box.grid(row=16, column=0, columnspan=2, sticky="nsew")

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=0)
        frame.rowconfigure(16, weight=1)
        self.refresh_output_mode_state()
        self.refresh_parent_name_state()

    def append_log(self, text: str) -> None:
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")

    def pick_file(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Select Cheat File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not file_path:
            return
        self.set_file(file_path)

    def pick_output_dir(self) -> None:
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_var.set(folder)
            self.output_overridden = True
            self.use_unified_output_var.set(False)
            self.refresh_output_mode_state()

    def pick_unified_output_dir(self) -> None:
        folder = filedialog.askdirectory(title="Select Unified Output Folder")
        if folder:
            self.unified_output_var.set(folder)
            self.use_unified_output_var.set(True)
            self.output_overridden = True
            self.refresh_output_mode_state()

    def set_file(self, file_path: str) -> None:
        self.file_var.set(file_path)
        default_out = suggest_output_dir(file_path)
        self.parent_name_var.set(output_subfolder_name(file_path))
        if not self.output_overridden and not self.use_unified_output_var.get():
            self.output_var.set(str(default_out))
        self.append_log(f"Selected: {file_path}")
        self.append_log(f"Default output: {default_out}")
        self.refresh_parent_name_state()

    def refresh_parent_name_state(self) -> None:
        allow_custom = self.group_in_parent_var.get() and not self.use_default_parent_name_var.get()
        self.parent_name_entry.configure(state=("normal" if allow_custom else "disabled"))

    def refresh_output_mode_state(self) -> None:
        unified = self.use_unified_output_var.get()
        self.unified_output_entry.configure(state=("normal" if unified else "disabled"))
        self.unified_output_button.configure(state=("normal" if unified else "disabled"))

    def on_drop(self, event) -> None:  # noqa: ANN001
        raw = event.data.strip()

        # Windows drag data may be wrapped in braces when path has spaces.
        if raw.startswith("{") and raw.endswith("}"):
            raw = raw[1:-1]

        if " " in raw and not Path(raw).exists():
            # If multiple files were dropped, keep only first token.
            raw = raw.split(" ", 1)[0]

        self.set_file(raw)

    def run_split(self) -> None:
        file_path = self.file_var.get().strip()
        output_dir = self.output_var.get().strip()

        if not file_path:
            messagebox.showerror("Missing Input", "Please select a cheat file first.")
            return

        out_arg = output_dir or None
        if self.use_unified_output_var.get():
            unified = self.unified_output_var.get().strip()
            if not unified:
                messagebox.showerror("Missing Unified Output", "Please select a unified output folder.")
                return
            out_arg = unified

        if out_arg and self.output_overridden and self.group_in_parent_var.get():
            if self.use_default_parent_name_var.get():
                parent_name = output_subfolder_name(file_path)
            else:
                parent_name = self.parent_name_var.get().strip()
                if not parent_name:
                    messagebox.showerror("Missing Parent Name", "Please enter a custom parent folder name.")
                    return
            out_arg = str(Path(out_arg) / parent_name)

        self.append_log("-" * 72)
        self.append_log("Starting split...")
        self.root.update_idletasks()

        try:
            logs = split_cheat_file(
                file_path=file_path,
                output_dir=out_arg,
                backup_original=self.backup_var.get(),
            )
            for line in logs:
                self.append_log(line)
            messagebox.showinfo("Done", "Cheats split successfully.")
        except Exception as exc:
            self.append_log(f"Error: {exc}")
            messagebox.showerror("Split Failed", str(exc))


def main() -> None:
    if TkinterDnD is not None:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    app = CheatSplitterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
