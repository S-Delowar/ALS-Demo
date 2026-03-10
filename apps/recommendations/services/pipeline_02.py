# apps/recommendations/services/pipelines.py
import concurrent.futures
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


# Orchestrator function to run all recommendation tasks concurrently
def run_full_recommendation_pipeline(user, profession, chat_history):
    """Executes the full function-based pipeline concurrently."""
    topics_plan = get_topics_plan(user, profession, chat_history)
    
    summary = {
        "topics_analyzed": [t['topic'] for t in topics_plan]
    }
    
    # Define our independent I/O bound tasks
    pipeline_tasks = [
        recommend_articles,
        recommend_videos,
        recommend_courses,
        recommend_books
    ]
    
    # Run the 4 main recommendation categories in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        # Map the tasks to the executor
        future_to_task = {
            executor.submit(task, user, topics_plan): task.__name__ 
            for task in pipeline_tasks
        }
        
        # Gather results as they complete
        for future in concurrent.futures.as_completed(future_to_task):
            task_name = future_to_task[future]
            try:
                result = future.result()
                summary.update(result)
            except Exception as e:
                # Log the error, but don't crash the entire pipeline if one source fails
                print(f"Pipeline component {task_name} failed: {e}")
                
    return summary