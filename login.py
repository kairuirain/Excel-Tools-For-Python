from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QMessageBox
from PyQt5.QtCore import Qt
from User import UserManager
import json
import os
import base64

def show_login():
    """显示登录窗口并返回登录结果
    
    Returns:
        LoginWindow: 登录窗口实例，包含登录用户信息
    """
    login_window = LoginWindow()
    result = login_window.exec_()
    login_window.is_accepted = (result == QDialog.Accepted)
    return login_window

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.user_manager = UserManager()
        self.config_file = 'login_config.json'
        # 加密密钥
        self._encryption_key = "CXF_KEY"
        self.load_login_config()
        self.init_ui()
        
        # 检查是否需要自动登录
        if hasattr(self, 'auto_login') and self.auto_login:
            # 使用QTimer延迟执行自动登录，确保UI已完全加载
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(500, self.login)

    def _encrypt(self, text):
        """加密文本"""
        if not text:
            return ""
        # 使用异或加密
        encrypted = ''.join(chr(ord(c) ^ ord(self._encryption_key[i % len(self._encryption_key)])) 
                          for i, c in enumerate(text))
        # 转换为base64
        return base64.b64encode(encrypted.encode()).decode()

    def _decrypt(self, encrypted_text):
        """解密文本"""
        if not encrypted_text:
            return ""
        try:
            # 从base64解码
            decoded = base64.b64decode(encrypted_text.encode()).decode()
            # 使用异或解密
            return ''.join(chr(ord(c) ^ ord(self._encryption_key[i % len(self._encryption_key)]))
                         for i, c in enumerate(decoded))
        except:
            return ""

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("登录")
        self.setFixedSize(300, 200)
        
        # 主布局
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # 用户名输入
        username_layout = QHBoxLayout()
        username_label = QLabel("用户名:")
        username_label.setMinimumWidth(80)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        # 设置保存的用户名
        if hasattr(self, 'saved_username') and self.saved_username:
            self.username_input.setText(self.saved_username)
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        main_layout.addLayout(username_layout)
        
        # 密码输入
        password_layout = QHBoxLayout()
        password_label = QLabel("密码:")
        password_label.setMinimumWidth(80)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        # 设置保存的密码
        if hasattr(self, 'saved_password') and self.saved_password:
            self.password_input.setText(self.saved_password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        main_layout.addLayout(password_layout)
        
        # 复选框布局
        checkbox_layout = QHBoxLayout()
        self.remember_pwd_checkbox = QCheckBox("记住密码")
        self.auto_login_checkbox = QCheckBox("自动登录")
        
        # 设置复选框状态
        if hasattr(self, 'saved_username') and self.saved_username:
            self.remember_pwd_checkbox.setChecked(True)
        if hasattr(self, 'auto_login') and self.auto_login:
            self.auto_login_checkbox.setChecked(True)
            
        # 设置自动登录复选框的依赖关系
        self.auto_login_checkbox.stateChanged.connect(self.on_auto_login_changed)
        
        checkbox_layout.addWidget(self.remember_pwd_checkbox)
        checkbox_layout.addWidget(self.auto_login_checkbox)
        main_layout.addLayout(checkbox_layout)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        login_button = QPushButton("登录")
        register_button = QPushButton("注册")
        login_button.clicked.connect(self.login)
        register_button.clicked.connect(self.register)
        button_layout.addWidget(login_button)
        button_layout.addWidget(register_button)
        main_layout.addLayout(button_layout)
        
        # 忘记密码链接
        forgot_layout = QHBoxLayout()
        forgot_layout.addStretch()
        forgot_password_button = QPushButton("忘记密码?")
        forgot_password_button.setStyleSheet("border: none; color: blue; text-decoration: underline;")
        forgot_password_button.setCursor(Qt.PointingHandCursor)
        forgot_password_button.clicked.connect(self.forgot_password)
        forgot_layout.addWidget(forgot_password_button)
        main_layout.addLayout(forgot_layout)

    def login(self):
        """验证用户登录"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "警告", "用户名和密码不能为空")
            return
        
        # 验证用户登录
        user = self.user_manager.login(username, password)
        if user:
            # 保存登录配置
            self.save_login_config()
            self.current_user = user  # 保存当前登录用户
            self.accept()
        else:
            QMessageBox.critical(self, "错误", "用户名或密码错误")

    def register(self):
        """打开注册窗口"""
        from register import RegisterWindow
        register_window = RegisterWindow()
        if register_window.exec_() == QDialog.Accepted:
            QMessageBox.information(self, "提示", "注册成功，请登录")

    def on_auto_login_changed(self, state):
        """自动登录复选框状态改变时的处理"""
        if state and not self.remember_pwd_checkbox.isChecked():
            self.remember_pwd_checkbox.setChecked(True)
            
    def forgot_password(self):
        """处理忘记密码"""
        from PyQt5.QtWidgets import QInputDialog
        
        # 获取用户名
        username, ok = QInputDialog.getText(self, "忘记密码", "请输入您的用户名:")
        if not ok or not username.strip():
            return
            
        # 检查用户是否存在
        user = self.user_manager.get_user_by_username(username.strip())
        if not user:
            QMessageBox.warning(self, "错误", "用户不存在")
            return
            
        # 这里可以实现更复杂的密码重置流程，如发送重置邮件、验证安全问题等
        # 简单起见，我们直接提示用户联系管理员
        QMessageBox.information(
            self, 
            "密码重置", 
            "密码重置请求已收到。\n\n"
            "请联系系统管理员重置您的密码。\n"
            "或者您可以尝试使用其他账号登录。"
        )

    def load_login_config(self):
        """加载登录配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.saved_username = config.get('username', '')
                    # 解密密码
                    encrypted_password = config.get('password', '')
                    self.saved_password = self._decrypt(encrypted_password)
                    self.auto_login = config.get('auto_login', False)
        except Exception as e:
            print(f"加载配置文件出错: {e}")
            
    def save_login_config(self):
        """保存登录配置"""
        try:
            config = {}
            
            # 如果选中了"记住密码"，保存用户名和加密后的密码
            if self.remember_pwd_checkbox.isChecked():
                config['username'] = self.username_input.text().strip()
                # 加密密码
                config['password'] = self._encrypt(self.password_input.text().strip())
            else:
                config['username'] = ''
                config['password'] = ''
                
            # 保存自动登录设置
            config['auto_login'] = self.auto_login_checkbox.isChecked()
            
            # 写入配置文件
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
                
        except Exception as e:
            print(f"保存配置文件出错: {e}")