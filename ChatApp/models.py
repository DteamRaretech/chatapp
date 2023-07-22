# import:モジュール全体を利用する from:モジュールの一部(関数や変数)を利用する
import pymysql # import(モジュール名) pymysqlライブラリを取り込む
from util.DB import DB # モジュール：util>DB.py から 要素：class DBを持ってくる


class dbConnect: # pythonでmysqlに接続するクラスを作成 ※濃緑色はimportした関数等
    def createUser(user): # 関数：ユーザ作成
        try: #例外が発生する可能性のある処理を記述→例外処理を捕捉するとexcept節の動作へ
            conn = DB.getConnection() # DBに接続する
            cur = conn.cursor() # mysqlからカーソルを取り出し、sql文を発行できるようにする
            sql = "INSERT INTO users (uid, user_name, email, password) VALUES (%s, %s, %s, %s);" # SQLを動的に作成
            cur.execute(sql, (user.uid, user.name, user.email, user.password)) # SQLを実行(この時点では処理行数を返すだけ)
            conn.commit() # DBと接続したOBJに対してINSERTの処理後、コミット(更新確定)
        except Exception as e: #except 例外名 as 変数名、Exceptionはすべての組み込み例外の基底クラス(非推奨)
            print(e + 'が発生しています')
            abort(500)
        finally: # 例外処理の有無に関わらず、常に最後に行う処理
            cur.close() # コネクタをクローンし全ての処理が完了


    def getUserId(email): # 関数：ユーザemailをもとにユーザID取得
        try:
            conn = DB.getConnection()
            cur = conn.cursor()
            sql = "SELECT uid FROM users WHERE email=%s;"
            cur.execute(sql, (email))
            id = cur.fetchone()
            return id # try→finally→try内のreturnの処理順
        except Exception as e:
            print(e + 'が発生しています')
            abort(500)
        finally:
            cur.close()


    def getUser(email):
        try:
            conn = DB.getConnection()
            cur = conn.cursor()
            sql = "SELECT * FROM users WHERE email=%s;"
            cur.execute(sql, (email))
            user = cur.fetchone()
            return user
        except Exception as e:
            print(e + 'が発生しています')
            abort(500)
        finally:
            cur.close()


    def getChannelAll():
        try:
            conn = DB.getConnection()
            cur = conn.cursor()
            sql = "SELECT * FROM channels;" # channelsのデータ全てを抽出
            cur.execute(sql)
            channels = cur.fetchall() # 全てのデータをPython実行端末にもってくる
            return channels
        except Exception as e:
            print(e + 'が発生しています')
            abort(500)
        finally:
            cur.close()


    def getChannelById(cid):
        try:
            conn = DB.getConnection()
            cur = conn.cursor()
            sql = "SELECT * FROM channels WHERE id=%s;" # init.sql > channelsテーブルのIDをすべて取得
            cur.execute(sql, (cid)) # SQLを実行(この時点では処理行数を返すだけ、引数はcid)
            channel = cur.fetchone() # DB(表)にカーソルを動かし、1行のみのデータを持ってくる
            return channel
        except Exception as e:
            print(e + 'が発生しています')
            abort(500)
        finally:
            cur.close()


    def getChannelByName(channel_name):
        try:
            conn = DB.getConnection()
            cur = conn.cursor()
            sql = "SELECT * FROM channels WHERE name=%s;" # テーブルchannels から、formで取得したname="channelTitle"に一致するデータを抽出
            cur.execute(sql, (channel_name))
            channel = cur.fetchone() # DB(表)にカーソルを動かし、1行のみのデータを持ってくる
            return channel
        except Exception as e:
            print(e + 'が発生しています')
            abort(500)
        finally:
            cur.close()


    def addChannel(uid, newChannelName, newChannelDescription):
        try:
            conn = DB.getConnection()
            cur = conn.cursor()
            sql = "INSERT INTO channels (uid, name, abstract) VALUES (%s, %s, %s);" # テーブルchannelsにuid, name, abstractを追加
            cur.execute(sql, (uid, newChannelName, newChannelDescription))
            conn.commit()
        except Exception as e:
            print(e + 'が発生しています')
            abort(500)
        finally:
            cur.close()


    def getChannelByName(channel_name):
        try:
            conn = DB.getConnection()
            cur = conn.cursor()
            sql = "SELECT * FROM channels WHERE name=%s;"
            cur.execute(sql, (channel_name))
            channel = cur.fetchone()
        except Exception as e:
            print(e + 'が発生しました')
            abort(500)
        finally:
            cur.close()
            return channel


    def updateChannel(uid, newChannelName, newChannelDescription, cid):
        try:
            conn = DB.getConnection()
            cur = conn.cursor()
            sql = "UPDATE channels SET uid=%s, name=%s, abstract=%s WHERE id=%s;"
            cur.execute(sql, (uid, newChannelName, newChannelDescription, cid))
            conn.commit()
        except Exception as e:
            print(e + 'が発生しました')
            abort(500)
        finally:
            cur.close()


    #deleteチャンネル関数
    def deleteChannel(cid):
        try:
            conn = DB.getConnection()
            cur = conn.cursor()
            sql = "DELETE FROM channels WHERE id=%s;" # init.sql > channels からチャンネル削除
            cur.execute(sql, (cid))
            conn.commit()
        except Exception as e:
            print(e + 'が発生しています')
            abort(500)
        finally:
            cur.close()


    def getMessageAll(cid):

        try:
            conn = DB.getConnection()
            cur = conn.cursor()
            sql = "SELECT id,u.uid, user_name, message FROM messages AS m INNER JOIN users AS u ON m.uid = u.uid WHERE cid = %s;"
            # 以下の構文でテーブルの内部結合を実施…内部結合とは、両方のテーブルに存在するデータを結合して抽出すること。
            # FROM テーブル名1 INNER JOIN テーブル名2 ON 結合条件;
            # テーブル1.messagesをm、テーブル2.usersをuと言い換える。messageテーブルのuid=usersテーブルのuidとなるのデータを結合して抽出。cidは動的。

            cur.execute(sql, (cid)) # SQLを実行(この時点では処理行数を返すだけ、引数はcid)
            messages = cur.fetchall() # sqlで抽出できた、全てのデータをPython実行端末にもってくる
            return messages
        except Exception as e:
            print(e + 'が発生しています')
            abort(500)
        finally:
            cur.close()


    def createMessage(uid, cid, message): # 関数createMessage(引数はDB.messagesのuid,cid,message)
    # try..except..構文でエラーの補足 finally..最後の必須処理
        try:
            conn = DB.getConnection() # DB.pyの関数getConnectionを、変数connに入れる
            cur = conn.cursor() # 変数connの接続からカーソルを取り出し、sql文を発行できるようにする。
            sql = "INSERT INTO messages(uid, cid, message) VALUES(%s, %s, %s)" # DB.messagesの項目(uid,cid,message)に値を追加。
            cur.execute(sql, (uid, cid, message)) #  SQLを実行(この時点では処理行数を返すだけ)
            conn.commit() # DBと接続したOBJに対してINSERTの処理後、コミット(更新確定)
        except Exception as e: #except 例外名 as 変数名、Exceptionはすべての組み込み例外の基底クラス→これを'e'という変数で表す
            print(e + 'が発生しています')
            abort(500)
        finally:
            cur.close() # コネクタをクローンし全ての処理が完了


    def deleteMessage(message_id): # 関数deleteMessage(引数はDB.messagesのmessage_id) ※この時点では、'message_id'は仮引数なので、わかりやすく名付けているだけの空の箱。

        # Connection があれば、 Cursor オブジェクトを作りその execute() メソッドを呼んで SQL コマンドを実行することができる。
        try:
            conn = DB.getConnection() # DB.pyの関数getConnectionを、変数connに入れる。アプリとmysqlは別リソースなので、これをつなぐトンネルを作る。
            cur = conn.cursor() # コネクションの中にカーソルを作成…リレーショナルDBの中身を1行ずつ見るために動かす、カーソルを作っている。
            sql = "DELETE FROM messages WHERE id=%s;" # DB.messageからデータ削除
            cur.execute(sql, (message_id)) # execute()にSQL文を渡すことでどんなSQLも実行可能。引数はDB.messagesのmessage_id
            conn.commit() # DBと接続したOBJに対してDELETEの処理後、コミット(更新確定)
        except Exception as e: # 例外を変数eと名付ける
            print(e + 'が発生しています')
            abort(500) # 500エラーページに飛ばす
        finally:
            cur.close() # コネクタをクローンし全ての処理が完了
