import json
import os
import hashlib
import re
from typing import Dict, Optional

class User:
    def __init__(self, username: str, password: str, role: str = "user"):
        self.username = username
        self._password = self._encrypt_password(password)
        self.role = role
    
    @staticmethod
    def _encrypt_password(password: str) -> str:
        """使用PBKDF2加密密码"""
        salt = os.urandom(16).hex()
        return hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt.encode(),
            100000
        ).hex() + ':' + salt
    
    def verify_password(self, password: str) -> bool:
        """验证密码是否正确"""
        if ':' not in self._password:
            # 兼容旧密码
            return self._password == hashlib.sha256(password.encode()).hexdigest()
            
        password_hash, salt = self._password.split(':')
        new_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt.encode(),
            100000
        ).hex()
        return password_hash == new_hash
    
    def to_dict(self) -> Dict:
        """将用户数据转换为字典"""
        return {
            'username': self.username,
            'password': self._password,
            'role': self.role
        }

class UserManager:
    def __init__(self, db_file: str = "users.json"):
        self.db_file = db_file
        self.users = {}  # username: User
        self._load_users()
    
    def _is_first_run(self) -> bool:
        """检查是否是第一次运行系统"""
        step_file = "auth/step.txt"
        
        # 确保auth目录存在
        if not os.path.exists("auth"):
            os.makedirs("auth")
            
        # 检查step.txt是否存在
        if not os.path.exists(step_file):
            # 第一次运行，创建step.txt并写入1
            with open(step_file, 'w') as f:
                f.write("1")
            return True
        
        # 读取当前运行次数
        try:
            with open(step_file, 'r') as f:
                step = int(f.read().strip())
                
            # 更新运行次数
            with open(step_file, 'w') as f:
                f.write(str(step + 1))
                
            # 如果step为1，则是第一次运行
            return step == 1
        except:
            # 文件损坏或格式错误，视为非首次运行
            with open(step_file, 'w') as f:
                f.write("2")  # 设为第二次运行
            return False
    
    def _load_users(self):
        """从文件加载用户数据"""
        is_first_run = self._is_first_run()
        
        if not os.path.exists(self.db_file):
            # 只在第一次运行时创建默认管理员账户
            if is_first_run:
                admin = User("admin", "admin123", "admin")
                self.users[admin.username] = admin
                self._save_users()
            return
        
        try:
            with open(self.db_file, 'r') as f:
                data = json.load(f)
                for user_data in data.values():
                    user = User(
                        user_data['username'],
                        "",  # 密码从文件读取，不需要明文
                        user_data['role']
                    )
                    user._password = user_data['password']  # 设置加密后的密码
                    self.users[user.username] = user
        except (json.JSONDecodeError, FileNotFoundError):
            # 文件损坏或不存在，只在第一次运行时创建默认管理员账户
            if is_first_run:
                admin = User("admin", "admin123", "admin")
                self.users[admin.username] = admin
                self._save_users()
    
    def _save_users(self):
        """保存用户数据到文件"""
        data = {username: user.to_dict() for username, user in self.users.items()}
        with open(self.db_file, 'w') as f:
            json.dump(data, f, indent=4)
    
    @staticmethod
    def _validate_username(username: str) -> bool:
        """验证用户名有效性
        规则:
        - 长度4-20个字符
        - 只能包含字母、数字和下划线
        - 不能以数字开头
        """
        if not username or len(username) < 4 or len(username) > 20:
            return False
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', username):
            return False
        return True
    
    @staticmethod
    def _validate_password(password: str) -> bool:
        """验证密码强度"""
        if len(password) < 8:
            return False
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'[0-9]', password):
            return False
        return True

    def register(self, username: str, password: str, role: str = "user") -> bool:
        """注册新用户"""
        if not self._validate_username(username):
            return False
            
        if not self._validate_password(password):
            return False
            
        if username in self.users:
            return False
        
        self.users[username] = User(username, password, role)
        self._save_users()
        return True
    
    def change_password(self, username: str, new_password: str) -> bool:
        """修改用户密码
        Args:
            username: 要修改密码的用户名
            new_password: 新密码
        Returns:
            bool: 修改是否成功
        """
        if not self._validate_password(new_password):
            return False
            
        user = self.users.get(username)
        if not user:
            return False
            
        # 使用User类的加密方法更新密码
        user._password = User._encrypt_password(new_password)
        self._save_users()
        return True
    
    def login(self, username: str, password: str) -> Optional[User]:
        """用户登录验证"""
        user = self.users.get(username)
        if user and user.verify_password(password):
            return user
        return None
    
    def is_admin(self, user: User) -> bool:
        """检查用户是否为管理员"""
        return user.role == "admin" if user else False
        
    def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户对象
        
        Args:
            username: 要查找的用户名
            
        Returns:
            User: 找到的用户对象，如果不存在则返回None
        """
        return self.users.get(username)