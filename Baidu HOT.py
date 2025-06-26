import requests
from datetime import datetime
from mysql_helper import MySqlHelper  # 自动读取 .env 文件

def get_baidu_hot_top10():
    url = 'https://top.baidu.com/api/board?platform=pc&tab=realtime'
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    try:
        res = requests.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        data = res.json()
    except Exception as e:
        print("❌ 百度热搜接口请求失败：", e)
        return []

    top10_list = []
    for i, item in enumerate(data['data']['cards'][0]['content'][:10], start=1):
        top10_list.append({
            'rank': i,
            'title': item['word'],
            'hot_value': item['hotScore'],
            'crawl_time': datetime.now()
        })
        print(f"{i}. {item['word']}（热度：{item['hotScore']}）")

    return top10_list

def save_to_db(hot_list):
    db = MySqlHelper()  # 自动从 .env 获取配置
    for item in hot_list:
        sql = """
        INSERT INTO baidu_hot (`rank`, title, hot_value, crawl_time)
        VALUES (%s, %s, %s, %s)
        """
        db.execute(sql, (item['rank'], item['title'], item['hot_value'], item['crawl_time']))
    db.close()
    print("✅ 已成功写入数据库")

if __name__ == '__main__':
    hot_list = get_baidu_hot_top10()
    if hot_list:
        save_to_db(hot_list)


 
   