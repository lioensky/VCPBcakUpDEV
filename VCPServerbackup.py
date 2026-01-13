import os
import zipfile
import datetime
import sys

def backup_user_data_fast(backup_filename, source_dir='.'):
    """
    极速版本 - 带智能进度条
    """
    file_extensions = {'.txt', '.md', '.env', '.json'}
    excluded_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}
    excluded_paths = {os.path.normpath(os.path.join(source_dir, 'dailynote/MusicDiary'))}
    # 需要忽略的具体文件路径
    excluded_files = {
        os.path.normpath(os.path.join(source_dir, r'Plugin\ImageProcessor\multimodal_cache.json')),
        os.path.normpath(os.path.join(source_dir, r'Plugin\TarotDivination\celestial_database.json'))
    }
    
    print(f"--- VCPServer 备份工具 ---")
    print(f"源目录: {source_dir}")
    
    print("阶段1: 扫描文件...")
    start_time = datetime.datetime.now()
    
    # 第一阶段：快速收集所有文件路径
    files_to_backup = []
    
    for root, dirs, files in os.walk(source_dir):
        root_norm = os.path.normpath(root)
        dirs[:] = [d for d in dirs 
                   if d not in excluded_dirs 
                   and os.path.join(root_norm, d) not in excluded_paths]
        
        for file in files:
            _, ext = os.path.splitext(file)
            if ext in file_extensions:
                file_path = os.path.join(root, file)
                if not (file == backup_filename and root in ('.', './')):
                    if os.path.normpath(file_path) not in excluded_files:
                        files_to_backup.append(file_path)
    
    scan_time = (datetime.datetime.now() - start_time).total_seconds()
    print(f"扫描完成: {len(files_to_backup):,} 个文件, 耗时 {scan_time:.2f}s")
    
    # 第二阶段：压缩文件（带智能进度条）
    print("阶段2: 压缩文件...")
    compress_start = datetime.datetime.now()
    
    total = len(files_to_backup)
    
    # ✅ 动态计算更新频率：至少更新20次，但不超过每个文件都更新
    update_interval = max(1, total // 20)
    
    with zipfile.ZipFile(backup_filename, 'w', zipfile.ZIP_DEFLATED, 
                         compresslevel=1) as zipf:
        for i, file_path in enumerate(files_to_backup):
            try:
                zipf.write(file_path, os.path.relpath(file_path, source_dir))
            except (PermissionError, FileNotFoundError):
                pass
            
            # ✅ 智能进度更新
            if (i + 1) % update_interval == 0 or (i + 1) == total:
                pct = (i + 1) / total * 100
                bar_len = 30
                filled = int(bar_len * (i + 1) // total)
                bar = '█' * filled + '░' * (bar_len - filled)
                
                elapsed = (datetime.datetime.now() - compress_start).total_seconds()
                speed = (i + 1) / elapsed if elapsed > 0 else 0
                
                try:
                    sys.stdout.write(f"\r[{bar}] {pct:5.1f}% | {i+1:,}/{total:,} | {speed:.0f} 文件/秒")
                    sys.stdout.flush()
                except UnicodeEncodeError:
                    # 如果 GBK 编码失败（例如在某些 Windows 终端），则使用简化的进度显示
                    sys.stdout.write(f"\r> {pct:5.1f}% | {i+1:,}/{total:,} | {speed:.0f} files/s")
                    sys.stdout.flush()
    
    print()  # 换行
    
    total_time = (datetime.datetime.now() - start_time).total_seconds()
    backup_size = os.path.getsize(backup_filename) / (1024 * 1024)
    
    print(f"{'=' * 50}")
    try:
        print(f"✅ 备份完成: {backup_filename}")
        print(f"📁 文件数量: {total:,}")
        print(f"📦 大小: {backup_size:.2f} MB")
        print(f"⏱️  总耗时: {total_time:.2f}s")
    except UnicodeEncodeError:
        print(f"DONE: {backup_filename}")
        print(f"Files: {total:,}")
        print(f"Size: {backup_size:.2f} MB")
        print(f"Time: {total_time:.2f}s")


if __name__ == "__main__":
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_user_data_fast(f"VCPServer_Backup_{timestamp}.zip")