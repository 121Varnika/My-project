import googleapiclient.discovery
import googleapiclient.errors
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

nltk.download('vader_lexicon')
sid = SentimentIntensityAnalyzer()

api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = ""

youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=DEVELOPER_KEY)

video_id = input("Enter the YouTube video ID: ")
max_results = int(input("Enter the number of comments to retrieve: "))

def get_comments(video_id, max_results):
    comments = []
    next_page_token = None

    while len(comments) < max_results:
        try:
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=min(100, max_results - len(comments)),
                pageToken=next_page_token
            )
            response = request.execute()
            comments += [item['snippet']['topLevelComment']['snippet']['textDisplay'] for item in response['items']]
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            break
    return comments

comments = get_comments(video_id, max_results)

def analyze_sentiment(comments):
    positive = 0
    neutral = 0
    negative = 0
    for comment in comments:
        sentiment_score = sid.polarity_scores(comment)
        if sentiment_score['compound'] >= 0.05:
            positive += 1
        elif sentiment_score['compound'] <= -0.05:
            negative += 1
        else:
            neutral += 1
    return positive, neutral, negative

positive, neutral, negative = analyze_sentiment(comments)
print("\nTotal Sentiment Counts:")
print(f"Positive: {positive}")
print(f"Neutral: {neutral}")
print(f"Negative: {negative}")

def get_video_statistics(video_id):
    try:
        request = youtube.videos().list(
            part='statistics',
            id=video_id
        )
        response = request.execute()

        if 'items' in response and len(response['items']) > 0:
            statistics = response['items'][0]['statistics']
            likes = statistics.get('likeCount', 0)
            dislikes = statistics.get('dislikeCount', 0)
            return likes, dislikes
        else:
            return None, None
    except googleapiclient.errors.HttpError as e:
        print(f"An error occurred: {e}")
        return None, None
        