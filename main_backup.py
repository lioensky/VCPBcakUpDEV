import os
import datetime
import sys

# 将当前目录加入路径以便导入
sys.path.append(os.path.dirname(__file__))

from Vchatbackup import create_backup as vchat_backup
from VCPServerbackup import backup_user_data_fast as vcp_server_backup
from upload_jianguoyun import main as upload_main

def load_env(env_path):
    config = {}
    if not os.path.exists(env_path):
        print(f"警告: 配置文件 {env_path} 不存在")
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

def main():
    print("="*50)
    print("VCP 一键备份系统启动")
    print("="*50)
    
    # 加载配置
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(current_dir, "config.env")
    config = load_env(env_path)
    
    # 获取路径
    vchat_url = config.get("VchatUrl", r"H:\MCP\VCPChat")
    vcp_url = config.get("VCPUrl", r"\\DESKTOP-QULL1SM\Tsubasa\Cherry-Var-Reborn")
    
    # 获取开关 (VchatCache=false)
    vchat_cache_enabled = config.get("VchatCache", "false").lower() == "true"
    
    # 备份输出目录（默认为脚本所在目录下的 backups 文件夹）
    output_dir = os.path.join(current_dir, "backups")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"配置信息:")
    print(f" - Vchat 路径: {vchat_url}")
    print(f" - VCPServer 路径: {vcp_url}")
    print(f" - 缓存备份开关: {vchat_cache_enabled}")
    print(f" - 备份输出目录: {output_dir}")
    print("-" * 50)

    # 1. 执行 Vchat 备份
    print("\n[1/2] 开始备份 Vchat (前端)...")
    # Vchatbackup.py 内部会处理 AppData 逻辑
    # 根据 config.env，如果 VchatCache 为 false，则不备份附件和TTS缓存
    vchat_res = vchat_backup(
        source_dir=vchat_url, 
        backup_attachments=vchat_cache_enabled, 
        backup_tts_cache=vchat_cache_enabled,
        output_dir=output_dir
    )
    
    if vchat_res:
        print(f"Vchat 备份成功: {vchat_res}")
    else:
        print("Vchat 备份失败，请检查路径是否正确。")

    # 2. 执行 VCPServer 备份
    print("\n[2/2] 开始备份 VCPServer (后端)...")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    vcp_filename = os.path.join(output_dir, f"VCPServer_Backup_{timestamp}.zip")
    
    vcp_res = False
    try:
        vcp_server_backup(vcp_filename, source_dir=vcp_url)
        print(f"VCPServer 备份成功: {vcp_filename}")
        vcp_res = True
    except Exception as e:
        print(f"VCPServer 备份失败: {e}")

    # 3. 坚果云上传集成
    if config.get("JianguoyunDEV", "false").lower() == "true":
        print("\n[3/3] 正在准备合并并上传至坚果云...")
        try:
            upload_main()
        except Exception as e:
            print(f"上传过程中出现错误: {e}")

    print("\n" + "="*50)
    print("所有备份任务处理完毕")
    print("="*50)
    if sys.stdin.isatty():
        input("按回车键退出...")

if __name__ == "__main__":
    main()