from flask import Flask, request, redirect, render_template, session, flash, abort
from models import dbConnect
from util.user import User
from datetime import timedelta
import hashlib
import uuid
import re


app = Flask(__name__)
app.secret_key = uuid.uuid4().hex
app.permanent_session_lifetime = timedelta(days=30)


# サインアップページの表示
@app.route('/signup')
def signup():
    return render_template('registration/signup.html')


# サインアップ処理
@app.route('/signup', methods=['POST'])
def userSignup():
    name = request.form.get('name')
    email = request.form.get('email')
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')

    pattern = "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

    if name == '' or email =='' or password1 == '' or password2 == '':
        flash('空のフォームがあるようです')
    elif password1 != password2:
        flash('二つのパスワードの値が違っています')
    elif re.match(pattern, email) is None:
        flash('正しいメールアドレスの形式ではありません')
    else:
        uid = uuid.uuid4()
        password = hashlib.sha256(password1.encode('utf-8')).hexdigest()
        user = User(uid, name, email, password)
        DBuser = dbConnect.getUser(email)

        if DBuser != None:
            flash('既に登録されているようです')
        else:
            dbConnect.createUser(user)
            UserId = str(uid)
            session['uid'] = UserId
            return redirect('/')
    return redirect('/signup')


# ログインページの表示
@app.route('/login')
def login():
    return render_template('registration/login.html')


# ログイン処理
@app.route('/login', methods=['POST'])
def userLogin():
    email = request.form.get('email')
    password = request.form.get('password')

    if email =='' or password == '':
        flash('空のフォームがあるようです')
    else:
        user = dbConnect.getUser(email)
        if user is None:
            flash('このユーザーは存在しません')
        else:
            hashPassword = hashlib.sha256(password.encode('utf-8')).hexdigest()
            if hashPassword != user["password"]:
                flash('パスワードが間違っています！')
            else:
                session['uid'] = user["uid"]
                return redirect('/')
    return redirect('/login')


# ログアウト
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# チャンネル一覧ページの表示
@app.route('/')
def index():
    uid = session.get("uid")
    if uid is None:
        return redirect('/login')
    else:
        channels = dbConnect.getChannelAll() #from models import dbConnect > 関数getChannelAll()を実行…channelsのデータ全てを抽出し、Python実行端末にもってくる
        channels.reverse() # リストオブジェクト自体の要素が逆順で更新される
    return render_template('index.html', channels=channels, uid=uid) 
    # フロントindex.htmlに、channels,uidを引数として渡す
    # render_template…フロント側でpythonの処理を書き込むことができる。その時に、バックエンドから引数を渡せるメソッド。


# チャンネルの追加

# @xxx…デコレータ デコレータとは、関数やクラスの前後に特定の処理を追加できる機能。①関数を受け取り②関数を返す③関数である

@app.route('/', methods=['POST'])

# @app.route() で、どのURLにどのメソッドでアクセスされると、どのメソッドを呼び出すかを指定する。
# route()…ルーティング URLとアプリケーション（サーバ側）の処理を紐づける。クライアントは実行したいURLに対してリクエストを投げ、サーバではそのURLに対応する処理が実行され、クライアントに何等かの結果が返される。

# '/delete/<cid>'に対してPOSTでアクセスされたら、関数update_channelを実行する。
# POST…自分のPCから渡したいデータがある時、POST

def add_channel():
    uid = session.get('uid')
    if uid is None:
        return redirect('/login')
    channel_name = request.form.get('channelTitle') # フロント add-channel.htmlから、nameタグchannelTitleを取得
    channel = dbConnect.getChannelByName(channel_name) # from models import dbConnect > 関数getChannelByNameを実行…# テーブルchannels から、formで取得したname="channelTitle"に一致するデータを抽出
    if channel == None: # 一致するchannelがない時
        channel_description = request.form.get('channelDescription') # フロント add-channel.htmlから、nameタグchannelDescriptionを取得
        dbConnect.addChannel(uid, channel_name, channel_description) # models.py > 関数addChannelを実行、引数uid, channel_name, channel_description
        return redirect('/')
    else:
        error = '既に同じ名前のチャンネルが存在しています'
        return render_template('error/error.html', error_message=error)


# ★チャンネルの更新★

# init.sqlについて
# 外部キー…foreign key(<項目名>) references <繋ぐテーブル名>(<繋ぐテーブルの項目名>)

# @xxx…デコレータ デコレータとは、関数やクラスの前後に特定の処理を追加できる機能。①関数を受け取り②関数を返す③関数である

@app.route('/update_channel', methods=['POST'])

