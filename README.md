# building-estimator-ai

## コーディングルール
基本的にイシューやプルリクエストを利用する
新しいコードを書きたいときは  -> Issue
コードの修正など既にできたコードについて議論する場合 -> Pull requests

1. コードは必ず```コードブロックで囲む
2. コードブロックの先頭に必ずファイル名を書く(説明用など具体的なファイルが存在しない場合は除く)
3. ファイルの作成や全変更か修正、部分変更は必ず明示する
4. 別のファイルや同じファイルでも比較の場合はコードブロックを分ける
5. コメントの編集は誤字修正などの限られた場面以外では使わず、新しい情報は新しいコメントに記載する

## 現状のbackendのファイル構成

backend
    - app
        - models
            - upload_models.py
        - routers
            - __init__.py
            - estimate.py
            - extract_info.py
            - land_price_loader.py
            - land_price_models.py
            - land_price.py
        - services
            - estimate_logic
                - __init__.py
                - estimate_logic.py
                - land_price_models.py
            - __init__.py
            - auto_estimate.py
            - esimator.py
            - land_price_models.py
            - old_land_price_data.py
        - __init__.py
        - main.py
        - models.py