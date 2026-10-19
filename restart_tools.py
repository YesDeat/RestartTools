#!/usr/bin/env python3
# restart_tools.py
# 融合常用「重启 / 刷新 / 清理」类 Windows 维护操作（原 重启Edge.bat、重启资源管理器.bat 的升级版）。
# Merge common Windows "restart / refresh / clean" maintenance tasks
# (an upgraded, all-in-one version of the old RestartEdge.bat & RestartExplorer.bat).
#
# 用法 / Usage:
#   python restart_tools.py                 # 交互菜单 / interactive menu
#   python restart_tools.py edge            # 重启 Edge / restart Edge
#   python restart_tools.py explorer        # 重启资源管理器 / restart Explorer
#   python restart_tools.py all             # 执行默认全套（无需管理员）/ default set (no admin)
#   python restart_tools.py edge explorer dns  # 组合多个 / combine several
#
# 依赖 / Dependencies: 仅标准库 / stdlib only.

import os
import sys
import time
import glob
import shutil
import subprocess

WAIT_SECONDS = 2  # EN: delay between kill and restart


def run(cmd, **kw):
    """执行命令并返回 CompletedProcess / Run a command, return the result."""
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def kill_process(image_name):
    """结束进程（忽略不存在的错误）/ Terminate a process (ignore "not found")."""
    return run(["taskkill", "/F", "/IM", image_name]).returncode == 0


def launch(image_name):
    """启动程序并立即返回 / Launch a program and return immediately."""
    # EN: CREATE_NEW_CONSOLE keeps it detached from this script's console.
    subprocess.Popen([image_name], creationflags=subprocess.CREATE_NEW_CONSOLE)


# ----------------------------- 单个任务 / Tasks -----------------------------

def restart_edge():
    """重启 Edge（只处理 Edge 相关进程，不影响 Chrome）/
    Restart Edge (only Edge processes; your Chrome is never touched)."""
    print("Kill msedge / msedgedriver / CredentialUIBroker ...")
    for name in ("msedgedriver.exe", "msedge.exe", "CredentialUIBroker.exe"):
        if kill_process(name):
            print(f"  killed {name}")
    time.sleep(WAIT_SECONDS)
    print("Starting Edge ...")
    launch("msedge.exe")
    print("Done. Edge has been restarted.\n")


def restart_explorer():
    """重启资源管理器（刷新任务栏/桌面）/ Restart Explorer (refreshes taskbar/desktop)."""
    print("Restarting Windows Explorer ...")
    kill_process("explorer.exe")
    time.sleep(WAIT_SECONDS)
    launch("explorer.exe")
    print("Done. Explorer has been restarted.\n")


def flush_dns():
    """刷新 DNS 缓存 / Flush the DNS resolver cache."""
    print("Flush DNS cache ...")
    r = run(["ipconfig", "/flushdns"])
    out = (r.stdout or r.stderr).strip()
    print(out if out else "Done.\n")


def clear_temp():
    """清理当前用户的临时文件 / Clean the current user's temp files."""
    tmp = os.environ.get("TEMP", "")
    if not tmp or not os.path.isdir(tmp):
        print("Temp 目录不存在 / Temp folder not found.\n")
        return
    print(f"Clean temp: {tmp}")
    removed = 0
    for root, dirs, files in os.walk(tmp):
        for f in files:
            try:
                os.remove(os.path.join(root, f))
                removed += 1
            except OSError:
                pass
        for d in list(dirs):
            try:
                shutil.rmtree(os.path.join(root, d), ignore_errors=True)
            except OSError:
                pass
    print(f"已清理 {removed} 个文件 / Cleaned {removed} files.\n")


def empty_recycle():
    """清空回收站 / Empty the Recycle Bin."""
    print("Empty Recycle Bin ...")
    run(["powershell", "-NoProfile", "-Command",
         "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"])
    print("Done.\n")


