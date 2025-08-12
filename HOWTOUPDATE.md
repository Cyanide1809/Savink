# Hướng dẫn cập nhật Trình quản lý File
Tài liệu này hướng dẫn cách biên dịch lại và cập nhật ứng dụng sau khi bạn đã thay đổi mã nguồn.
<br>
*This document guides you on how to recompile and update the application after you have modified the source code.*

---

## 🇻🇳 Hướng dẫn cập nhật (Tiếng Việt)

### 1. Khi nào cần cập nhật?
Hướng dẫn này dành cho các **nhà phát triển** hoặc **người dùng nâng cao** đã chỉnh sửa file mã nguồn `savink.py` (ví dụ: để thêm tính năng mới hoặc sửa lỗi).

Nếu bạn chỉ là người dùng thông thường và không chỉnh sửa code, bạn không cần thực hiện các bước này. File `setup.py` chỉ cần chạy một lần duy nhất cho việc cài đặt ban đầu.

### 2. Các bước cập nhật

#### Bước 1: Đóng hoàn toàn ứng dụng
Đây là bước **quan trọng nhất** để tránh lỗi "Access is denied" (Từ chối truy cập).
- Nếu ứng dụng đang mở, hãy đóng cửa sổ của nó.
- Để chắc chắn, hãy mở **Task Manager** (`Ctrl + Shift + Esc`), tìm đến tab "Details" và đảm bảo không có tiến trình nào tên là `main.exe` đang chạy. Nếu có, hãy kết thúc nó (End task).

#### Bước 2: Chạy file `compile.py` với quyền Administrator
1.  Mở **PowerShell** hoặc **Command Prompt** với quyền quản trị viên (chuột phải -> *Run as administrator*).

2.  Sử dụng lệnh `cd` để di chuyển đến thư mục chứa dự án của bạn. Ví dụ:
    ```sh
    cd D:\Code\Python\Link
    ```

3.  Chạy lệnh sau để bắt đầu quá trình biên dịch:
    ```sh
    python compile.py
    ```

#### Bước 3: Chờ quá trình hoàn tất
Script sẽ tự động thực hiện các công việc sau trong cửa sổ terminal:
- Xóa file `main.exe` cũ trong `C:\Program Files\savink\`.
- Biên dịch lại file `savink.py` đã được chỉnh sửa.
- Sao chép file `main.exe` mới vào lại thư mục cài đặt.

#### Bước 4: Hoàn tất!
Khi bạn thấy thông báo "Biên dịch và cài đặt hoàn tất", ứng dụng của bạn đã được cập nhật thành công. Bây giờ bạn có thể khởi chạy lại nó từ shortcut trên thanh Taskbar hoặc từ file `main.exe`.

### 3. Lưu ý quan trọng
- **`setup.py` vs `compile.py`**: Hãy nhớ, `setup.py` dùng để cài đặt mọi thứ từ đầu (bao gồm cả các thư viện), trong khi `compile.py` chỉ dùng để biên dịch lại mã nguồn đã có.
- **An toàn dữ liệu**: Quá trình cập nhật này **sẽ không** ảnh hưởng đến bất kỳ tệp hay thư mục nào bạn đã tạo bên trong `FileManagerRoot`. Dữ liệu của bạn luôn được giữ an toàn.

---

## 🇬🇧 Update Guide (English)

### 1. When to Update?
This guide is intended for **developers** or **advanced users** who have modified the `savink.py` source code file (e.g., to add new features or fix bugs).

If you are a regular user and have not edited the code, you do not need to perform these steps. The `setup.py` file only needs to be run once for the initial installation.

### 2. Update Steps

#### Step 1: Completely Close the Application
This is the **most important step** to avoid the "Access is denied" error.
- If the application is open, close its window.
- To be certain, open **Task Manager** (`Ctrl + Shift + Esc`), go to the "Details" tab, and ensure that no process named `main.exe` is running. If it is, end the task.

#### Step 2: Run `compile.py` with Administrator Privileges
1.  Open **PowerShell** or **Command Prompt** as an administrator (right-click -> *Run as administrator*).

2.  Use the `cd` command to navigate to your project directory. For example:
    ```sh
    cd D:\Code\Python\Link
    ```

3.  Run the following command to start the compilation process:
    ```sh
    python compile.py
    ```

#### Step 3: Wait for the Process to Complete
The script will automatically perform the following tasks in the terminal window:
- Delete the old `main.exe` file from `C:\Program Files\savink\`.
- Recompile the modified `savink.py` file.
- Copy the new `main.exe` back into the installation directory.

#### Step 4: Done!
When you see the message "Compilation and installation complete," your application has been successfully updated. You can now launch it again from your Taskbar shortcut or from the `main.exe` file.

### 3. Important Notes
- **`setup.py` vs. `compile.py`**: Remember, `setup.py` is for setting up everything from scratch (including libraries), while `compile.py` is only for recompiling existing source code.
- **Data Safety**: This update process **will not** affect any of the files or folders you have created inside `FileManagerRoot`. Your data is always kept safe.
