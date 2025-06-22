import hashlib
import random
import string
from datetime import datetime, timedelta
from typing import Optional
from PyQt5.QtWidgets import (QDialog, QLabel, QLineEdit, QPushButton, 
                            QVBoxLayout, QMessageBox, QHBoxLayout)
from PyQt5.QtCore import Qt
from User import UserManager

class RegisterCode:
    """注册码管理类"""
    def __init__(self, code: str, expiry: datetime):
        self.code = code
        self.expiry = expiry
        self.used = False

class RegisterCodeManager:
    """注册码管理器"""
    _instance = None
    _codes = {}  # 存储注册码: RegisterCode对象
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RegisterCodeManager, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def generate_code(cls, valid_hours: int = 24) -> str:
        """生成新的注册码
        
        Args:
            valid_hours: 注册码有效期（小时）
            
        Returns:
            str: 生成的注册码
        """
        # 生成16位随机字符串
        chars = string.ascii_letters + string.digits
        code = ''.join(random.choice(chars) for _ in range(16))
        
        # 创建注册码对象并存储
        expiry = datetime.now() + timedelta(hours=valid_hours)
        cls._codes[code] = RegisterCode(code, expiry)
        
        return code
    
    @classmethod
    def verify_code(cls, code: str) -> bool:
        """验证注册码是否有效
        
        Args:
            code: 要验证的注册码
            
        Returns:
            bool: 注册码是否有效
        """
        reg_code = cls._codes.get(code)
        if not reg_code:
            return False
            
        if reg_code.used:
            return False
            
        if datetime.now() > reg_code.expiry:
            return False
            
        # 标记注册码为已使用
        reg_code.used = True
        return True

class RegisterWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_manager = UserManager()
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI界面"""
        self.setWindowTitle("用户注册")
        self.setFixedWidth(400)
        
        layout = QVBoxLayout()
        
        # 用户名输入
        username_layout = QHBoxLayout()
        username_label = QLabel("用户名:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("4-20个字符，字母/数字/下划线")
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)
        
        # 密码输入
        password_layout = QHBoxLayout()
        password_label = QLabel("密码:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("至少8个字符，包含大小写字母和数字")
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)
        
        # 确认密码输入
        confirm_layout = QHBoxLayout()
        confirm_label = QLabel("确认密码:")
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.setPlaceholderText("再次输入密码")
        confirm_layout.addWidget(confirm_label)
        confirm_layout.addWidget(self.confirm_input)
        layout.addLayout(confirm_layout)
        
        # 注册码输入
        code_layout = QHBoxLayout()
        code_label = QLabel("注册码:")
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("请输入管理员提供的注册码")
        code_layout.addWidget(code_label)
        code_layout.addWidget(self.code_input)
        layout.addLayout(code_layout)
        
        # 注册按钮
        self.register_btn = QPushButton("注册")
        self.register_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.register_btn.clicked.connect(self.register)
        layout.addWidget(self.register_btn)
        
        # 返回登录按钮
        self.back_btn = QPushButton("返回登录")
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                padding: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.back_btn.clicked.connect(self.reject)
        layout.addWidget(self.back_btn)
        
        self.setLayout(layout)
        
    def register(self):
        """处理注册请求"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        reg_code = self.code_input.text().strip()
        
        # 验证输入
        if not username or not password or not confirm or not reg_code:
            QMessageBox.warning(self, "错误", "请填写所有字段")
            return
            
        if password != confirm:
            QMessageBox.warning(self, "错误", "两次输入的密码不一致")
            return
            
        # 验证注册码
        if not RegisterCodeManager.verify_code(reg_code):
            QMessageBox.warning(self, "错误", "无效的注册码")
            return
            
        # 尝试注册
        if self.user_manager.register(username, password):
            QMessageBox.information(self, "成功", "注册成功！")
            self.accept()
        else:
            QMessageBox.warning(self, "错误", "注册失败，请检查用户名和密码是否符合要求")