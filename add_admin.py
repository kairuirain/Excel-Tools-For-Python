import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout,
                            QLabel, QLineEdit, QPushButton, QMessageBox,
                            QFormLayout, QGroupBox)
from PyQt5.QtCore import Qt, QPropertyAnimation
from PyQt5.QtGui import QFont
from User import UserManager

class AdminUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_manager = UserManager()
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("创建管理员和普通用户")
        self.setFixedWidth(400)
        
        layout = QVBoxLayout()
        
        # 管理员账号组
        admin_group = QGroupBox("管理员账号")
        admin_layout = QFormLayout()
        
        self.admin_username = QLineEdit()
        self.admin_password = QLineEdit()
        self.admin_password.setEchoMode(QLineEdit.Password)
        self.admin_confirm = QLineEdit()
        self.admin_confirm.setEchoMode(QLineEdit.Password)
        
        admin_layout.addRow("用户名:", self.admin_username)
        admin_layout.addRow("密码:", self.admin_password)
        admin_layout.addRow("确认密码:", self.admin_confirm)
        
        # 添加用户名和密码规则提示
        username_hint = QLabel("用户名要求: 4-20个字符，只能包含字母、数字和下划线，不能以数字开头")
        username_hint.setWordWrap(True)
        username_hint.setStyleSheet("color: gray; font-size: 10px;")
        
        password_hint = QLabel("密码要求: 至少8个字符，必须包含大小写字母和数字")
        password_hint.setWordWrap(True)
        password_hint.setStyleSheet("color: gray; font-size: 10px;")
        
        admin_layout.addRow("", username_hint)
        admin_layout.addRow("", password_hint)
        
        admin_group.setLayout(admin_layout)
        
        # 普通用户账号组
        user_group = QGroupBox("普通用户账号")
        user_layout = QFormLayout()
        
        self.user_username = QLineEdit()
        self.user_password = QLineEdit()
        self.user_password.setEchoMode(QLineEdit.Password)
        self.user_confirm = QLineEdit()
        self.user_confirm.setEchoMode(QLineEdit.Password)
        
        user_layout.addRow("用户名:", self.user_username)
        user_layout.addRow("密码:", self.user_password)
        user_layout.addRow("确认密码:", self.user_confirm)
        
        # 添加用户名和密码规则提示
        user_username_hint = QLabel("用户名要求: 4-20个字符，只能包含字母、数字和下划线，不能以数字开头")
        user_username_hint.setWordWrap(True)
        user_username_hint.setStyleSheet("color: gray; font-size: 10px;")
        
        user_password_hint = QLabel("密码要求: 至少8个字符，必须包含大小写字母和数字")
        user_password_hint.setWordWrap(True)
        user_password_hint.setStyleSheet("color: gray; font-size: 10px;")
        
        user_layout.addRow("", user_username_hint)
        user_layout.addRow("", user_password_hint)
        
        user_group.setLayout(user_layout)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.create_button = QPushButton("创建账号")
        self.create_button.clicked.connect(self.create_users)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.cancel_setup)
        
        button_layout.addWidget(self.create_button)
        button_layout.addWidget(self.cancel_button)
        
        # 添加所有组件到主布局
        layout.addWidget(admin_group)
        layout.addWidget(user_group)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 设置样式
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 3px;
            }
            QPushButton {
                padding: 8px 15px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton[text="取消"] {
                background-color: #f44336;
            }
            QPushButton[text="取消"]:hover {
                background-color: #da190b;
            }
        """)
        
    def cancel_setup(self):
        try:
            # 确保auth目录存在
            if not os.path.exists("auth"):
                os.makedirs("auth")
            
            # 将step.txt设置为0
            with open("auth/step.txt", "w") as f:
                f.write("0")
            
            self.reject()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"设置step.txt时发生错误：{str(e)}")
            self.reject()

    def create_users(self):
        # 验证管理员账号
        admin_username = self.admin_username.text().strip()
        admin_password = self.admin_password.text()
        admin_confirm = self.admin_confirm.text()
        
        if not admin_username or not admin_password:
            QMessageBox.warning(self, "错误", "管理员账号和密码不能为空")
            return
            
        if admin_password != admin_confirm:
            QMessageBox.warning(self, "错误", "管理员密码两次输入不一致")
            return
            
        # 注意：这里使用了UserManager类的私有方法来验证用户名和密码格式
        # 虽然这些方法是私有的（以下划线开头），但我们需要使用它们来确保用户输入符合要求
        # 验证管理员用户名格式
        if not self.user_manager._validate_username(admin_username):
            QMessageBox.warning(self, "错误", "管理员用户名格式不正确\n要求：4-20个字符，只能包含字母、数字和下划线，不能以数字开头")
            return
            
        # 验证管理员密码格式
        if not self.user_manager._validate_password(admin_password):
            QMessageBox.warning(self, "错误", "管理员密码格式不正确\n要求：至少8个字符，必须包含大小写字母和数字")
            return
            
        # 验证普通用户账号
        user_username = self.user_username.text().strip()
        user_password = self.user_password.text()
        user_confirm = self.user_confirm.text()
        
        if not user_username or not user_password:
            QMessageBox.warning(self, "错误", "普通用户账号和密码不能为空")
            return
            
        if user_password != user_confirm:
            QMessageBox.warning(self, "错误", "普通用户密码两次输入不一致")
            return
            
        # 同样使用UserManager类的私有方法验证普通用户的用户名和密码格式
        # 验证普通用户用户名格式
        if not self.user_manager._validate_username(user_username):
            QMessageBox.warning(self, "错误", "普通用户用户名格式不正确\n要求：4-20个字符，只能包含字母、数字和下划线，不能以数字开头")
            return
            
        # 验证普通用户密码格式
        if not self.user_manager._validate_password(user_password):
            QMessageBox.warning(self, "错误", "普通用户密码格式不正确\n要求：至少8个字符，必须包含大小写字母和数字")
            return
        
        try:
            # 检查users.json是否存在
            if not os.path.exists("users.json"):
                # 创建空的users.json文件
                with open("users.json", "w") as f:
                    json.dump({}, f)
            
            # 创建管理员账号
            if not self.user_manager.register(admin_username, admin_password, "admin"):
                QMessageBox.warning(self, "错误", "管理员账号创建失败，用户名可能已存在")
                return
                
            # 创建普通用户账号
            if not self.user_manager.register(user_username, user_password, "user"):
                QMessageBox.warning(self, "错误", "普通用户账号创建失败，用户名可能已存在")
                return
                
            QMessageBox.information(self, "成功", "账号创建成功！")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建账号时发生错误：{str(e)}")
            return

def main():
    app = QApplication(sys.argv)
    dialog = AdminUserDialog()
    dialog.exec_()

if __name__ == "__main__":
    main()