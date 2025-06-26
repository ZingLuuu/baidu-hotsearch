import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_baidu_hot_top10_html():
    url = 'https://top.baidu.com/board?tab=realtime'
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    try:
        res = requests.get(url, headers=headers, timeout=15)
        res.encoding = 'utf-8'
        html = res.text
    except Exception as e:
        print("❌ 网页加载失败：", e)
        return []

    soup = BeautifulSoup(html, 'lxml')

    # 提取热搜词（标题）
    titles = [tag.get_text(strip=True) for tag in soup.select('.c-single-text-ellipsis')][:10]

    # 提取热度值
    hot_values = [tag.get_text(strip=True) for tag in soup.select('.hot-index_1Bl1a')][:10]

    hot_list = []
    for i, (title, score) in enumerate(zip(titles, hot_values), start=1):
        hot_list.append({
            'rank': i,
            'title': title,
            'hot_value': score,
            'crawl_time': datetime.now()
        })
        print(f"{i}. {title}（热度：{score}）")

    return hot_list

# 测试运行
if __name__ == '__main__':
    hot_list = get_baidu_hot_top10_html()
