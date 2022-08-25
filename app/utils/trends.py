
def extract_topics(trends):
    topics = [trend["name"] for trend in trends if "#" not in trend["name"]]
    return topics
def extract_hashtags(trends):
    hashtags = [trend['name'] for trend in trends if "#" in trend['name']]
    return hashtags