import pymysql

class DB:
    def getConnection():

        # pymysqlにconnect()で接続要求
        try:
            conn = pymysql.connect(
            host="db",
            db="chatapp",
            user="testuser",
            password="testuser",
            charset="utf8",
            cursorclass=pymysql.cursors.DictCursor #結果をDict形式で取得
        )
            return conn
        except (ConnectionError):
            print("コネクションエラーです")
            conn.close()
