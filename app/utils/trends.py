
def extract_topics(trends):
    topics=[]
    for trend in trends:
        if "#" not in trend['name'] and trend['tweet_volume']!="null":
            dic = {"name":trend['name'],"tweet_count":trend['tweet_volume']}
            topics.append(dic)
        else:
            dic = {"name":trend['name'] , "tweet_count": None}
            topics.append(dic)
    return topics

def extract_hashtags(trends):
    hashtags=[]
    for trend in trends:
        if "#" in trend['name'] and trend['tweet_volume']!="null":
            dic = {"name":trend['name'],"tweet_count":trend['tweet_volume']}
            hashtags.append(dic)
        else:
            dic = {"name":trend['name'], "tweet_count": None}
            hashtags.append(dic)
    return hashtags