# @app.route() で、どのURLにどのメソッドでアクセスされると、どのメソッドを呼び出すかを指定する。
# route()…ルーティング URLとアプリケーション（サーバ側）の処理を紐づける。クライアントは実行したいURLに対してリクエストを投げ、サーバではそのURLに対応する処理が実行され、クライアントに何等かの結果が返される。

# '/delete/<cid>'に対してPOSTでアクセスされたら、関数update_channelを実行する。

def update_channel():
    uid = session.get("uid")
    if uid is None:
        return redirect('/login')

    cid = request.form.get('cid')
    channel_name = request.form.get('channelTitle')
    channel_description = request.form.get('channelDescription')

    dbConnect.updateChannel(uid, channel_name, channel_description, cid)
    return redirect('/detail/{cid}'.format(cid = cid))


# チャンネルの削除

# init.sqlについて
# 外部キー…foreign key(<項目名>) references <繋ぐテーブル名>(<繋ぐテーブルの項目名>)

# @xxx…デコレータ デコレータとは、関数やクラスの前後に特定の処理を追加できる機能。①関数を受け取り②関数を返す③関数である

@app.route('/delete/<cid>')

# @app.route() で、どのURLにどのメソッドでアクセスされると、どのメソッドを呼び出すかを指定する。
# route()…ルーティング URLとアプリケーション（サーバ側）の処理を紐づける。クライアントは実行したいURLに対してリクエストを投げ、サーバではそのURLに対応する処理が実行され、クライアントに何等かの結果が返される。

# '/delete/<cid>'に対してGET(Flaskのデフォルトメソッド)でアクセスされたら、関数delete_channelを実行する。

def delete_channel(cid):
    uid = session.get("uid") # sessionにユーザIDを格納する。 session…ローカルの簡易データベース
    if uid is None: # uidが空の場合＝ログイン認証切れの場合
        return redirect('/login') # /loginにリダイレクト
    else:
        channel = dbConnect.getChannelById(cid) #models.py > dbConnect から関数getChannelByIdの結果を格納…cidに一致するチャンネル1データのみを持ってくる
        if channel["uid"] != uid: # 変数channnelのキーuid ≠ sessionから取得したuidの時
            flash('チャンネルは作成者のみ削除可能です') #文字表示
            return redirect ('/') # '/delete/<cid>'にリダイレクト
        else:
            dbConnect.deleteChannel(cid) #models.py > dbConnect から関数deleteChannelを実行…# init.sql > channels からチャンネル削除
            channels = dbConnect.getChannelAll() #models.py > dbConnect から関数deleteChannelを実行…channelsのデータ全てを抽出
            return redirect('/') # '/delete/<cid>'にリダイレクト


# ★チャンネル詳細ページの表示★

# @xxx…デコレータ デコレータとは、関数やクラスの前後に特定の処理を追加できる機能。①関数を受け取り②関数を返す③関数である

@app.route('/detail/<cid>')

# @app.route() で、どのURLにどのメソッドでアクセスされると、どのメソッドを呼び出すかを指定する。
# route()…ルーティング URLとアプリケーション（サーバ側）の処理を紐づける。クライアントは実行したいURLに対してリクエストを投げ、サーバではそのURLに対応する処理が実行され、クライアントに何等かの結果が返される。

# '/detail/<cid>'に対してGET(Flaskのデフォルトメソッド)でアクセスされたら、関数detailを実行する。

def detail(cid):
    uid = session.get("uid") #sessionにユーザIDを格納する。 session…ローカルの簡易データベース
    if uid is None: # uidが空の場合＝ログイン認証切れの場合
        return redirect('/login') # /loginにリダイレクト

    cid = cid
    channel = dbConnect.getChannelById(cid) #models.py > dbConnect から関数getChannelByIdの結果を格納…cidに一致するチャンネル1データのみを持ってくる
    messages = dbConnect.getMessageAll(cid) #models.py > dbConnect から関数getMessageAllの結果を格納…cidに一致するチャンネルの、自分の全メッセージを持ってくる

    return render_template('detail.html', messages=messages, channel=channel, uid=uid) # htmlの中にpythonを書くことができる。その部分に、抽出できた値を渡してあげている。


# メッセージの投稿

# @xxx…デコレータ デコレータとは、関数やクラスの前後に特定の処理を追加できる機能。①関数を受け取り②関数を返す③関数である。

@app.route('/message', methods=['POST']) 

