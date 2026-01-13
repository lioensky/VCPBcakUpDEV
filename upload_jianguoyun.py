import os
import zipfile
import datetime
import requests
import glob
import sys

# 将当前目录加入路径以便导入
sys.path.append(os.path.dirname(__file__))

def load_env(env_path):
    config = {}
    if not os.path.exists(env_path):
        return config
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()
    except Exception as e:
        print(f"读取配置文件出错: {e}")
    return config

def get_latest_file(pattern):
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getctime)

def upload_to_webdav(file_path, config):
    url = config.get("JianguoyunDEVUrl", "https://dav.jianguoyun.com/dav/")
    user = config.get("JianguoyunDEVUser")
    password = config.get("JianguoyunDEVPW")
    remote_path = config.get("JianguoyunPath", "/VCP备份")
    
    if not all([user, password]):
        print("错误: 坚果云账号或密码未配置")
        return False

    filename = os.path.basename(file_path)
    # 确保远程路径以 / 结尾，且不包含重复的 /
    base_url = url.rstrip('/')
    target_url = f"{base_url}{remote_path}/{filename}"
    
    print(f"正在上传 {filename} 到坚果云...")
    try:
        with open(file_path, 'rb') as f:
            response = requests.put(
                target_url,
                data=f,
                auth=(user, password),
                timeout=300
            )
        
        if response.status_code in [200, 201, 204]:
            try:
                print("✅ 上传成功！")
            except UnicodeEncodeError:
                print("DONE: Upload Success!")
            return True
        else:
            try:
                print(f"❌ 上传失败，状态码: {response.status_code}")
            except UnicodeEncodeError:
                print(f"FAIL: Upload Failed, Status: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
    except Exception as e:
        try:
            print(f"❌ 上传过程中出现异常: {e}")
        except UnicodeEncodeError:
            print(f"ERROR: Exception during upload: {e}")
        return False

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(current_dir, "config.env")
    config = load_env(env_path)
    
    output_dir = os.path.join(current_dir, "backups")
    
    # 1. 寻找最新的前后端备份
    latest_vchat = get_latest_file(os.path.join(output_dir, "Vchat_Backup_*.zip"))
    latest_vcp = get_latest_file(os.path.join(output_dir, "VCPServer_Backup_*.zip"))
    
    if not latest_vchat or not latest_vcp:
        print("错误: 未找到足够的备份文件进行合并")
        return

    print(f"找到最新备份:")
    print(f" - 前端: {os.path.basename(latest_vchat)}")
    print(f" - 后端: {os.path.basename(latest_vcp)}")

    # 2. 创建合并文件 (使用固定文件名以覆盖旧备份，节省坚果云空间)
    full_backup_path = os.path.join(output_dir, "VCP_Full_Backup.zip")
    
    print(f"正在创建合并备份: {os.path.basename(full_backup_path)}...")
    try:
        with zipfile.ZipFile(full_backup_path, 'w', zipfile.ZIP_DEFLATED) as full_zip:
            full_zip.write(latest_vchat, os.path.basename(latest_vchat))
            full_zip.write(latest_vcp, os.path.basename(latest_vcp))
        try:
            print("✅ 合并完成")
        except UnicodeEncodeError:
            print("DONE: Merge Complete")
    except Exception as e:
        try:
            print(f"❌ 合并失败: {e}")
        except UnicodeEncodeError:
            print(f"FAIL: Merge Failed: {e}")
        return

    # 3. 上传坚果云
    if config.get("JianguoyunDEV", "false").lower() != "false":
        upload_to_webdav(full_backup_path, config)
    else:
        print("跳过上传: JianguoyunDEV 未开启")

if __name__ == "__main__":
    main()