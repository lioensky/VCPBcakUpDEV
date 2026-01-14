import os
import requests
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

def upload_to_webdav(file_path, config, remote_folder):
    url = config.get("JianguoyunDEVUrl", "https://dav.jianguoyun.com/dav/")
    user = config.get("JianguoyunDEVUser")
    password = config.get("JianguoyunDEVPW")
    
    if not all([user, password]):
        print("错误: 坚果云账号或密码未配置")
        return False

    if not os.path.exists(file_path):
        print(f"错误: 本地文件不存在: {file_path}")
        return False

    filename = os.path.basename(file_path)
    # 确保远程路径以 / 结尾，且不包含重复的 /
    base_url = url.rstrip('/')
    # 确保远程文件夹路径以 / 开头
    if not remote_folder.startswith('/'):
        remote_folder = '/' + remote_folder
    
    target_url = f"{base_url}{remote_folder}/{filename}"
    
    print(f"正在上传 {filename} 到坚果云 {remote_folder}...")
    try:
        with open(file_path, 'rb') as f:
            response = requests.put(
                target_url,
                data=f,
                auth=(user, password),
                timeout=300
            )
        
        if response.status_code in [200, 201, 204]:
            print("✅ 上传成功！")
            return True
        else:
            print(f"❌ 上传失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 上传过程中出现异常: {e}")
        return False

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(current_dir, "config.env")
    config = load_env(env_path)
    
    # 从 env 获取 VCPUrl 并推导 one-api.db 路径
    # 同目录考虑
    vcp_url = config.get("VCPUrl")
    if not vcp_url:
        print("错误: config.env 中未配置 VCPUrl")
        return

    # 获取父目录 (\\DESKTOP-QULL1SM\Tsubasa) 并拼接 NewAPI\one-api.db
    base_dir = os.path.dirname(vcp_url)
    db_path = os.path.join(base_dir, "NewAPI", "one-api.db")
    
    # 坚果云目标文件夹
    remote_folder = "/API数据库备份"
    
    # 执行上传
    if config.get("JianguoyunDEV", "false").lower() != "false":
        upload_to_webdav(db_path, config, remote_folder)
    else:
        print("跳过上传: JianguoyunDEV 未开启")

if __name__ == "__main__":
    main()