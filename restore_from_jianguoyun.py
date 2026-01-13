import os
import zipfile
import requests
import sys
from xml.etree import ElementTree

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

def list_webdav_files(config):
    url = config.get("JianguoyunDEVUrl", "https://dav.jianguoyun.com/dav/")
    user = config.get("JianguoyunDEVUser")
    password = config.get("JianguoyunDEVPW")
    remote_path = config.get("JianguoyunDEV", "/VCP备份")
    
    base_url = url.rstrip('/')
    target_url = f"{base_url}{remote_path}/"
    
    headers = {'Depth': '1'}
    try:
        response = requests.request(
            'PROPFIND', 
            target_url, 
            auth=(user, password), 
            headers=headers,
            timeout=30
        )
        if response.status_code in [200, 207]:
            # 解析 XML 获取文件列表
            tree = ElementTree.fromstring(response.content)
            files = []
            ns = {'d': 'DAV:'}
            for response_node in tree.findall('d:response', ns):
                href = response_node.find('d:href', ns).text
                filename = os.path.basename(href.rstrip('/'))
                if filename and "VCP_Full_Backup_" in filename and filename.endswith(".zip"):
                    files.append(filename)
            return sorted(files, reverse=True) # 最新的在前
        else:
            print(f"无法获取文件列表，状态码: {response.status_code}")
            return []
    except Exception as e:
        print(f"获取列表异常: {e}")
        return []

def download_file(filename, config, local_path):
    url = config.get("JianguoyunDEVUrl", "https://dav.jianguoyun.com/dav/")
    user = config.get("JianguoyunDEVUser")
    password = config.get("JianguoyunDEVPW")
    remote_path = config.get("JianguoyunDEV", "/VCP备份")
    
    base_url = url.rstrip('/')
    target_url = f"{base_url}{remote_path}/{filename}"
    
    print(f"正在从坚果云下载: {filename}...")
    try:
        response = requests.get(target_url, auth=(user, password), stream=True, timeout=300)
        if response.status_code == 200:
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            try:
                print("✅ 下载成功")
            except UnicodeEncodeError:
                print("DONE: Download Success")
            return True
        else:
            try:
                print(f"❌ 下载失败，状态码: {response.status_code}")
            except UnicodeEncodeError:
                print(f"FAIL: Download Failed, Status: {response.status_code}")
            return False
    except Exception as e:
        try:
            print(f"❌ 下载异常: {e}")
        except UnicodeEncodeError:
            print(f"ERROR: Download Exception: {e}")
        return False

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(current_dir, "config.env")
    config = load_env(env_path)
    
    # 1. 获取远程文件列表
    files = list_webdav_files(config)
    if not files:
        print("未在坚果云找到备份文件")
        return
    
    latest_full_backup = files[0]
    print(f"发现最新完整备份: {latest_full_backup}")
    
    # 2. 下载到本地临时目录
    restore_dir = os.path.join(current_dir, "restore")
    if not os.path.exists(restore_dir):
        os.makedirs(restore_dir)
    
    local_zip_path = os.path.join(restore_dir, latest_full_backup)
    if not download_file(latest_full_backup, config, local_zip_path):
        return

    # 3. 拆分并解压
    print(f"正在拆分备份文件...")
    try:
        with zipfile.ZipFile(local_zip_path, 'r') as full_zip:
            # 找到内部的两个 zip
            inner_files = full_zip.namelist()
            vchat_zip_name = next((f for f in inner_files if "Vchat_Backup_" in f), None)
            vcp_zip_name = next((f for f in inner_files if "VCPServer_Backup_" in f), None)
            
            if vchat_zip_name:
                print(f" - 提取并解压前端: {vchat_zip_name}")
                full_zip.extract(vchat_zip_name, restore_dir)
                vchat_extract_path = os.path.join(restore_dir, "Vchat_Restored")
                with zipfile.ZipFile(os.path.join(restore_dir, vchat_zip_name), 'r') as z:
                    z.extractall(vchat_extract_path)
                try:
                    print(f"   ✅ 前端已恢复至: {vchat_extract_path}")
                except UnicodeEncodeError:
                    print(f"   DONE: Vchat restored to: {vchat_extract_path}")
                
            if vcp_zip_name:
                print(f" - 提取并解压后端: {vcp_zip_name}")
                full_zip.extract(vcp_zip_name, restore_dir)
                vcp_extract_path = os.path.join(restore_dir, "VCPServer_Restored")
                with zipfile.ZipFile(os.path.join(restore_dir, vcp_zip_name), 'r') as z:
                    z.extractall(vcp_extract_path)
                try:
                    print(f"   ✅ 后端已恢复至: {vcp_extract_path}")
                except UnicodeEncodeError:
                    print(f"   DONE: VCPServer restored to: {vcp_extract_path}")
                
        print("\n" + "="*50)
        try:
            print("✅ 恢复与拆分任务完成")
        except UnicodeEncodeError:
            print("DONE: Restore and Split Task Complete")
        print(f"所有文件已存放在: {restore_dir}")
        print("="*50)
    except Exception as e:
        try:
            print(f"❌ 拆分或解压失败: {e}")
        except UnicodeEncodeError:
            print(f"FAIL: Split or Extract Failed: {e}")

if __name__ == "__main__":
    main()