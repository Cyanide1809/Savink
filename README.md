# Trình quản lý File / File Manager

Đây là file hướng dẫn cài đặt và sử dụng ứng dụng Trình quản lý File.
<br>
*This is the README file for installing and using the File Manager application.*

---

## 🇻🇳 Hướng dẫn (Tiếng Việt)

### 1. Cài đặt
Để cài đặt ứng dụng, bạn chỉ cần thực hiện các bước đơn giản sau:

1.  **Chạy file `setup.py`:** Tìm file `setup.py` trong thư mục dự án và chạy nó (ví dụ: bằng cách nhấp đúp hoặc chạy lệnh `python setup.py` trong terminal). Điều này bao gồm việc bạn phải cài đặt Python 3 trước đó.

2.  **Cung cấp quyền Administrator:** Một cửa sổ **User Account Control (UAC)** sẽ hiện lên hỏi quyền quản trị viên. Hãy nhấn **"Yes"** để tiếp tục.
    > ⚠️ Đây là bước **bắt buộc** để chương trình có thể cài đặt vào thư mục `Program Files` và lưu lại các cài đặt sau này.

3.  **Chờ quá trình tự động hoàn tất:** Script sẽ tự động thực hiện các công việc sau:
    *   Cập nhật `pip` lên phiên bản mới nhất.
    *   Cài đặt tất cả các thư viện cần thiết.
    *   Biên dịch mã nguồn thành file chương trình (`main.exe`).
    *   Sao chép file chương trình vào thư mục cài đặt.

4.  **Lấy đường dẫn chương trình:** Khi quá trình hoàn tất, cửa sổ terminal sẽ hiển thị thông báo "HOÀN TẤT!" cùng với đường dẫn đến file chương trình, ví dụ:
    ```
    Bạn có thể tìm thấy file thực thi tại: C:\Program Files\savink\main.exe
    ```

### 2. Sử dụng lần đầu

1.  **Sao chép đường dẫn:** Bôi đen và sao chép (`Ctrl+C`) toàn bộ đường dẫn `C:\Program Files\savink\main.exe` từ cửa sổ terminal.

2.  **Chạy chương trình:** Nhấn tổ hợp phím **`Win + R`** để mở hộp thoại Run, dán (`Ctrl+V`) đường dẫn vừa sao chép vào và nhấn Enter.

3.  Ứng dụng sẽ khởi động. Từ bây giờ, bạn đã có thể sử dụng chương trình.

### 3. Mẹo sử dụng: Ghim lên Taskbar
Để tiện cho việc truy cập sau này mà không cần lặp lại các bước trên, bạn nên ghim ứng dụng ra thanh Taskbar (thanh tác vụ).

1.  Mở **File Explorer** (trình quản lý tệp của Windows).
2.  Dán đường dẫn `C:\Program Files\savink` vào thanh địa chỉ và nhấn Enter.
3.  Tìm file **`main.exe`**, nhấp chuột phải vào nó.
4.  Chọn **"Pin to taskbar"** (Ghim vào thanh tác vụ).

Bây giờ bạn có thể khởi động ứng dụng chỉ bằng một cú nhấp chuột từ thanh taskbar!

---

## 🇬🇧 Instructions (English)

### 1. Installation
To install the application, simply follow these steps:

1.  **Run the `setup.py` file:** Locate the `setup.py` file in the project directory and run it (e.g., by double-clicking or by running `python setup.py` in a terminal). This action include install Python 3 before.

2.  **Grant Administrator Privileges:** A **User Account Control (UAC)** prompt will appear asking for administrator permissions. Click **"Yes"** to continue.
    > ⚠️ This step is **mandatory** for the program to be installed into the `Program Files` directory and to save settings correctly later on.

3.  **Wait for the automated process:** The script will automatically perform the following tasks:
    *   Update `pip` to the latest version.
    *   Install all required libraries.
    *   Compile the source code into a program file (`main.exe`).
    *   Copy the program file to the installation directory.

4.  **Get the program path:** When the process is complete, the terminal will display a "COMPLETE!" message along with the path to the program file, for example:
    ```
    You can find the executable at: C:\Program Files\savink\main.exe
    ```

### 2. First-time Usage

1.  **Copy the path:** Highlight and copy (`Ctrl+C`) the full path `C:\Program Files\savink\main.exe` from the terminal window.

2.  **Run the program:** Press the **`Win + R`** key combination to open the Run dialog, paste (`Ctrl+V`) the copied path, and press Enter.

3.  The application will now launch. You are now ready to use the program.

### 3. Usage Tip: Pin to Taskbar
For convenient access in the future without repeating the steps above, you should pin the application to your Taskbar.

1.  Open **File Explorer**.
2.  Paste the path `C:\Program Files\savink` into the address bar and press Enter.
3.  Find the **`main.exe`** file and right-click on it.
4.  Select **"Pin to taskbar"**.

Now you can launch the application with a single click from your taskbar
