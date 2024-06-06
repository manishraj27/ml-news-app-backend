from flask import Flask, request, jsonify

from flask_cors import CORS

from flask import Flask
from flask_cors import CORS
from PIL import Image
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
from newspaper import Article
import io
import logging
import nltk

nltk.download('punkt')

app = Flask(__name__)
cors = CORS(app)  # Enable CORS for all routes
CORS(app, resources={r"/api/*": {"origins": "*"}})

def fetch_news_search_topic(topic):
    site = 'https://news.google.com/rss/search?q={}'.format(topic)
    op = urlopen(site)  
    rd = op.read()  
    op.close()  
    sp_page = soup(rd, 'xml')  
    news_list = sp_page.find_all('item')  
    return news_list

def fetch_top_news():
    site = 'https://news.google.com/news/rss'
    op = urlopen(site)  
    rd = op.read()  
    op.close()  
    sp_page = soup(rd, 'xml')  
    news_list = sp_page.find_all('item')  
    return news_list

def fetch_category_news(topic):
    site = 'https://news.google.com/news/rss/headlines/section/topic/{}'.format(topic)
    op = urlopen(site)  
    rd = op.read()  
    op.close()  
    sp_page = soup(rd, 'xml')  
    news_list = sp_page.find_all('item')  
    return news_list

def fetch_news_poster(poster_link):
    try:
        u = urlopen(poster_link)
        return poster_link
    except Exception as e:
        logging.error(f"Error fetching news poster: {e}")
        return None


def get_news_data(news):
    news_data = Article(news.link.text)
    try:
        news_data.download()
        news_data.parse()
        news_data.nlp()
    except Exception as e:
        return {"error": str(e)}
    
    return {
        "title": news.title.text,
        "summary": news_data.summary,
        "source": news.source.text,
        "link": news.link.text,
        "pubDate": news.pubDate.text,
        "image": fetch_news_poster(news_data.top_image)
    }

@app.route('/api/news', methods=['GET'])
def get_news():
    topic = request.args.get('topic')
    if not topic:
        return jsonify({"error": "Topic parameter is required"}), 400
    
    news_quantity = int(request.args.get('quantity', 5))
    
    if topic == 'top':
        news_list = fetch_top_news()
    elif topic == 'search':
        query = request.args.get('query')
        if not query:
            return jsonify({"error": "Query parameter is required for search"}), 400
        news_list = fetch_news_search_topic(query)
    else:
        news_list = fetch_category_news(topic)
    
    if not news_list:
        return jsonify({"error": "No news found"}), 404
    
    formatted_news = []
    for news in news_list[:news_quantity]:
        formatted_news.append(get_news_data(news))
    
    return jsonify(formatted_news)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
    print("Server is running...")
