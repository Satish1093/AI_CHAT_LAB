from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import re

extract = URLExtract()

# ------------------------- #
# 1. Fetch Stats
# ------------------------- #
def fetch_stats(selected_user, df):
    """
    Returns: num_messages, total_words, num_media_messages, num_links
    """

    if selected_user == "Overall":
        temp = df
    else:
        temp = df[df['user'] == selected_user]

    # total messages
    num_messages = temp.shape[0]

    # total words
    words = []
    for message in temp['message']:
        words.extend(message.split())

    # total media messages
    num_media_messages = temp[temp['message'] == '<Media omitted>'].shape[0]

    # total links
    links = []
    for message in temp['message']:
        links.extend(extract.find_urls(message))

    return num_messages, len(words), num_media_messages, len(links)


# ------------------------- #
# 2. Most Busy Users
# ------------------------- #
def most_busy_users(df):
    x = df['user'].value_counts().head()
    df_percent = round((df['user'].value_counts() / df.shape[0]) * 100, 2) \
        .reset_index() \
        .rename(columns={'index': 'name', 'user': 'percent'})
    return x, df_percent


# ------------------------- #
# 3. WordCloud
# ------------------------- #
def create_wordcloud(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    wc = WordCloud(
        width=500,
        height=500,
        min_font_size=10,
        background_color='white'
    )

    df_wc = wc.generate(df['message'].str.cat(sep=" "))
    return df_wc


# ------------------------- #
# 4. Most Common Words
# ------------------------- #
def most_common_words(selected_user, df):
    f = open('stop_hinglish.txt', 'r', encoding="utf-8")
    stop_words = f.read().split()

    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>']

    words = []
    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    most_common_df.columns = ['word', 'count']
    return most_common_df


# ------------------------- #
# 5. Emoji Helper
# ------------------------- #
def emoji_helper(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    emojis = []
    # Regex that captures most emojis
    emoji_pattern = re.compile("[" 
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport
                               u"\U0001F1E0-\U0001F1FF"  # flags
                               u"\U00002700-\U000027BF"  # dingbats
                               u"\U0001F900-\U0001F9FF"  # supplemental symbols
                               u"\U0001FA70-\U0001FAFF"  # extended symbols
                               u"\U00002600-\U000026FF"  # misc
                               "]+", flags=re.UNICODE)

    for message in df['message']:
        emojis.extend(emoji_pattern.findall(message))

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    emoji_df.columns = ['emoji', 'count']
    return emoji_df
def monthly_timeline(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    # Group by year-month directly using pd.Grouper
    timeline = df.groupby(pd.Grouper(key="date", freq="M")).count()['message'].reset_index()

    # Format month-year like "Aug-2025"
    timeline['time'] = timeline['date'].dt.strftime("%B-%Y")

    return timeline

def daily_timeline(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    # Group by day
    daily_timeline = df.groupby(df['date'].dt.date).count()['message'].reset_index()
    daily_timeline.rename(columns={'date': 'day'}, inplace=True)
    return daily_timeline
def weekday_activity_map(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    # Extract weekday (Monday, Tuesday, etc.)
    df['day_name'] = df['date'].dt.day_name()

    # Count messages per user per weekday
    activity_map = df.groupby(['user', 'day_name']).count()['message'].reset_index()

    return activity_map

# Most Busy Day

def most_busy_day(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    # Extract day of week
    df['day_name'] = df['date'].dt.day_name()

    busy_day = df['day_name'].value_counts().reset_index()
    busy_day.columns = ['day', 'message_count']
    return busy_day


# ------------------------- #
# Most Busy Month
# ------------------------- #
def most_busy_month(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    # Extract month name
    df['month'] = df['date'].dt.month_name()

    busy_month = df['month'].value_counts().reset_index()
    busy_month.columns = ['month', 'message_count']
    return busy_month


