import os
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from markdownify import markdownify as md

def get_article_urls(driver, list_page_url):
    print(f"一覧ページを取得中: {list_page_url}")
    driver.get(list_page_url)
    time.sleep(5)

    # --- 無限スクロール対策: 最後までスクロールする ---
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # 下端までスクロール
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3) # 読み込み待ち
        
        # 新しい高さを取得して、前回と同じ（＝これ以上スクロールできない）なら終了
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        print("スクロール中...")

# 記事リンク（noteの標準的なURL形式 /n/xxxxxxxxxxxx）を探す
    links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/n/"]')
    urls = []
    for link in links:
        url = link.get_attribute('href')
        # 重複を避けてリストに追加
        if url and url not in urls:
            urls.append(url)
    
    print(f"合計 {len(urls)} 件の記事が見つかりました。")
    return urls

def save_note_manual_trigger(driver, url):
    """単一記事を保存する（既存の関数を流用）"""
    try:
        print(f"取得中: {url}")
        driver.get(url)
        time.sleep(3)  # 記事の読み込み待ち

        title = driver.title.replace("｜note", "").strip()
        # ファイル名に使えない文字を置換
        safe_title = re.sub(r'[\\/:*?"<>|]', '_', title)
        filename = f"{safe_title}.md"

        # 本文エリアの取得
        content_element = driver.find_element(By.TAG_NAME, "article")
        html_content = content_element.get_attribute('innerHTML')
        markdown_text = md(html_content, heading_style="ATX")

        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\nSource: {url}\n\n{markdown_text}")
        
        print(f"保存完了: {filename}")
    except Exception as e:
        print(f"保存失敗 ({url}): {e}")

def main(list_url):
    chrome_options = Options()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        # 1. ログイン（一度行えばOK）
        driver.get("https://note.com/login")
        print("\n" + "="*50)
        print("1. ブラウザでログインを完了させてください。")
        print("2. 完了後、このターミナルに戻って Enterキー を押してください...")
        print("="*50 + "\n")
        input(">>> ログインが終わったらEnterを押してください...")

        # 2. 記事URLの一覧を取得
        article_urls = get_article_urls(driver, list_url)

        # 3. 各記事を順番に保存
        for index, url in enumerate(article_urls):
            print(f"\n[{index + 1}/{len(article_urls)}] 処理を開始します...")
            save_note_manual_trigger(driver, url)
            time.sleep(2)  # サーバー負荷軽減のための待機

        print("\nすべての記事の処理が完了しました。")

    finally:
        print("\nブラウザを閉じて終了するにはEnterを押してください...")
        input()
        driver.quit()

# 実行（対象の一覧ページURLを指定してください）
target_list_url = "https://note.com/papapico/m/mef844c1d39fc"
main(target_list_url)