import os
import lzma
import threading
import sys
import time
import customtkinter as ctk
from tkinter import filedialog, messagebox

# --- Premium Color Palette ---
BG_MAIN = "#0B0F19"       # Deep outer space blue
BG_SIDEBAR = "#111827"   # Matte slate sidebar
BG_CARD = "#1F2937"      # Layered card color
ACCENT_BLUE = "#3B82F6"  # Premium electric blue
ACCENT_GREEN = "#10B981" # Cyberpunk neon green
ACCENT_RED = "#EF4444"   # Vivid ruby red
TEXT_MAIN = "#F9FAFB"    # Crisp clear text
TEXT_MUTED = "#9CA3AF"   # Soft subtext

# --- Proprietary Application Configuration ---
ARR_MAGIC = b"ARR!"      # 4-byte custom file signature to break standard LZMA headers

ctk.set_appearance_mode("Dark")

class ARRStudioX:
    def __init__(self, root):
        self.root = root
        self.root.title("ARR Engine Studio — Premium")
        self.root.geometry("780x480")
        self.root.resizable(False, False)
        
        self.selected_file_path = ""
        self.mode = "compress"

        # Apply application framework windows logo
        try:
            if os.path.exists("logo.ico"):
                self.root.iconbitmap("logo.ico")
        except:
            pass

        # --- Main Layout Grid Construction ---
        self.root.configure(fg_color=BG_MAIN)
        
        # 1. Left Navigation Sidebar Panel
        self.sidebar = ctk.CTkFrame(self.root, width=200, height=480, corner_radius=0, fg_color=BG_SIDEBAR, border_width=0)
        self.sidebar.place(x=0, y=0)
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="ARR ENGINE", font=("Impact", 24), text_color=ACCENT_BLUE)
        self.logo_label.place(x=25, y=30)
        
        self.sub_logo = ctk.CTkLabel(self.sidebar, text="STUDIO SUITE X", font=("Helvetica", 10, "bold"), text_color=TEXT_MUTED)
        self.sub_logo.place(x=27, y=60)

        # Tab Selectors
        self.btn_comp = ctk.CTkButton(self.sidebar, text="⚡ Compress Pipeline", font=("Helvetica", 12, "bold"), anchor="w", fg_color=BG_CARD, hover_color="#2D3748", height=40, width=160, corner_radius=8, command=lambda: self.set_pipeline_mode("compress"))
        self.btn_comp.place(x=20, y=140)

        self.btn_decomp = ctk.CTkButton(self.sidebar, text="🔓 Unpack Archive", font=("Helvetica", 12, "bold"), anchor="w", fg_color="transparent", hover_color="#2D3748", height=40, width=160, corner_radius=8, command=lambda: self.set_pipeline_mode("decompress"))
        self.btn_decomp.place(x=20, y=195)

        self.version_tag = ctk.CTkLabel(self.sidebar, text="Build Pipeline v3.0.4", font=("Consolas", 10), text_color="#4B5563")
        self.version_tag.place(x=25, y=440)

        # 2. Main Studio Canvas Space
        self.canvas = ctk.CTkFrame(self.root, width=540, height=440, corner_radius=12, fg_color="#131B2E", border_color="#1E293B", border_width=1)
        self.canvas.place(x=220, y=20)

        self.view_title = ctk.CTkLabel(self.canvas, text="FILE COMPRESSION MATRIX", font=("Helvetica", 16, "bold"), text_color=TEXT_MAIN)
        self.view_title.place(x=30, y=25)

        # 3. Interactive File Drag Zone Display Card
        self.file_card = ctk.CTkFrame(self.canvas, width=480, height=150, corner_radius=10, fg_color=BG_CARD, border_color="#374151", border_width=1)
        self.file_card.place(x=30, y=70)

        self.card_icon = ctk.CTkLabel(self.file_card, text="📁", font=("Helvetica", 32))
        self.card_icon.place(x=220, y=25)

        self.file_status_text = ctk.CTkLabel(self.file_card, text="No target file mapped to buffer pipeline", font=("Helvetica", 12, "bold"), text_color=TEXT_MUTED)
        self.file_status_text.place(x=130, y=80)

        self.browse_link = ctk.CTkButton(self.file_card, text="Browse Hard Drive", font=("Helvetica", 11, "underline"), fg_color="transparent", hover=False, text_color=ACCENT_BLUE, width=100, height=20, command=self.map_file_target)
        self.browse_link.place(x=190, y=110)

        # 4. Premium Console System Log Terminal Overlay
        self.console_frame = ctk.CTkFrame(self.canvas, width=480, height=45, corner_radius=8, fg_color="#090D16", border_color="#1F2937", border_width=1)
        self.console_frame.place(x=30, y=240)
        
        self.glow_dot = ctk.CTkLabel(self.console_frame, text="●", font=("Helvetica", 12), text_color=ACCENT_GREEN)
        self.glow_dot.place(x=15, y=12)

        self.console_log = ctk.CTkLabel(self.console_frame, text="CORE ENGINE STATUS: Standby / Optimization Matrix Ready", font=("Consolas", 11), text_color="#A7F3D0", anchor="w")
        self.console_log.place(x=35, y=13)

        # 5. Continuous Dynamic Loading Engine Bar Tracking
        self.bar = ctk.CTkProgressBar(self.canvas, width=480, height=6, corner_radius=3, fg_color="#0F172A", progress_color=ACCENT_BLUE)
        self.bar.set(0)
        self.bar.place(x=30, y=305)

        self.bar_metrics = ctk.CTkLabel(self.canvas, text="Data Buffer State: 0.00%", font=("Consolas", 10), text_color=TEXT_MUTED)
        self.bar_metrics.place(x=30, y=320)

        # 6. Global Operational Trigger Action Button
        self.master_btn = ctk.CTkButton(self.canvas, text="EXECUTE COMPRESSION MATRIX", font=("Helvetica", 13, "bold"), text_color="#FFFFFF", fg_color=ACCENT_RED, hover_color="#DC2626", height=45, width=480, corner_radius=8, command=self.launch_async_pipeline)
        self.master_btn.place(x=30, y=365)

        # Trigger background file reader checks on bootup
        self.check_system_arguments()

    def set_pipeline_mode(self, selected_mode):
        self.mode = selected_mode
        if selected_mode == "compress":
            self.view_title.configure(text="FILE COMPRESSION MATRIX")
            self.master_btn.configure(text="EXECUTE COMPRESSION MATRIX", fg_color=ACCENT_RED, hover_color="#DC2626")
            self.btn_comp.configure(fg_color=BG_CARD)
            self.btn_decomp.configure(fg_color="transparent")
            self.console_log.configure(text="CORE ENGINE STATUS: Standby / Compression Ready", text_color="#A7F3D0")
        else:
            self.view_title.configure(text="ARCHIVE EXTRACTION MATRIX")
            self.master_btn.configure(text="EXECUTE EXTRACTION MATRIX", fg_color=ACCENT_GREEN, hover_color="#059669")
            self.btn_comp.configure(fg_color="transparent")
            self.btn_decomp.configure(fg_color=BG_CARD)
            self.btn_decomp.configure(fg_color=BG_CARD)
            self.console_log.configure(text="CORE ENGINE STATUS: Standby / Extraction Ready", text_color="#A7F3D0")

    def map_file_target(self):
        if self.mode == "compress":
            target = filedialog.askopenfilename(title="Select file layer to pack")
        else:
            target = filedialog.askopenfilename(title="Select .arr container archive", filetypes=[("ARR Archive Container", "*.arr")])
            
        if target:
            self.selected_file_path = target
            size_mb = os.path.getsize(target) / (1024 * 1024)
            name_truncated = os.path.basename(target) if len(os.path.basename(target)) < 35 else os.path.basename(target)[:32] + "..."
            self.file_status_text.configure(text=f"{name_truncated} — [{size_mb:.2f} MB]", text_color=TEXT_MAIN)
            self.console_log.configure(text=f"CORE ENGINE STATUS: Target file array successfully buffered.", text_color="#93C5FD")

    def launch_async_pipeline(self):
        if not self.selected_file_path:
            messagebox.showerror("Execution Aborted", "No structural layout target addresses found inside data registers.")
            return
        threading.Thread(target=self.execute_processing_core, daemon=True).start()

    def execute_processing_core(self):
        self.master_btn.configure(state="disabled", text="PROCESSING SYSTEM STREAM...")
        self.browse_link.configure(state="disabled")
        self.glow_dot.configure(text_color="#FBBF24") 
        
        try:
            if self.mode == "compress":
                self.console_log.configure(text="CORE ENGINE STATUS: Partitioning data blocks into binary structures...", text_color="#FBBF24")
                output = self.selected_file_path + ".arr"
                
                for i in range(5, 50, 8):
                    time.sleep(0.02)
                    self.bar.set(i / 100)
                    self.bar_metrics.configure(text=f"Data Buffer State: {i}.00%")

                with open(self.selected_file_path, 'rb') as f_in:
                    raw_bytes = f_in.read()
                
                # Compress payload using standard high-ratio LZMA
                compressed_payload = lzma.compress(raw_bytes, preset=9)
                
                for i in range(50, 90, 8):
                    time.sleep(0.02)
                    self.bar.set(i / 100)
                    self.bar_metrics.configure(text=f"Data Buffer State: {i}.00%")

                # Write custom magic bytes envelope BEFORE the data payload
                with open(output, 'wb') as f_out:
                    f_out.write(ARR_MAGIC)
                    f_out.write(compressed_payload)
                    
            elif self.mode == "decompress":
                self.console_log.configure(text="CORE ENGINE STATUS: Verifying integrity checks... Scanning headers.", text_color="#FBBF24")
                output = self.selected_file_path[:-4] if self.selected_file_path.endswith(".arr") else self.selected_file_path + "_unpacked"
                
                for i in range(5, 40, 12):
                    time.sleep(0.015)
                    self.bar.set(i / 100)
                    self.bar_metrics.configure(text=f"Data Buffer State: {i}.00%")

                with open(self.selected_file_path, 'rb') as f_in:
                    # Look at the first 4 bytes to check for the custom signature
                    incoming_magic = f_in.read(4)
                    
                    if incoming_magic != ARR_MAGIC:
                        raise ValueError("Proprietary Header Failure: File structure type not recognized by ARR Suite X engine.")
                    
                    # Read the rest of the actual file data
                    payload = f_in.read()
                
                for i in range(40, 85, 12):
                    time.sleep(0.015)
                    self.bar.set(i / 100)
                    self.bar_metrics.configure(text=f"Data Buffer State: {i}.00%")

                restored_bytes = lzma.decompress(payload)
                
                with open(output, 'wb') as f_out:
                    f_out.write(restored_bytes)

            self.bar.set(1.0)
            self.bar_metrics.configure(text="Data Buffer State: 100.00%")
            self.glow_dot.configure(text_color=ACCENT_GREEN)
            self.console_log.configure(text="CORE ENGINE STATUS: Success. Active task finished safely.", text_color="#A7F3D0")
            messagebox.showinfo("Matrix Execution Complete", f"Data arrays verified and built cleanly.")
            
        except Exception as err:
            self.glow_dot.configure(text_color=ACCENT_RED)
            self.console_log.configure(text=f"CRITICAL FAULT: Pipeline break detected.", text_color="#FCA5A5")
            messagebox.showerror("Pipeline Breakdown", str(err))

        self.bar.set(0)
        self.bar_metrics.configure(text="Data Buffer State: 0.00%")
        self.browse_link.configure(state="normal")
        self.master_btn.configure(state="normal")
        self.set_pipeline_mode(self.mode)

    def check_system_arguments(self):
        if len(sys.argv) > 1:
            passed_path = sys.argv[1]
            if os.path.exists(passed_path):
                self.selected_file_path = passed_path
                size_mb = os.path.getsize(passed_path) / (1024 * 1024)
                self.file_status_text.configure(text=f"{os.path.basename(passed_path)} — [{size_mb:.2f} MB]", text_color=TEXT_MAIN)
                if passed_path.endswith(".arr"):
                    self.set_pipeline_mode("decompress")

if __name__ == "__main__":
    app_root = ctk.CTk()
    ARRStudioX(app_root)
    app_root.mainloop()