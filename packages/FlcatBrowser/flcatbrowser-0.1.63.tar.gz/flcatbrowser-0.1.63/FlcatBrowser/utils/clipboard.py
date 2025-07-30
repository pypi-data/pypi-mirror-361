import platform
from typing import Tuple
import pyperclip

# Windows 专用模块
if platform.system() == 'Windows':
    import win32clipboard
    import win32con

def save_clipboard():
    """保存当前剪贴板内容（Windows支持多格式，其他平台仅保存文本）"""
    system = platform.system()
    saved_data = {'system': system}

    if system == 'Windows':
        # Windows 保存所有剪贴板格式
        try:
            win32clipboard.OpenClipboard()
            formats = []
            current_format = 0
            while True:
                current_format = win32clipboard.EnumClipboardFormats(current_format)
                if current_format == 0:
                    break
                formats.append(current_format)
            
            data = {}
            for fmt in formats:
                try:
                    data[fmt] = win32clipboard.GetClipboardData(fmt)
                except Exception as e:
                    pass  # 跳过无法读取的格式
            saved_data['data'] = data
        finally:
            win32clipboard.CloseClipboard()
    else:
        # 其他平台仅保存文本
        try:
            saved_data['text'] = pyperclip.paste()
        except pyperclip.PyperclipException:
            saved_data['text'] = None
    return saved_data

def restore_clipboard(saved_data):
    """恢复剪贴板内容"""
    system = saved_data.get('system', '')
    
    if system == 'Windows' and 'data' in saved_data:
        # Windows 恢复多格式
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            for fmt, data in saved_data['data'].items():
                win32clipboard.SetClipboardData(fmt, data)
        finally:
            win32clipboard.CloseClipboard()
    else:
        # 其他平台恢复文本
        if saved_data.get('text'):
            pyperclip.copy(saved_data['text'])
            
def set_clipboard(text: str) -> Tuple[bool, str]:
    """
    设置剪贴板文本内容（跨平台）
    
    参数:
        text (str): 要设置的文本内容
        
    返回:
        Tuple[bool, str]: (操作是否成功, 错误消息)
    """
    try:
        # 优先使用 pyperclip 的跨平台方案
        pyperclip.copy(text)
        
        # 二次验证（Windows 专用）
        if platform.system() == "Windows":
            win32clipboard.OpenClipboard()
            clipboard_text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
            if clipboard_text != text:
                raise RuntimeError("剪贴板验证失败，内容不一致")
                
        return (True, "")
        
    except Exception as e:
        error_msg = f"设置剪贴板失败: {str(e)}"
        
        # 尝试备用方案 (Windows)
        if platform.system() == "Windows":
            try:
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
                win32clipboard.CloseClipboard()
                return (True, "")
            except Exception as win_err:
                error_msg += f" | 备用方案失败: {str(win_err)}"
        
        return (False, error_msg)
# 使用示例
if __name__ == '__main__':
    # 1. 保存当前剪贴板
    original_data = save_clipboard()
    
    # 2. 设置新内容到剪贴板
    new_text = "临时设置的剪贴板内容"
    pyperclip.copy(new_text)
    print("当前剪贴板:", pyperclip.paste())
    
    # 3. 恢复原始内容
    restore_clipboard(original_data)
    print("恢复后的剪贴板:", pyperclip.paste())