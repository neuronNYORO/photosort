import os
import shutil
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

def get_capture_date(image_path):
    """EXIFまたはファイルの更新日時から撮影日を取得する"""
    try:
        with Image.open(image_path) as img:
            exif_data = img.getexif()
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag_name = TAGS.get(tag_id, tag_id)
                    if tag_name == 'DateTimeOriginal':
                        date_str = value.split(' ')[0]
                        return date_str.replace(':', '-')
    except Exception:
        pass
    
    timestamp = os.path.getmtime(image_path)
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')

def organize_photos(source_dir, dest_dir, progress_var, status_var, root):
    """日付 > 拡張子 の順にフォルダを作成し、ファイルをコピーする"""
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    # 対象とする拡張子（OM SystemのRAWである.orfなども含む）
    valid_extensions = ('.jpg', '.jpeg',  '.cr3', '.CR3', '.mp4', '.mov','orf', '.ORF')
    
    file_list = []
    for root_dir, _, files in os.walk(source_dir):
        for file in files:
            if file.lower().endswith(valid_extensions):
                file_list.append((root_dir, file))
                
    total_files = len(file_list)
    if total_files == 0:
        return 0

    progress_bar['maximum'] = total_files
    processed_count = 0
    copied_count = 0

    for root_dir, file in file_list:
        source_path = os.path.join(root_dir, file)
        
        # 撮影日（YYYY-MM-DD）を取得
        capture_date = get_capture_date(source_path)
        
        # 拡張子を取得して大文字のフォルダ名にする（例: '.orf' -> 'ORF'）
        ext = os.path.splitext(file)[1].lower()
        ext_folder_name = ext.replace('.', '').upper()
        if not ext_folder_name:
            ext_folder_name = "UNKNOWN"
        
        # 保存先/日付/拡張子/ というパスを作成
        date_folder = os.path.join(dest_dir, capture_date, ext_folder_name)
        if not os.path.exists(date_folder):
            os.makedirs(date_folder)
        
        dest_path = os.path.join(date_folder, file)
        
        # コピー処理（同名ファイルがなければコピー）
        if not os.path.exists(dest_path):
            shutil.copy2(source_path, dest_path)
            copied_count += 1
            
        processed_count += 1
        progress_var.set(processed_count)
        status_var.set(f"処理中... {processed_count} / {total_files} 件完了")
        root.update()
    
    return copied_count

# --- GUI部分の処理 ---
def select_source():
    dir_path = filedialog.askdirectory(title="読み込み元フォルダを選択")
    if dir_path:
        source_var.set(dir_path)

def select_dest():
    dir_path = filedialog.askdirectory(title="保存先フォルダを選択")
    if dir_path:
        dest_var.set(dir_path)

def execute_sort():
    source = source_var.get()
    dest = dest_var.get()
    
    if not source or not dest:
        messagebox.showwarning("警告", "読み込み元と保存先の両方を選択してほしい。")
        return
        
    try:
        run_button.config(state=tk.DISABLED)
        progress_var.set(0)
        status_var.set("準備中...")
        root.update()
        
        count = organize_photos(source, dest, progress_var, status_var, root)
        
        status_var.set("処理完了！")
        messagebox.showinfo("完了", f"処理が完了した。\nコピーされたファイル数: {count}件")
    # ここから下の except と finally が消えていたか、ずれていた可能性が高い
    except Exception as e:
        status_var.set("エラー発生")
        messagebox.showerror("エラー", f"エラーが発生した:\n{e}")
    finally:
        run_button.config(state=tk.NORMAL)
        progress_var.set(0)

# --- ウィンドウの設定 ---
root = tk.Tk()
root.title("Fortuner - 写真整理ツール")
root.geometry("450x300")

source_var = tk.StringVar()
dest_var = tk.StringVar()
progress_var = tk.DoubleVar()
status_var = tk.StringVar()
status_var.set("待機中")

tk.Label(root, text="読み込み元 (SDカード等):").pack(pady=(10, 0))
tk.Entry(root, textvariable=source_var, width=50).pack()
tk.Button(root, text="フォルダを選択", command=select_source).pack()

tk.Label(root, text="保存先:").pack(pady=(10, 0))
tk.Entry(root, textvariable=dest_var, width=50).pack()
tk.Button(root, text="フォルダを選択", command=select_dest).pack()

run_button = tk.Button(root, text="整理を開始する", command=execute_sort, bg="lightblue")
run_button.pack(pady=15)

progress_bar = ttk.Progressbar(root, variable=progress_var, orient="horizontal", length=350, mode="determinate")
progress_bar.pack(pady=(0, 5))
tk.Label(root, textvariable=status_var).pack()

root.mainloop()