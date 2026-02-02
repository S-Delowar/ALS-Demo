from ddgs import DDGS


# ==========================================
# MODULE 2: The Hunter (Search)
# ==========================================
def search_content(topic_plan):
    """
    Executes searches for a specific topic plan.
    """
    raw_results = {
        "topic": topic_plan['topic'],
        "articles": [],
        "videos": [],
        "courses": [],
        "books": []
    }
    
    queries = topic_plan['queries']
    
    with DDGS() as ddgs:
        # 1. Search Videos (YouTube via .videos)
        try:
            video_q = f"{queries['video']} site:youtube.com"
            video_results = list(ddgs.videos(
                video_q, 
                max_results=6, 
            ))
            
            if video_results:
                raw_results['videos'] = video_results
        except: pass

        # 2. Search Articles (General Text)
        try:
            # Filter for educational/tech sites if possible
            article_results = list(ddgs.text(
                queries['article'], 
                max_results=4
            ))
            
            if article_results:
                raw_results['articles'] = article_results
        except: pass

        # 3. Search Courses (Coursera/Udemy via Text)
        try:
            course_q = f"{queries['course']} site:coursera.org OR site:udemy.com"
            course_results = list(ddgs.text(
                course_q, 
                max_results=2
            ))
            if course_results:
                raw_results['courses'] = course_results
        except: pass

        # 4. Search Books
        # Note: ddgs.books() is not standard in all versions. 
        # We use .text() with book-specific intent or custom handling.
        try:
            # Attempting to emulate user's request structure via text search
            book_q = f"{queries['book']} (site:amazon.com OR site:goodreads.com OR filetype:pdf)"
            book_results = list(ddgs.text(book_q, max_results=2))
            if book_results:
                raw_results['books'] = book_results
        except: pass

    return raw_results 