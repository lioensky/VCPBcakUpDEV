import os
import zipfile
import datetime
import sys

def create_backup(source_dir=None, backup_attachments=False, backup_tts_cache=False, output_dir="."):
    # 获取当前时间作为备份文件名的一部分
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = os.path.join(output_dir, f"Vchat_Backup_{timestamp}.zip")
    
    if source_dir is None:
        source_dir = os.getcwd()
    
    appdata_dir = os.path.join(source_dir, "AppData")
    
    if not os.path.exists(appdata_dir):
        print(f"错误: 未找到 {appdata_dir} 目录。")
        return None

    print(f"--- Vchat 备份工具 ---")
    print(f"源目录: {source_dir}")
    print(f"备份附件: {backup_attachments}, 备份TTS缓存: {backup_tts_cache}")

    # 定义备份规则
    # 1. AppData 根目录文件 (不包含子文件夹)
    # 2-9. 指定子文件夹的所有文件
    subdirs_to_include = [
        "Notemodules",
        "avatarimage",
        "generated_lists",
        "systemPromptPresets",
        "UserData",
        "Agents",
        "AgentGroups",
        "Translatormodules"
    ]
    
    if backup_tts_cache:
        subdirs_to_include.append("tts_cache")

    try:
        with zipfile.ZipFile(backup_filename, 'w', zipfile.ZIP_DEFLATED) as backup_zip:
            # 1. 备份 AppData 根目录下的文件 (不包含子文件夹)
            print("正在备份 AppData 根目录文件...")
            for item in os.listdir(appdata_dir):
                item_path = os.path.join(appdata_dir, item)
                if os.path.isfile(item_path):
                    backup_zip.write(item_path, arcname=os.path.join("AppData", item))

            # 2-10. 备份指定的子文件夹
            for subdir in subdirs_to_include:
                subdir_path = os.path.join(appdata_dir, subdir)
                if not os.path.exists(subdir_path):
                    print(f"跳过: 目录 {subdir_path} 不存在")
                    continue
                
                print(f"正在备份 {subdir}...")
                for root, dirs, files in os.walk(subdir_path):
                    # 处理附件排除逻辑
                    if not backup_attachments and "attachments" in root:
                        # 如果不备份附件，且当前路径包含 attachments，则跳过该目录下的文件
                        # 注意：这里简单处理，如果 UserData 下有 attachments 文件夹则跳过
                        if os.path.basename(root) == "attachments" or "attachments" in root.split(os.sep):
                            continue

                    for file in files:
                        file_path = os.path.join(root, file)
                        # 计算在 zip 中的相对路径
                        arcname = os.path.relpath(file_path, os.path.dirname(appdata_dir))
                        backup_zip.write(file_path, arcname=arcname)

            # 3. 备份 VCPDistributedServer 目录下的 env 和 json 文件
            dist_server_dir = os.path.join(source_dir, "VCPDistributedServer")
            if os.path.exists(dist_server_dir):
                print(f"正在备份 {dist_server_dir} 中的配置文件...")
                for item in os.listdir(dist_server_dir):
                    if item.endswith(".env") or item.endswith(".json"):
                        item_path = os.path.join(dist_server_dir, item)
                        if os.path.isfile(item_path):
                            arcname = os.path.join("VCPDistributedServer", item)
                            backup_zip.write(item_path, arcname=arcname)
            else:
                print(f"跳过: 目录 {dist_server_dir} 不存在")

        print(f"\n备份完成！")
        print(f"备份文件已保存为: {os.path.abspath(backup_filename)}")
        return backup_filename
    except Exception as e:
        print(f"\n备份过程中出错: {e}")
        return None

if __name__ == "__main__":
    # 保持交互式运行兼容性
    appdata_dir = "AppData"
    if os.path.exists(appdata_dir):
        backup_attachments = input("是否备份聊天附件 (AppData/UserData/attachments)? (体积可能很大) [y/N]: ").lower() == 'y'
        backup_tts_cache = input("是否备份 TTS 缓存 (AppData/tts_cache)? (体积可能很大) [y/N]: ").lower() == 'y'
        create_backup(os.getcwd(), backup_attachments, backup_tts_cache)
        input("\n按回车键退出...")
    else:
        print("请在 VCPChat 根目录下运行此脚本。")