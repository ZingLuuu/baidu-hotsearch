import requests
from bs4 import BeautifulSoup
import pymysql
import time

# 插入语句
insert_sql = """
INSERT INTO douban_top100 (title, director, year, rating, genre, douban_url, cover_url)
VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

def get_movies_from_page(start):
    url = f'https://movie.douban.com/top250?start={start}'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    movies = soup.find_all('div', class_='item')

    conn = pymysql.connect(host='localhost', user='root', password='Lzx1005-', database='database1', charset='utf8mb4')
    cursor = conn.cursor()

    for movie in movies:
        title = movie.find('span', class_='title').text.strip()
        info_text = movie.find('div', class_='bd').p.text.strip().replace('\n', '').replace('\xa0', '')
        info_parts = info_text.split('/')
        director = info_parts[0].strip().split(':')[1].strip() if ':' in info_parts[0] else info_parts[0].strip()
        rating = float(movie.find('span', class_='rating_num').text.strip())
        douban_url = movie.find('a')['href'].strip()
        cover_url = movie.find('img')['src'].strip()

        # ====== 补充抓取详情页以获取 year 和 genre ======
        try:
            detail_response = requests.get(douban_url, headers=headers, timeout=10)
            detail_soup = BeautifulSoup(detail_response.text, 'lxml')
            year_tag = detail_soup.find('span', class_='year')
            year_text = year_tag.text.strip('() ') if year_tag else '0'
            year = int(year_text) if year_text.isdigit() else 0
            genre_tags = detail_soup.find_all('span', property='v:genre')
            genre_list = [tag.text.strip() for tag in genre_tags]
            genre = '/'.join(genre_list) if genre_list else '未知'
            time.sleep(2)
        except Exception as e:
            print(f'⚠️ 详情页抓取失败 {title}, 错误: {e}')
            year = 0
            genre = '未知'

        # ====== 插入数据库 ======
        try:
           # 检查是否已存在
           check_sql = "SELECT COUNT(*) FROM douban_top100 WHERE douban_url = %s"
           cursor.execute(check_sql, (douban_url,))
           exists = cursor.fetchone()[0]

           if exists:
                print(f'⚠️ 已存在，跳过: {title}')
           else:
                cursor.execute(insert_sql, (title, director, year, rating, genre, douban_url, cover_url))
                conn.commit()
                print(f'✅ 插入成功: {title}')
        except Exception as e:
           conn.rollback()
           print(f'❌ 插入失败: {title}, 错误: {e}')


    cursor.close()
    conn.close()

if __name__ == '__main__':
    for start in range(0, 100, 25):
        get_movies_from_page(start)
        time.sleep(2)
    print('✅ 豆瓣 Top 100 爬取、年份和类型同时获取完成并存入数据库。')


import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from matplotlib import rcParams

rcParams['font.sans-serif'] = ['SimHei']
rcParams['axes.unicode_minus'] = False

engine = create_engine('mysql+pymysql://root:Lzx1005-@localhost:3306/database1')
df = pd.read_sql('SELECT * FROM douban_top100', engine)
print(df.head())

# 评分分布
plt.figure(figsize=(8,6))
plt.hist(df['rating'], bins=20, edgecolor='black')
plt.title('豆瓣 Top100 评分分布')
plt.xlabel('评分')
plt.ylabel('电影数量')
plt.show()

# 年份趋势折线图（限制合理年份范围）
df_valid = df[(df['year'] >= 1950) & (df['year'] <= 2025)]
year_rating = df_valid.groupby('year')['rating'].mean().sort_index()
plt.figure(figsize=(10,6))
year_rating.plot(marker='o')
plt.title('豆瓣 Top100 不同年份平均评分趋势')
plt.xlabel('年份')
plt.ylabel('平均评分')
plt.grid(True)
plt.show()

# 饼图类型汇总显示（合并包含关键词的类型）
def simplify_genre(genre_str):
    genre_list = genre_str.split('/')
    simplified = []
    for g in genre_list:
        if '惊悚' in g:
            simplified.append('惊悚')
        elif '犯罪' in g:
            simplified.append('犯罪')
        elif '爱情' in g:
            simplified.append('爱情')
        elif '动画' in g:
            simplified.append('动画')
        elif '科幻' in g:
            simplified.append('科幻')
        elif '剧情' in g:
            simplified.append('剧情')
        elif '喜剧' in g:
            simplified.append('喜剧')
        elif '战争' in g:
            simplified.append('战争')
        elif '动作' in g:
            simplified.append('动作')
        else:
            simplified.append(g)
    return list(set(simplified))

genre_all = []
for g in df['genre']:
    genre_all.extend(simplify_genre(g))

from collections import Counter
genre_count = Counter(genre_all)
labels = list(genre_count.keys())
sizes = list(genre_count.values())

plt.figure(figsize=(10,10))
plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
plt.title('豆瓣 Top100 类型占比（合并同类）')
plt.show()

# 年份 vs 评分散点图
plt.figure(figsize=(10,6))
plt.scatter(df_valid['year'], df_valid['rating'], alpha=0.7)
plt.title('豆瓣 Top100 年份 vs 评分')
plt.xlabel('年份')
plt.ylabel('评分')
plt.grid(True)
plt.show()
