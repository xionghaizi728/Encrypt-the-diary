from PyQt6.QtWidgets import QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox, QDialog, QListWidget, QInputDialog, QHBoxLayout
from PyQt6.QtCore import QDate
import hashlib
import os

class DiaryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("日记本")
        self.resize(800, 600)
        self.encryption_key = ""  # 初始化加密密钥为空
        
        # 应用样式表
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTextEdit {
                background-color: white;
                color: black;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        # 日记存储目录
        self.diary_dir = "C:\\Public\\Diaries"
        if not os.path.exists(self.diary_dir):
            os.makedirs(self.diary_dir)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        self.layout = QVBoxLayout(central_widget)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(20)
        
        # 写日记区域
        self.diary_edit = QTextEdit()
        self.diary_edit.setPlaceholderText("在这里写下你的日记...")
        self.diary_edit.setMinimumHeight(400)
        self.layout.addWidget(self.diary_edit)
        
        # 按钮区域
        button_layout = QVBoxLayout()
        button_layout.setSpacing(10)
        
        self.save_btn = QPushButton("保存日记")
        self.save_btn.clicked.connect(self.save_diary)
        button_layout.addWidget(self.save_btn)
        
        self.view_btn = QPushButton("查看日记")
        self.view_btn.clicked.connect(self.view_diaries)
        button_layout.addWidget(self.view_btn)
        
        self.setting_btn = QPushButton("设置密钥")
        self.setting_btn.clicked.connect(self.set_encryption_key)
        button_layout.addWidget(self.setting_btn)
        
        self.layout.addLayout(button_layout)
    
    def save_diary(self):
        """保存日记到文件，使用AES加密"""
        content = self.diary_edit.toPlainText()
        if not content:
            QMessageBox.warning(self, "警告", "日记内容不能为空！")
            return
        
        # 使用Fernet加密
        from cryptography.fernet import Fernet
        import base64
        import hashlib
        
        if not hasattr(self, 'encryption_key') or not self.encryption_key:
            QMessageBox.warning(self, "警告", "请先在设置中配置加密密钥！")
            return
            
        # 使用SHA256生成固定长度密钥
        key = hashlib.sha256(self.encryption_key.encode()).digest()
        fernet_key = base64.urlsafe_b64encode(key)
        fernet = Fernet(fernet_key)
        
        encrypted = fernet.encrypt(content.encode()).decode('utf-8')
        
        # 以日期为文件名
        filename = QDate.currentDate().toString("yyyy-MM-dd") + ".txt"
        
        # 处理重名文件
        counter = 1
        base_name, ext = os.path.splitext(filename)
        while os.path.exists(os.path.join(self.diary_dir, filename)):
            counter += 1
            filename = f"{base_name}({counter}){ext}"
            
        filepath = os.path.join(self.diary_dir, filename)
        
        with open(filepath, "w") as f:
            f.write(encrypted)
        
        QMessageBox.information(self, "成功", "日记已加密保存！")
        self.diary_edit.clear()
    
    def view_diaries(self):
        """查看已保存的日记列表"""
        diaries = os.listdir(self.diary_dir)
        if not diaries:
            QMessageBox.information(self, "提示", "还没有保存过日记！")
            return
        

        
        dialog = QDialog(self)
        dialog.setWindowTitle("日记列表")
        dialog.resize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        self.diary_list = QListWidget()
        self.diary_list.addItems(diaries)
        layout.addWidget(self.diary_list)
        
        button_layout = QHBoxLayout()
        
        view_btn = QPushButton("查看")
        view_btn.clicked.connect(lambda: self.view_selected_diary(dialog))
        button_layout.addWidget(view_btn)
        
        delete_btn = QPushButton("删除")
        delete_btn.clicked.connect(lambda: self.delete_diary(dialog))
        button_layout.addWidget(delete_btn)
        
        rename_btn = QPushButton("重命名")
        rename_btn.clicked.connect(lambda: self.rename_diary(dialog))
        button_layout.addWidget(rename_btn)
        
        layout.addLayout(button_layout)
        dialog.exec()
        
    def view_selected_diary(self, dialog):
        """查看选中的日记"""
        selected = self.diary_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "警告", "请先选择一篇日记！")
            return
            
        filename = selected.text()
        filepath = os.path.join(self.diary_dir, filename)
        
        try:
            with open(filepath, "r") as f:
                encrypted_data = f.read()
                
            if not hasattr(self, 'encryption_key') or not self.encryption_key:
                QMessageBox.warning(self, "警告", "请先在设置中配置加密密钥！")
                return
                
            # 解密内容
            from cryptography.fernet import Fernet
            import base64
            import hashlib
            
            # 使用SHA256生成固定长度密钥
            key = hashlib.sha256(self.encryption_key.encode()).digest()
            fernet_key = base64.urlsafe_b64encode(key)
            fernet = Fernet(fernet_key)
            
            decrypted = fernet.decrypt(encrypted_data.encode()).decode('utf-8')
            
            # 显示解密后的内容
            view_dialog = QDialog(self)
            view_dialog.setWindowTitle(f"查看日记 - {filename}")
            view_dialog.resize(600, 400)
            
            layout = QVBoxLayout(view_dialog)
            
            content_edit = QTextEdit()
            content_edit.setReadOnly(False)  # 允许编辑
            content_edit.setPlainText(decrypted)
            
            # 添加保存和导出按钮
            button_layout = QHBoxLayout()
            
            save_btn = QPushButton("保存修改")
            save_btn.clicked.connect(lambda: self.save_edited_diary(content_edit.toPlainText(), filename, view_dialog))
            button_layout.addWidget(save_btn)
            
            export_btn = QPushButton("导出明文")
            export_btn.clicked.connect(lambda: self.export_plaintext(content_edit.toPlainText(), filename))
            button_layout.addWidget(export_btn)
            
            layout.addWidget(content_edit)
            layout.addLayout(button_layout)
            
            view_dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法读取日记文件: {str(e)}")
    
    def delete_diary(self, dialog):
        """删除选中的日记"""
        selected = self.diary_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "警告", "请先选择一篇日记！")
            return
            
        filename = selected.text()
        reply = QMessageBox.question(self, "确认", f"确定要删除日记 {filename} 吗？",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                os.remove(os.path.join(self.diary_dir, filename))
                self.diary_list.takeItem(self.diary_list.row(selected))
                QMessageBox.information(self, "成功", "日记已删除！")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法删除日记: {str(e)}")
    
    def rename_diary(self, dialog):
        """重命名选中的日记"""
        selected = self.diary_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "警告", "请先选择一篇日记！")
            return
            
        old_name = selected.text()
        new_name, ok = QInputDialog.getText(self, "重命名日记", "请输入新的文件名:", text=old_name)
        
        if ok and new_name and new_name != old_name:
            try:
                old_path = os.path.join(self.diary_dir, old_name)
                new_path = os.path.join(self.diary_dir, new_name)
                os.rename(old_path, new_path)
                selected.setText(new_name)
                QMessageBox.information(self, "成功", "日记已重命名！")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法重命名日记: {str(e)}")
                
    def save_edited_diary(self, content, filename, dialog):
        """保存编辑后的日记"""
        if not content:
            QMessageBox.warning(self, "警告", "日记内容不能为空！")
            return
            
        try:
            # 使用Fernet加密
            from cryptography.fernet import Fernet
            import base64
            import hashlib
            
            if not hasattr(self, 'encryption_key') or not self.encryption_key:
                QMessageBox.warning(self, "警告", "请先在设置中配置加密密钥！")
                return
                
            # 使用SHA256生成固定长度密钥
            key = hashlib.sha256(self.encryption_key.encode()).digest()
            fernet_key = base64.urlsafe_b64encode(key)
            fernet = Fernet(fernet_key)
            
            encrypted = fernet.encrypt(content.encode()).decode('utf-8')
            
            filepath = os.path.join(self.diary_dir, filename)
            
            with open(filepath, "w") as f:
                f.write(encrypted)
            
            QMessageBox.information(self, "成功", "日记修改已保存！")
            dialog.close()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法保存日记: {str(e)}")
            
    def export_plaintext(self, content, filename):
        """导出日记为明文文件"""
        try:
            # 获取桌面路径
            desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
            export_path = os.path.join(desktop, f"{filename}.txt")
            
            with open(export_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            QMessageBox.information(self, "成功", f"日记已导出到桌面: {export_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法导出日记: {str(e)}")
                
    def set_encryption_key(self):
        """设置加密密钥"""
        key, ok = QInputDialog.getText(self, "设置加密密钥", "请输入加密密钥(任意长度):", text=self.encryption_key)
        if ok and key:
            self.encryption_key = key
            QMessageBox.information(self, "成功", "加密密钥已设置！")

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    window = DiaryApp()
    window.show()
    sys.exit(app.exec())
