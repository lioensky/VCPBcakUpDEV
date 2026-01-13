# VCP 一键备份与恢复系统

这是一个为 VCP 项目量身定制的自动化备份解决方案，支持前后端分离备份、局域网路径、文件过滤以及坚果云云端同步。

## 核心功能

- **一键备份**：同时备份前端 (Vchat) 和后端 (VCPServer) 数据。
- **智能过滤**：
  - 前端：可选是否备份 `attachments` 和 `tts_cache`（通过 `VchatCache` 开关）。
  - 后端：自动忽略大型缓存文件（如 `multimodal_cache.json`）和数据库文件。
- **云端同步**：自动将前后端备份合并，并通过 WebDAV 上传至坚果云。
- **一键恢复**：从坚果云拉取最新备份，自动拆分并解压到指定目录。
- **跨平台兼容**：修复了 Windows 终端下的编码显示问题。

## 文件结构

- `main_backup.py`: 备份主控脚本。
- `restore_from_jianguoyun.py`: 恢复与拆分脚本。
- `Vchatbackup.py`: 前端备份逻辑。
- `VCPServerbackup.py`: 后端备份逻辑。
- `upload_jianguoyun.py`: 合并与上传逻辑。
- `config.env`: 配置文件（需根据 `config.env.example` 创建）。

## 快速开始

1. **配置环境**：
   复制 `config.env.example` 为 `config.env`，并填写你的项目路径和坚果云 WebDAV 信息。

2. **执行备份**：
   ```bash
   python VCPBackUp/main_backup.py
   ```

3. **执行恢复**：
   ```bash
   python VCPBackUp/restore_from_jianguoyun.py
   ```

## 注意事项

- 坚果云需要使用**应用密码**而非登录密码。
- 后端备份支持 `\\` 开头的局域网共享路径。
- 备份文件默认保存在 `VCPBackUp/backups/`，恢复文件保存在 `VCPBackUp/restore/`。