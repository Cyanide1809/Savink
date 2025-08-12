# Tên file: setup.py
import sys
import subprocess
import ctypes
import os

# --- CÁC HẰNG SỐ CẤU HÌNH ---

# Danh sách các thư viện cần thiết cho ứng dụng
REQUIRED_LIBRARIES = [
    "pyinstaller",   # Để biên dịch ra file .exe
    "Pillow",        # Xử lý hình ảnh (PIL Fork)
    "PyMuPDF",       # Xử lý file PDF (fitz)
    "markdown2",     # Chuyển đổi Markdown sang HTML
    "tkhtmlview"     # Hiển thị HTML trong Tkinter
]

# Tên file script biên dịch
COMPILE_SCRIPT_NAME = "compile.py"

# Lấy đường dẫn tuyệt đối đến thư mục chứa script này
# Điều này đảm bảo script luôn tìm thấy các file khác trong cùng thư mục,
# bất kể nó được chạy từ đâu hay thư mục làm việc hiện tại là gì.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def is_admin():
    """Kiểm tra xem script có đang chạy với quyền Administrator không."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_command(command, description):
    """Chạy một lệnh trong command prompt và in ra mô tả."""
    print(f"\n--- {description} ---")
    try:
        # shell=True giúp thực thi lệnh một cách an toàn và nhất quán trên Windows
        subprocess.run(command, check=True, shell=True)
        print(f"Thành công: {description} hoàn tất.")
    except subprocess.CalledProcessError as e:
        print(f"Lỗi khi thực hiện: '{description}'.")
        print(f"Lệnh thất bại: {' '.join(str(c) for c in command)}")
        print(f"Mã lỗi: {e.returncode}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Lỗi: Lệnh '{command[0]}' không được tìm thấy.")
        print("Vui lòng đảm bảo Python và pip đã được thêm vào PATH hệ thống.")
        sys.exit(1)

def main():
    """Hàm chính thực thi toàn bộ quá trình cài đặt."""
    
    # 1. Nâng cấp pip
    run_command(
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
        "Đang cập nhật pip lên phiên bản mới nhất"
    )

    # 2. Cài đặt các thư viện cần thiết
    for lib in REQUIRED_LIBRARIES:
        run_command(
            [sys.executable, "-m", "pip", "install", lib],
            f"Đang cài đặt thư viện: {lib}"
        )
    
    print("\n>>> Tất cả các thư viện cần thiết đã được cài đặt. <<<")

    # 3. Chạy script biên dịch bằng đường dẫn tuyệt đối
    compile_script_path = os.path.join(SCRIPT_DIR, COMPILE_SCRIPT_NAME)

    if not os.path.exists(compile_script_path):
        print(f"\nLỗi: Không tìm thấy file '{compile_script_path}'.")
        print("Vui lòng đảm bảo file này tồn tại trong cùng thư mục với setup.py.")
        sys.exit(1)

    run_command(
        [sys.executable, compile_script_path],
        f"Đang chạy script biên dịch '{COMPILE_SCRIPT_NAME}'"
    )
    
    print("\n---------------------------------------------------------")
    print("HOÀN TẤT! Ứng dụng đã được cài đặt thành công.")
    # Xác định đường dẫn Program Files một cách an toàn để hiển thị
    program_files_dir = os.environ.get('ProgramFiles', 'C:\\Program Files')
    final_exe_path = os.path.join(program_files_dir, "savink", "main.exe")
    print(f"Bạn có thể tìm thấy file thực thi tại: {final_exe_path}")
    print("---------------------------------------------------------")


if __name__ == "__main__":
    # Kiểm tra quyền Administrator
    if not is_admin():
        print("Yêu cầu quyền Administrator để tiếp tục...")
        # Tự động chạy lại script này với quyền admin
        try:
            # __file__ trả về đường dẫn đến script hiện tại, đảm bảo 'runas' chạy đúng file
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        except Exception as e:
            print(f"Không thể tự động yêu cầu quyền admin. Lỗi: {e}")
            print("Vui lòng chuột phải vào file 'setup.py' và chọn 'Run as administrator'.")
        sys.exit(0) # Thoát tiến trình hiện tại không có quyền admin

    # Nếu đã có quyền admin, tiếp tục thực thi hàm main
    main()
    
    # Giữ cửa sổ mở để người dùng đọc thông báo cuối cùng
    input("\nNhấn Enter để thoát...")
