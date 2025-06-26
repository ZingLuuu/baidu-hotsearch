import pymysql
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv(dotenv_path="Password.env")

class MySqlHelper:
    def __init__(self):
        try:
            self.conn = pymysql.connect(
                host=os.getenv("MYSQL_HOST"),
                user=os.getenv("MYSQL_USER"),
                password=os.getenv("MYSQL_PASSWORD"),
                database=os.getenv("MYSQL_DATABASE"),
                port = int(os.getenv("MYSQL_PORT", 3306)),
                charset='utf8mb4'
            )
            self.cursor = self.conn.cursor()
            print("✅ 数据库连接成功")
        except Exception as e:
            print("数据库连接失败：", e)
            raise

    def execute(self, sql, args=None):
        """执行 INSERT/UPDATE/DELETE"""
        try:
            self.cursor.execute(sql, args)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print("执行失败：", e)

    def query(self, sql, args=None):
        """执行 SELECT 查询"""
        try:
            self.cursor.execute(sql, args)
            return self.cursor.fetchall()
        except Exception as e:
            print("查询失败：", e)
            return None

    def close(self):
        """关闭连接"""
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'conn'):
            self.conn.close()
        print("已断开数据库连接")

# ========== 实际测试使用（可选）==========
if __name__ == "__main__":
    db = MySqlHelper()

    # 示例：查询数据库中已有表名
    result = db.query("SHOW TABLES;")
    for row in result:
        print(row)

    db.close()

