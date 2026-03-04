# apps/recommendations/services/pipelines.py
from duckduckgo_search import DDGS
from apps.recommendations.models import Article, Course, Video, Book
from apps.recommendations.services.scraper import fetch_page_data
from apps.recommendations.services.context import get_topics_plan

def recommend_articles(user, topics_plan):
    count = 0
    with DDGS() as ddgs:
        for plan in topics_plan:
            topic_name = plan['topic']
            query = plan['queries']['article']
            
            try:
                results = list(ddgs.text(query, max_results=4))
                for item in results:
                    url = item.get('href')
                    if not url: continue
                    
                    page_data = fetch_page_data(url)
                    Article.objects.create(
                        user=user,
                        topic=topic_name[:200],
                        title=item.get('title')[:255],
                        url=url,
                        thumbnail=page_data.get("image"),
                        platform="Web",
                        author="",
                        body=item.get('body', '')[:500]
                    )
                    count += 1
            except Exception as e:
                print(f"Error fetching articles for {topic_name}: {e}")
    return {"articles_added": count}

def recommend_videos(user, topics_plan):
    count = 0
    with DDGS() as ddgs:
        for plan in topics_plan:
            topic_name = plan['topic']
            query = f"{plan['queries']['video']} site:youtube.com"
            
            try:
                results = list(ddgs.videos(query, max_results=6))
                for item in results:
                    url = item.get('content')
                    if not url: continue
                    
                    Video.objects.create(
                        user=user,
                        topic=topic_name[:200],
                        title=item.get('title')[:255],
                        url=url,
                        thumbnail=item.get('images', {}).get('medium'),
                        platform="YouTube",
                        description=item.get('description', '')[:500],
                        embed_url=item.get('embed_url', "")
                    )
                    count += 1
            except Exception as e:
                print(f"Error fetching videos for {topic_name}: {e}")
    return {"videos_added": count}

def recommend_courses(user, topics_plan):
    count = 0
    with DDGS() as ddgs:
        for plan in topics_plan:
            topic_name = plan['topic']
            query = f"{plan['queries']['course']} site:coursera.org OR site:udemy.com"
            
            try:
                results = list(ddgs.text(query, max_results=2))
                for item in results:
                    url = item.get('href')
                    if not url: continue
                    
                    page_data = fetch_page_data(url)
                    Course.objects.create(
                        user=user,
                        topic=topic_name[:200],
                        title=item.get('title')[:255],
                        url=url,
                        thumbnail=page_data.get("image"),
                        platform='Web',
                        instructor="unknown",
                        price=10,
                        course_objectives=[]
                    )
                    count += 1
            except Exception as e:
                pass
    return {"courses_added": count}

def recommend_books(user, topics_plan):
    count = 0
    with DDGS() as ddgs:
        for plan in topics_plan:
            topic_name = plan['topic']
            query = f"{plan['queries']['book']} (site:amazon.com OR site:goodreads.com OR filetype:pdf)"
            
            try:
                results = list(ddgs.text(query, max_results=2))
                for item in results:
                    url = item.get('href')
                    if not url: continue
                    
                    page_data = fetch_page_data(url)
                    Book.objects.create(
                        user=user,
                        topic=topic_name[:200],
                        title=item.get('title')[:255],
                        url=url,
                        thumbnail=page_data.get("image"),
                        author="",
                        publisher="",
                        book_summary=item.get('body', '')[:500]
                    )
                    count += 1
            except Exception as e:
                pass
    return {"books_added": count}

def run_full_pipeline(user, profession, chat_history):
    """Executes the full monolith pipeline."""
    topics_plan = get_topics_plan(user, profession, chat_history)
    
    summary = {
        "topics_analyzed": [t['topic'] for t in topics_plan]
    }
    
    # Run all modular components
    summary.update(recommend_articles(user, topics_plan))
    summary.update(recommend_videos(user, topics_plan))
    summary.update(recommend_courses(user, topics_plan))
    summary.update(recommend_books(user, topics_plan))
    
    return summary