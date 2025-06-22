import os
import sys
import configparser
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMessageBox, QPushButton, 
                            QVBoxLayout, QWidget, QLabel, QHBoxLayout)
from PyQt5.QtCore import Qt
from Mode.ExcelToMarkdown import ExcelToMarkdown
from Mode.ExcelDataQuery import ExcelDataQuery

# 检查是否需要运行add_admin.py
def check_and_run_admin_setup():
    """
    检查是否需要运行管理员设置程序
    条件：
    1. /auth/step.txt文件不存在，或
    2. /auth/step.txt文件中值为1或0
    """
    # 确保auth目录存在
    if not os.path.exists("auth"):
        os.makedirs("auth")
    
    step_path = "auth/step.txt"
    run_setup = False
    
    # 检查文件是否存在
    if not os.path.exists(step_path):
        run_setup = True
    else:
        # 读取文件内容
        try:
            with open(step_path, 'r') as f:
                content = f.read().strip()
                if content == '0' or content == '1' or content == '':
                    run_setup = True
        except:
            # 读取文件出错，视为需要运行设置
            run_setup = True
    
    # 如果需要运行设置程序
    if run_setup:
        try:
            # 运行add_admin.py
            subprocess.run([sys.executable, "add_admin.py"], check=True)
            
            # 更新step.txt，设置为2表示已完成初始设置
            with open(step_path, 'w') as f:
                f.write('2')
        except subprocess.CalledProcessError:
            print("管理员设置程序运行失败")
        except Exception as e:
            print(f"发生错误: {e}")

class MainWindow(QMainWindow):
    def __init__(self, current_user=None):
        super().__init__()
        self.current_user = current_user
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Excel应用程序")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建中央部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 添加顶部栏
        top_bar_layout = QHBoxLayout()
        
        # 添加标题
        title_label = QLabel("Excel工具集")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        title_label.setAlignment(Qt.AlignCenter)
        top_bar_layout.addWidget(title_label)
        
        # 添加退出登录按钮
        logout_btn = QPushButton("退出登录")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border-radius: 5px;
                font-size: 14px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        logout_btn.setMaximumWidth(100)
        logout_btn.clicked.connect(self.logout)
        top_bar_layout.addWidget(logout_btn)
        
        main_layout.addLayout(top_bar_layout)
        
        # 添加功能按钮
        button_layout = QHBoxLayout()
        
        # 定义按钮样式
        button_style = """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """
        
        # Excel转Markdown按钮
        self.excel_to_md_btn = QPushButton("Excel转Markdown")
        self.excel_to_md_btn.setMinimumSize(200, 60)
        self.excel_to_md_btn.setStyleSheet(button_style)
        self.excel_to_md_btn.clicked.connect(self.open_excel_to_markdown)
        button_layout.addWidget(self.excel_to_md_btn)
        
        # Excel数据查询按钮
        self.excel_query_btn = QPushButton("Excel数据查询")
        self.excel_query_btn.setMinimumSize(200, 60)
        self.excel_query_btn.setStyleSheet(button_style)
        self.excel_query_btn.clicked.connect(self.open_excel_data_query)
        button_layout.addWidget(self.excel_query_btn)
        
        # 用户管理按钮（仅管理员可见）
        if self.current_user and self.current_user.role == 'admin':
            self.user_manage_btn = QPushButton("用户管理")
            self.user_manage_btn.setMinimumSize(200, 60)
            self.user_manage_btn.setStyleSheet(button_style)
            self.user_manage_btn.clicked.connect(self.open_user_management)
            button_layout.addWidget(self.user_manage_btn)
        
        # 添加按钮布局到主布局
        main_layout.addLayout(button_layout)
        main_layout.addStretch()
        
        # 添加底部信息
        footer_layout = QHBoxLayout()
        version_label = QLabel("版本: 1.0.0")
        author_label = QLabel("作者: SkyXing")
        footer_layout.addWidget(version_label)
        footer_layout.addStretch()
        footer_layout.addWidget(author_label)
        main_layout.addLayout(footer_layout)
        
        # 显示当前登录用户信息
        if self.current_user:
            user_info = f'当前用户: {self.current_user.username} ({self.current_user.role})'
            self.statusBar().showMessage(user_info)
        else:
            self.statusBar().showMessage('就绪')
        
    def show_message(self, title, message):
        QMessageBox.information(self, title, message)
        
    def open_excel_to_markdown(self):
        """打开Excel转Markdown功能窗口"""
        self.excel_to_md_window = ExcelToMarkdown()
        self.excel_to_md_window.show()
    
    def open_excel_data_query(self):
        """打开Excel数据查询窗口"""
        self.excel_data_query_window = ExcelDataQuery()
        self.excel_data_query_window.show()
        
    def open_user_management(self):
        """打开用户管理窗口"""
        from admin import AdminWindow
        admin_window = AdminWindow(self)
        admin_window.exec_()
        
    def logout(self):
        """处理退出登录"""
        from login import show_login
        
        # 关闭当前窗口
        self.close()
        
        # 显示登录窗口
        login_window = show_login()
        
        # 如果登录成功，创建新的主窗口
        if hasattr(login_window, 'is_accepted') and login_window.is_accepted:
            new_window = MainWindow(login_window.current_user)
            new_window.show()

def main():
    # 检查并运行管理员设置
    check_and_run_admin_setup()
    
    # 启动主应用程序
    app = QApplication(sys.argv)
    
    # 显示登录窗口
    from login import show_login
    login_window = show_login()
    
    # 如果登录成功，显示主窗口
    if hasattr(login_window, 'is_accepted') and login_window.is_accepted:
        window = MainWindow(login_window.current_user)
        window.show()
        sys.exit(app.exec_())

if __name__ == "__main__":
    main()