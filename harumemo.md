# 開発環境に関するメモ書き

## python3 venv

YOLOを入れるためにvenvで仮想環境を入れている
- myenvというファイルが生成されている
- source myenv/bin/activateというコマンドで仮想環境が起動するっぽい
- 仮想環境を終了するときは ```deactivate```コマンド
- よくわからないから調べてね

この仮想環境はそれぞれで作用するため、新たなプロジェクトでは新たにライブラリを入れる必要がある
そのためtkrlyディレクトリにtempenvとrequirements.txtを作成し共通で使いたいライブラリはそれで管理する

そのためpython環境の構築は以下のようになる({project}はプロジェクトの名前など 別にmyenvとかでもよさそう)
``` bash
python3 -m venv {project}env
source ./{project}env/bin/activate
(for windows .\{project}env\Script\activate)
cp /mnt/c/Users/tkrly/requirements.txt requirements.txt
pip3 install -r requirements.txt
```

テンプレートを変更した場合、このコマンドでrequirements.txtを再生成
``` bash
cd /mnt/c/Users/tkrly
source ./tempenv/bin/activate
~pip install などでライブラリ構成を変更~
pip3 freeze > requirements.txt
```