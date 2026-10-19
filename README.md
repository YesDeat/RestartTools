# RestartTools

一个用 Python 写的 Windows 维护小工具，把「重启 Edge」「重启资源管理器」等常用刷新/清理操作融合到一个带菜单的脚本里。

A small Python Windows maintenance tool that merges common "restart / refresh / clean" operations — including the old `RestartEdge.bat` and `RestartExplorer.bat` — into one script with a menu.

## 功能 / Features

| 命令 / Command | 说明 / Description | 需管理员 / Admin |
| --- | --- | --- |
| `edge` | 重启 Edge（只杀 Edge 相关进程，不影响 Chrome）/ Restart Edge (Edge-only, Chrome untouched) | 否 No |
| `explorer` | 重启资源管理器（刷新任务栏/桌面）/ Restart Explorer | 否 No |
| `dns` | 刷新 DNS 缓存 / Flush DNS cache | 否 No |
| `temp` | 清理临时文件 / Clean `%TEMP%` | 否 No |
| `recycle` | 清空回收站 / Empty Recycle Bin | 否 No |
| `thumb` | 清除缩略图/图标缓存 / Clear thumbnail & icon caches | 否 No |
| `audio` | 重启音频服务 / Restart Audio service | 是 Yes |
| `spooler` | 重启打印后台服务 / Restart Print Spooler | 是 Yes |
| `search` | 重启搜索索引服务 / Restart Windows Search | 是 Yes |

## 依赖 / Dependencies

仅 Python 标准库，无需安装任何东西 / Stdlib only, nothing to install.

> 注意：本机 `python` 命令指向 Microsoft Store 存根，请用 **`py`** 启动器运行（如已安装 Python 3）。
> Note: on this machine `python` points to the Store stub; use the **`py`** launcher instead.

## 用法 / Usage

交互菜单 / Interactive menu（双击或运行 / double-click or run）:

```powershell
py restart_tools.py
```

命令行 / Command line（空格分隔可多选 / space-separated for multiple）:

```powershell
py restart_tools.py edge            # 只重启 Edge / restart Edge only
py restart_tools.py explorer        # 只重启资源管理器 / restart Explorer only
py restart_tools.py edge explorer dns
py restart_tools.py all             # 默认全套（无需管理员）/ default set (no admin)
```

## 说明 / Notes

- `all` 默认执行：`edge explorer dns temp recycle`（都不需要管理员）。
  `all` runs `edge explorer dns temp recycle` by default (none need admin).
- 服务类操作（`audio`/`spooler`/`search`）需右键「以管理员身份运行」才有效。
  Service tasks (`audio`/`spooler`/`search`) require "Run as administrator".
- 清完缩略图缓存后，建议再执行一次 `explorer` 让其生效。
  After clearing thumbnails, run `explorer` once more to apply.
