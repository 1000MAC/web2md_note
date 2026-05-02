from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from markdownify import markdownify as md
import re
import time

def save_note_manual_trigger(url):
    chrome_options = Options()
    # 画面を表示して操作できるようにする
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        # 1. ログインページへ移動
        driver.get("https://note.com/login")
        print("\n" + "="*50)
        print("1. 表示されたブラウザでログインを完了させてください。")
        print("2. 完了後、このターミナルに戻って Enterキー を押してください...")
        print("="*50 + "\n")

        # ここでユーザーの入力を待つ
        input(">>> ログインが終わったらEnterを押してください...")

        # 2. 目的の記事ページへ移動
        print(f"記事を取得中: {url}")
        driver.get(url)
        time.sleep(5) # 記事の読み込み待ち

        # 3. 本文の抽出
        title = driver.title.replace("｜note", "").strip()
        
        # 有料記事の全文が展開されている要素を取得
        # ログイン済みであれば article タグ内に全文が入ります
        try:
            content_element = driver.find_element(By.TAG_NAME, "article")
            html_content = content_element.get_attribute('innerHTML')
            markdown_text = md(html_content, heading_style="ATX")

            # 4. 保存
            filename = re.sub(r'[\\/:*?"<>|]', '_', title) + ".md"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"# {title}\n\nSource: {url}\n\n{markdown_text}")
            
            print(f"\n成功！: {filename} を保存しました。")
            print("このファイルをObsidianのVault（保管庫）に移動してください。")
        except Exception as e:
            print(f"本文エリアの取得に失敗しました。ログインが維持されているか確認してください: {e}")

    finally:
        # 動作確認のため、最後はあえて閉じないようにしています
        # 終わったら手動で閉じるか、下の行を有効にしてください
        # driver.quit()
        print("\nブラウザを閉じて終了するにはEnterを押してください...")
        input()
        driver.quit()

# 実行
save_note_manual_trigger("https://note.com/papapico/n/nb163688ef395")