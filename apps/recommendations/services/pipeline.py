from apps.memory.global_activities import search_global_activities
from apps.memory.persona_memory import search_persona_memory
from apps.recommendations.services.analyzer import analyze_user_needs
from apps.recommendations.services.searcher import search_content
from apps.recommendations.models import Article, Course, Video, Book
from apps.recommendations.services.scraper import fetch_page_data
from apps.recommendations.services.verifier import (
    verify_article, verify_video, verify_course, verify_book
)

# def run_recommendation_pipeline(user, profession="", chat_history=""):
    
#     # 1. Analyze User Needs to Generate Topic Plans
#     topics = analyze_user_needs(profession, chat_history)
    
#     print(f"=== Generated Topic Plans ===")
#     print(topics)
    
#     results = []
    
#     for topic_plan in topics:
#         topic = topic_plan['topic']
#         print(f"\n=== Processing Topic: {topic} ===")
        
#         # 2. Search Content for Each Topic Plan
#         search_results = search_content(topic_plan)
        
#         results.append(search_results)
        
#         print(f"--- Search Results for Topic: {topic} ---")
#         print(search_results)
    
#     return results



def run_recommendation_pipeline(user, profession, chat_history):
    
    # --- 1. Retrieve Persona Memory ---
    # We query for general interests or the profession to find relevant user background
    persona_query = f"Interests, goals, and learning style for {profession}"
    persona_data = search_persona_memory(
        query=persona_query, 
        user_id=user.id, 
        limit=3
    )
    # Format list of dicts/text into a single string
    # Assuming search_persona_memory returns [{'text': '...'}, ...]
    persona_text = "\n".join([p.get('text', '') for p in persona_data])

    # --- 2. Retrieve Global Activities ---
    # We search for what others in this profession are doing/asking
    # Using the user's chat history as a seed, or generic "trends" if history is empty
    global_query = chat_history if len(chat_history) > 50 else f"Trending skills for {profession}"
    
    global_activities_data = search_global_activities(
        query=global_query, 
        profession=profession, 
        limit=3
    )
    # Format list of strings into a single string
    global_activities_text = "\n".join(global_activities_data)

    # --- 3. Analyze Needs (LLM) ---
    topics_plan = analyze_user_needs(
        profession=profession, 
        chat_history=chat_history,
        persona=persona_text,
        global_activities=global_activities_text
    )

    # Analyze Needs
    # topics_plan = analyze_user_needs(profession, chat_history)
    
    print("=== *********************Topics Plan *****************************===")
    print(topics_plan)
    print("==\n\n\n\n\n=================")
    
    # Track what we found
    summary = {
        "articles": 0,
        "courses": 0,
        "books": 0,
        "videos": 0,
        "topics_analyzed": [t['topic'] for t in topics_plan]
    }
    
    
    # Process Each Topic Plan
    for plan in topics_plan:
        topic_name = plan['topic']
        print(f"Processing Topic: {topic_name}")

        # Search DuckDuckGo
        search_results = search_content(plan)
        
        print(f"Search result for topic '{topic_name}'================\n============:")
        print(search_results)
        print("====================\n\n\n\n\n\n=====================\n")
        
        
        
        # --- ARTICLES ---
        for item in search_results.get('articles', []):
            url = item.get('href')
            if not url: continue
            
            # Get Text AND Thumbnail Image
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
                
            summary["articles"] += 1
            
            # if not page_data["text"]:
            #     page_data["text"] = item.get('body', '')
                
            # # Verify
            # data = verify_article(profession, topic_name, item, page_data['text'])
            
            # if data.get('is_relevant'):
            #     Article.objects.create(
            #         user=user,
            #         topic=topic_name,
            #         title=item.get('title'),
            #         url=url,
            #         thumbnail=page_data.get("image"),
            #         platform=data.get('platform', 'Web'),
            #         author=data.get('author', ''),
            #         body=item.get('body', '')
            #     )
                
            #     summary["articles"] += 1

        # --- COURSES ---
        for item in search_results.get('courses', []):
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

            summary["courses"] += 1
            
            # if not page_data["text"]:
            #     page_data["text"] = item.get('body', '')
                
            # data = verify_course(profession, topic_name, item, page_data['text'])
            
            # if data.get('is_relevant'):
            #     # Handle Price safely
            #     price_val = data.get('price')
            #     if price_val == "null" or price_val is None:
            #         price_val = 0.00
                
            #     Course.objects.create(
            #         user=user,
            #         topic=topic_name,
            #         title=item.get('title'),
            #         url=url,
            #         thumbnail=page_data.get("image"),
            #         platform=data.get('platform', 'Web'),
            #         instructor=data.get('instructor', ''),
            #         price=price_val,
            #         course_objectives=data.get('course_objectives', [])
            #     )

            #     summary["courses"] += 1

        # --- BOOKS ---
        for item in search_results.get('books', []):
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
            
            summary["books"] += 1
            
            # if not page_data["text"]:
            #     page_data["text"] = item.get('body', '')
                
            # data = verify_book(profession, topic_name, item, page_data['text'])

            # if data.get('is_relevant'):
            #     Book.objects.create(
            #         user=user,
            #         topic=topic_name,
            #         title=item.get('title'),
            #         url=url,
            #         thumbnail=page_data.get("image"),
            #         author=data.get('author', ''),
            #         publisher=data.get('publisher', ''),
            #         book_summary=data.get('book_summary', '')
            #     )
                
            #     summary["books"] += 1

        # --- VIDEOS ---
        for item in search_results.get('videos', []):
            url = item.get('content') # content is the URL in ddgs
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
            
            summary["videos"] += 1

            # For videos, we rely on metadata, not scraping
            # data = verify_video(profession, topic_name, item)
            
            # if data.get('is_relevant'):
            #     # Construct Embed URL if missing
            #     embed_url = item.get('embed_url')
            #     if not embed_url and "youtube.com" in url:
            #         vid_id = url.split("v=")[-1]
            #         embed_url = f"https://www.youtube.com/embed/{vid_id}"

            #     Video.objects.create(
            #         user=user,
            #         topic=topic_name,
            #         title=item.get('title'),
            #         url=url,
            #         thumbnail=item.get('images', {}).get('medium'),
            #         platform="YouTube",
            #         description=item.get('description', ''),
            #         embed_url=embed_url or ""
            #     )
                
            #     summary["videos"] += 1
    return summary