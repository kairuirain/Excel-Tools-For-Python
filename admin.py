from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QListWidget, QMessageBox, QInputDialog)
from PyQt5.QtCore import Qt
from register import RegisterCodeManager

class AdminWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.register_code_manager = RegisterCodeManager()
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI界面"""
        self.setWindowTitle("管理员控制面板")
        self.setFixedWidth(400)
        
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel("管理员控制面板")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 生成注册码按钮
        generate_btn = QPushButton("生成新注册码")
        generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        generate_btn.clicked.connect(self.generate_code)
        layout.addWidget(generate_btn)
        
        # 注册码列表
        self.code_list = QListWidget()
        self.code_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: black;
            }
        """)
        layout.addWidget(self.code_list)
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
    def generate_code(self):
        """生成新的注册码"""
        # 获取有效期
        hours, ok = QInputDialog.getInt(
            self, 
            "设置有效期", 
            "请输入注册码有效期（小时）：",
            value=24,
            min=1,
            max=720  # 最长30天
        )
        
        if not ok:
            return
            
        # 生成注册码
        code = self.register_code_manager.generate_code(valid_hours=hours)
        
        # 添加到列表
        self.code_list.addItem(f"注册码: {code} (有效期: {hours}小时)")
        
        # 复制到剪贴板
        from PyQt5.QtWidgets import QApplication
        QApplication.clipboard().setText(code)
        
        QMessageBox.information(
            self,
            "注册码已生成",
            f"注册码已生成并复制到剪贴板：\n{code}\n\n有效期：{hours}小时"
        )