# @app.route() で、どのURLにどのメソッドでアクセスされると、どのメソッドを呼び出すかを指定する。
# route()…ルーティング URLとアプリケーション（サーバ側）の処理を紐づける。クライアントは実行したいURLに対してリクエストを投げ、サーバではそのURLに対応する処理が実行され、クライアントに何等かの結果が返される。

# methods=['HTTPメソッド']…クライアントがサーバにしてほしいことを依頼する手段。
# POST…データの送信(主に新規作成) でアクセスされたら、以下の関数add_message()を実行する。
# オブジェクトを作る→メソッドを使う の流れが必須。オブジェクト…データと関連するメソッドをまとめたもの。

def add_message(): # 関数：メッセージの投稿
    uid = session.get("uid") #変数uidに、deteal.html >form > name="cid" value="{{ channel.id }}を入れる。 session…ローカルの簡易データベース
    if uid is None: # 変数uidが空のとき
        return redirect('/login') # /loginページにリダイレクトする。

    # WEBページ側からPython側に値を渡す方法として、GETとPOSTがある。
    # request.formはPOST送信された値を取得するプロパティ
    # request.args.getはクエリパラメータの値を取得する関数

    message = request.form.get('message') # 変数messageに、POSTリクエストのパラメータ(deteal.html >form >message)を取得し、入れる。なければデフォルト値Noneを返す。
    cid = request.form.get('cid') # 変数cidに、POSTパラメータ(deteal.html >form >name="cid" value="{{ channel.id }})を取得し、入れる。

    if message: # DB.messagesの'message'の取得に成功する
        dbConnect.createMessage(uid, cid, message) #関数createMessage(引数uid, cid, message)実行、詳細はmodels.py

    return redirect('/detail/{cid}'.format(cid = cid)) 
    # 取得したチャンネル(個別)ルームへリダイレクト
    # format関数…Pyhonで変数の文字列への埋め込みに使う。
    # {h1}.format(h1=変数1)…キーワード引数指定。引数に名前を付けて、その名前で指定する。


# メッセージの削除
@app.route('/delete_message', methods=['POST'])

# @app.route() で、どのURLにどのメソッドでアクセスされると、どのメソッドを呼び出すかを指定する。
# route()…ルーティング URLとアプリケーション（サーバ側）の処理を紐づける。クライアントは実行したいURLに対してリクエストを投げ、サーバではそのURLに対応する処理が実行され、クライアントに何等かの結果が返される。

# methods=['HTTPメソッド']…クライアントがサーバにしてほしいことを依頼する手段。
# POST…データの送信(主に新規作成) でアクセスされたら、以下の関数delete_message()を実行する。

def delete_message():
    uid = session.get("uid") #変数uidに、sessionのuidを読み込んで入れる。 session…ローカルの簡易データベース
    if uid is None: # 変数uidが空のとき
        return redirect('/login') # /loginページにリダイレクトする。

    # WEBページ側からPython側に値を渡す方法として、GETとPOSTがある。
    # request.formはPOST送信された値を取得するプロパティ
    # request.args.getはクエリパラメータの値を取得する関数

    message_id = request.form.get('message_id') # 変数message_idに、POSTパラメータ(フロントのformタグ>name'message_id')を取得し、入れる。
    cid = request.form.get('cid') # 変数cidに、POSTパラメータ(フロントのformタグ>name'cid')を取得し、入れる。

    if message_id: # DB.messagesの'message_id'の取得に成功する
        dbConnect.deleteMessage(message_id) #関数deleteMessage(引数message_id)実行、詳細はmodels.py

    return redirect('/detail/{cid}'.format(cid = cid))
    # 取得したチャンネル(個別)ルームへリダイレクト
    # format関数…Pyhonで変数の文字列への埋め込みに使う。
    # {h1}.format(h1=変数1)…キーワード引数指定。引数に名前を付けて、その名前で指定する。


@app.errorhandler(404)

# @app.route() で、どのURLにどのメソッドでアクセスされると、どのメソッドを呼び出すかを指定する。
# errorhandler()デコレーターを使い、エラーハンドラーを登録し、登録されている場合は対応関数を呼び出す。

def show_error404(error):
    return render_template('error/404.html'),404 # render_template()…動的にテンプレートの内容を変更する。テンプレートのHTMLファイルは、デフォルトでアプリケーションのpythonファイルと同じ階層のtemplatesフォルダ内に配置


@app.errorhandler(500)
def show_error500(error):
    return render_template('error/500.html'),500

if __name__ == '__main__': # そのPythonファイルが「pythonファイル名.py」という形で実行されているかどうか」を判定する。
    app.run(host="0.0.0.0", debug=False) # 開発Webサーバーを起動する、デバッグモードはオフ