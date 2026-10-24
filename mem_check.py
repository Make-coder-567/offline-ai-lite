"""离线AI 本机内存 / 模型驻留检测 (Windows)。

用法:
    python mem_check.py

输出:
    - 系统总/可用物理内存
    - Ollama 进程工作集占用
    - 当前驻留(已加载到内存)的模型及大小  -> ollama ps
    - 全部已导入模型的体积              -> ollama list
    - 基于可用内存的预算建议

把输出贴回对话，可精准判断到底是离线AI(Ollama 多模型叠加)还是
RFS-DRL 训练(PyTorch)在吃内存。
"""
import ctypes
import subprocess
import sys


def system_memory():
    """返回 (总字节, 可用字节)。仅 Windows 用 ctypes；其他平台尽力而为。"""
    if sys.platform.startswith("win"):
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]
        s = MEMORYSTATUSEX()
        s.dwLength = ctypes.sizeof(s)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(s))
        return s.ullTotalPhys, s.ullAvailPhys
    # 非 Windows：退而求其次读 /proc 或 psutil（不可用就报错）
    try:
        import psutil
        vm = psutil.virtual_memory()
        return vm.total, vm.available
    except Exception:
        return 0, 0


def run_ollama(args):
    try:
        out = subprocess.run(
            ["ollama"] + args, capture_output=True, text=True, timeout=30
        )
        if out.returncode != 0:
            return None, out.stderr.strip() or "ollama 返回非零退出码"
        return out.stdout, None
    except FileNotFoundError:
        return None, "未找到 ollama 命令（未安装或未加入 PATH）"
    except Exception as e:  # noqa: BLE001
        return None, str(e)


def main():
    total, avail = system_memory()
    print("=" * 64)
    print("本机内存检测  (offline-ai mem_check)")
    print("=" * 64)
    if total:
        print(f"总物理内存   : {total / 1024 ** 3:.1f} GB")
        print(f"可用物理内存 : {avail / 1024 ** 3:.1f} GB"
              f"  ({avail / total * 100:.0f}%)")
    else:
        print("无法读取系统内存（非 Windows 且未装 psutil）。")
    print()

    print("Ollama 进程工作集占用:")
    try:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "Get-Process ollama* -ErrorAction SilentlyContinue | "
             "Select-Object Name,@{N='WS_MB';E={[math]::Round($_.WorkingSet/1MB,1)}} | "
             "Format-Table -AutoSize | Out-String -Width 120"],
            capture_output=True, text=True, timeout=30,
        )
        txt = (out.stdout or "").strip()
        print(txt or "  (无 ollama 进程在运行)")
    except Exception as e:  # noqa: BLE001
        print("  无法读取进程:", e)
    print()

    print("当前驻留模型 (ollama ps):")
    ps, err = run_ollama(["ps"])
    print((ps or "").strip() or f"  {err}")
    print()

    print("全部已导入模型体积 (ollama list):")
    ls, err = run_ollama(["list"])
    print((ls or "").strip() or f"  {err}")
    print()

    print("预算建议:")
    avail_gb = avail / 1024 ** 3 if total else None
    if avail_gb is None:
        print("  无法评估（没读到内存）。")
    elif avail_gb < 5:
        print(f"  [!] 可用内存仅 {avail_gb:.1f} GB，已低于 5GB 安全线。")
        print("      建议: 设 OLLAMA_MAX_LOADED_MODELS=1 + 仅用 ≤4B 单模型 + num_ctx=3072")
        print("            （离线AI 已默认 num_ctx=3072 / keep_alive=5m）。")
    else:
        print(f"  可用内存 {avail_gb:.1f} GB，较宽裕。")


if __name__ == "__main__":
    main()
