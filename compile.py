import os
import subprocess
import argparse
import shutil
import ctypes
import sys

SCRIPT_NAME = "savink.py" 
PYINSTALLER_EXE_NAME = "savink.exe" 
INSTALL_FOLDER_NAME = "savink" 
FINAL_EXE_NAME = "main.exe" 
LOGO_PNG_NAME = "logo.png"
LOGO_ICO_NAME = "logo.ico"

def is_admin():
    """Kiểm tra xem script có đang chạy với quyền Administrator không."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_install_path():
    """Lấy đường dẫn cài đặt đầy đủ trong Program Files."""
    program_files = os.environ.get('ProgramFiles', 'C:\\Program Files')
    install_dir = os.path.join(program_files, INSTALL_FOLDER_NAME)
    return os.path.join(install_dir, FINAL_EXE_NAME)

def delete_old_exe(exe_path):
    """Xóa file .exe cũ nếu tồn tại."""
    if os.path.exists(exe_path):
        try:
            os.remove(exe_path)
            print(f"Đã xóa file cũ: {exe_path}")
        except OSError as e:
            print(f"Lỗi khi xóa file cũ: {e}")
            print("Vui lòng đảm bảo chương trình không đang chạy và thử lại.")
            sys.exit(1)


def compile_and_install(target_exe_path):
    """Biên dịch script và cài đặt vào vị trí đích."""
    print("Đang biên dịch script thành file .exe...")

    icon_path = os.path.join(os.path.dirname(__file__), LOGO_ICO_NAME)
    
    pyinstaller_command = [
        "pyinstaller",
        "--onefile",
        "--noconsole",
    ]
    
    if os.path.exists(icon_path):
        pyinstaller_command.extend(["--icon", icon_path])
        print(f"Sử dụng icon: {icon_path}")
    else:
        print(f"Cảnh báo: Không tìm thấy file '{LOGO_ICO_NAME}'. Biên dịch không có icon.")

    pyinstaller_command.append(SCRIPT_NAME)

    subprocess.run(pyinstaller_command, check=True, shell=True)

    built_exe_path = os.path.join("dist", PYINSTALLER_EXE_NAME)

    if os.path.exists(built_exe_path):
        target_dir = os.path.dirname(target_exe_path)
        print(f"Đang tạo thư mục cài đặt: {target_dir}")
        os.makedirs(target_dir, exist_ok=True)

        print(f"Đang sao chép file thực thi đến: {target_exe_path}")
        shutil.copy2(built_exe_path, target_exe_path)
        print(f"Đã tạo thành công file: {target_exe_path}")
        
        source_logo_path = os.path.join(os.path.dirname(__file__), LOGO_PNG_NAME)
        if os.path.exists(source_logo_path):
            target_logo_path = os.path.join(target_dir, LOGO_PNG_NAME)
            print(f"Đang sao chép logo đến: {target_logo_path}")
            shutil.copy2(source_logo_path, target_logo_path)
        else:
            print(f"Cảnh báo: Không tìm thấy file '{LOGO_PNG_NAME}' để sao chép.")
    else:
        print("Lỗi: Không tìm thấy file đã biên dịch từ PyInstaller.")
        sys.exit(1)

    print("Đang dọn dẹp các file tạm...")
    for item in ["build", "dist", f"{SCRIPT_NAME.split('.')[0]}.spec"]:
        try:
            if os.path.isdir(item):
                shutil.rmtree(item)
            elif os.path.isfile(item):
                os.remove(item)
        except OSError as e:
            print(f"Lỗi khi dọn dẹp {item}: {e}")

if __name__ == "__main__":
    if not is_admin():
        print("Lỗi: Vui lòng chạy script này với quyền Administrator.")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit(0)
    
    target_path = get_install_path()
    
    delete_old_exe(target_path)
    compile_and_install(target_path)
    
    print("\nQuá trình biên dịch và cài đặt hoàn tất!")
