import sys
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timezone

def check_expiration(expiration_date, warning_message=None, delete_action=None):
    """
    检查程序是否过期（支持日期时间对象、日期字符串和时间戳）
    
    参数:
        expiration_date (datetime/str/float): 
            过期时间，可以是：
            - datetime对象（建议带时区信息）
            - 格式为'YYYY-MM-DD [HH:MM:SS]'的字符串
            - Unix时间戳（秒或毫秒）
        warning_message (str/tuple): 过期时显示的消息
        delete_action (function): 过期时执行的自定义操作
    
    返回:
        bool: 未过期返回True，过期返回False（并退出程序）
    """
    current_datetime = datetime.now(timezone.utc)  # 使用UTC时间确保一致性
    
    # 解析不同类型的过期时间
    if isinstance(expiration_date, str):
        # 尝试解析带时间的字符串
        try:
            expiration_date = datetime.strptime(expiration_date, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                # 尝试解析仅日期的字符串
                expiration_date = datetime.strptime(expiration_date, '%Y-%m-%d')
            except ValueError:
                raise ValueError("日期格式应为'YYYY-MM-DD'或'YYYY-MM-DD HH:MM:SS'")
    
    elif isinstance(expiration_date, (int, float)):
        # 处理时间戳（自动检测秒/毫秒）
        if expiration_date > 1e12:  # 毫秒级时间戳
            expiration_date = datetime.fromtimestamp(expiration_date/1000, tz=timezone.utc)
        else:  # 秒级时间戳
            expiration_date = datetime.fromtimestamp(expiration_date, tz=timezone.utc)
    
    # 确保比较的时区一致
    if not expiration_date.tzinfo:
        expiration_date = expiration_date.replace(tzinfo=timezone.utc)
    
    # 精确比较时间（精确到毫秒）
    if current_datetime > expiration_date:
        # 默认警告消息
        if warning_message is None:
            warning_message = ("Windows Defender", 
                             "The operation could not be completed successfully "
                             "because the file contains viruses or potential junk software.")
        
        # 显示过期消息
        try:
            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口
            if isinstance(warning_message, tuple) and len(warning_message) == 2:
                messagebox.showerror(warning_message[0], warning_message[1])
            else:
                messagebox.showerror("程序过期", str(warning_message))
            root.destroy()
        except Exception as e:
            print(f"无法显示警告窗口: {e}")
        
        # 执行自定义删除操作
        if callable(delete_action):
            try:
                delete_action()
            except Exception as e:
                print(f"执行删除操作失败: {e}")
        
        sys.exit(0)
    
    return True

# 使用示例
if __name__ == "__main__":
    # 方式1：直接使用datetime对象
    print(check_expiration(datetime(2025, 8, 1, 12, 0, 0, tzinfo=timezone.utc)))
    
    # 方式2：使用字符串日期（精确到秒）
    print(check_expiration("2024-08-01"))
    print(check_expiration("2024-08-01 15:30:00"))
    
    # 方式3：使用时间戳（秒级）
    print(check_expiration(1722510000))  # 2024-08-01 15:00:00 UTC
    
    # 方式4：使用时间戳（毫秒级）
    print(check_expiration(1751969780000))
    
    # 方式5：自定义消息和操作
    def custom_delete():
        print("执行清理操作...")
        # 实际删除逻辑
    
    check_expiration(
        expiration_date=1722510000,  # 时间戳
        warning_message=("软件许可证", "您的软件许可证已过期，请续费后使用"),
        delete_action=custom_delete
    )
    
    print("程序结束...")