def restart_service(svc, label):
    """重启一个 Windows 服务（需管理员）/ Restart a Windows service (needs admin)."""
    print(f"Restart {label} (needs admin) ...")
    s = run(["net", "stop", svc])
    line = (s.stdout or s.stderr).strip().splitlines()
    if line:
        print("  " + line[-1])
    time.sleep(1)
    r = run(["net", "start", svc])
    line = (r.stdout or r.stderr).strip().splitlines()
    if line:
        print("  " + line[-1])
    print()


def clear_thumbnails():
    """清除缩略图/图标缓存（之后建议重启资源管理器）/
    Clear thumbnail/icon caches (restart Explorer afterwards recommended)."""
    base = os.path.join(os.environ.get("LOCALAPPDATA", ""),
                        "Microsoft", "Windows", "Explorer")
    print(f"Clear thumbnail/icon cache: {base}")
    patterns = ("thumbcache*.db", "iconcache*.db", "thumbcache*.tmp")
    removed = 0
    for pat in patterns:
        for f in glob.glob(os.path.join(base, pat)):
            try:
                os.remove(f)
                removed += 1
            except OSError:
                pass
    print(f"已删除 {removed} 个缓存文件，建议再重启资源管理器。")
    print(f"Removed {removed} cache files; restart Explorer next.\n")


# ----------------------------- 任务注册表 / Registry -----------------------------

# EN: (中文名 / English name, 函数). Service tasks need admin.
TASKS = {
    "edge":     ("重启 Edge",            "Restart Edge",        restart_edge),
    "explorer": ("重启资源管理器",        "Restart Explorer",    restart_explorer),
    "dns":      ("刷新 DNS 缓存",         "Flush DNS",           flush_dns),
    "temp":     ("清理临时文件",          "Clean Temp",          clear_temp),
    "recycle":  ("清空回收站",            "Empty Recycle Bin",   empty_recycle),
    "thumb":    ("清除缩略图缓存",        "Clear Thumbnails",    clear_thumbnails),
    "audio":    ("重启音频服务",          "Restart Audio",       lambda: restart_service("audiosrv", "Audio")),
    "spooler":  ("重启打印后台服务",       "Restart Print Spooler", lambda: restart_service("spooler", "Print Spooler")),
    "search":   ("重启搜索索引服务",       "Restart Search",      lambda: restart_service("WSearch", "Windows Search")),
}

# EN: Default set run by `all` (no admin required).
DEFAULT_SET = ["edge", "explorer", "dns", "temp", "recycle"]


def show_menu():
    """显示交互菜单 / Show the interactive menu."""
    while True:
        print("=" * 46)
        print("Windows 维护工具 / Windows Maintenance Tool")
        keys = list(TASKS.keys())
        for i, k in enumerate(keys, 1):
            zh, en, _ = TASKS[k]
            print(f"  {i:>2}. {zh}  ({en})")
        print(f"  {len(keys)+1:>2}. 全套（无需管理员）/ All (no admin)")
        print("   0. 退出 / Exit")
        print("=" * 46)
        choice = input("请选择（数字或英文名，空格分隔多个）/ Choose: ").strip()
        if choice in ("0", "q", "Q"):
            print("退出 / Bye.")
            break
        if choice.lower() == "all" or choice == str(len(keys) + 1):
            run_set(DEFAULT_SET)
            continue
        picked = []
        for part in choice.split():
            if part.isdigit() and 1 <= int(part) <= len(keys):
                picked.append(keys[int(part) - 1])
            elif part.lower() in TASKS:
                picked.append(part.lower())
        if picked:
            run_set(picked)
        else:
            print("无效输入，请重试 / Invalid input, try again.\n")


def run_set(keys):
    """按顺序执行一组任务 / Run a list of tasks in order."""
    for k in keys:
        if k in TASKS:
            print(f"--- {TASKS[k][0]} / {TASKS[k][1]} ---")
            TASKS[k][2]()
        else:
            print(f"未知任务 / Unknown task: {k}")


def main():
    args = [a.lower() for a in sys.argv[1:]]
    if not args:
        show_menu()
        return
    if "menu" in args:
        show_menu()
        return
    if "all" in args:
        run_set(DEFAULT_SET)
        return
    run_set(args)


if __name__ == "__main__":
    main()
