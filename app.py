
import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt

# Sidebar setup
st.sidebar.title("WhatsApp Chat Analyzer")
uploaded_file = st.sidebar.file_uploader("Choose a chat file (.txt)")

if uploaded_file is not None:
    # Read file
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")

    # Preprocess chat
    df = preprocessor.preprocess(data)

    # Show preview
    st.subheader("Chat Data Preview")
    st.dataframe(df.head(20))

    # User list for analysis
    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

    if st.sidebar.button("Show Analysis"):
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Messages", num_messages)

        with col2:
            st.metric("Total Words", words)

        with col3:
            st.metric("Media Shared", num_media_messages)

        with col4:
            st.metric("Links Shared", num_links)

        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)

        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'], color='green', marker='o')
        plt.xticks(rotation=90)  # keep labels readable
        st.pyplot(fig)
        st.title("Daily Timeline")
        daily_tl = helper.daily_timeline(selected_user, df)

        fig, ax = plt.subplots()
        ax.plot(daily_tl['day'], daily_tl['message'], color='blue')
        plt.xticks(rotation=90)  # Rotate to avoid overlap
        st.pyplot(fig)

        # Most Busy Day
        st.title("Most Busy Day")
        busy_day = helper.most_busy_day(selected_user, df)

        fig, ax = plt.subplots()
        ax.bar(busy_day['day'], busy_day['message_count'], color="teal")
        plt.xticks(rotation=45)
        st.pyplot(fig)

        # Most Busy Month
        st.title("Most Busy Month")
        busy_month = helper.most_busy_month(selected_user, df)

        fig, ax = plt.subplots()
        ax.bar(busy_month['month'], busy_month['message_count'], color="darkorange")
        plt.xticks(rotation=45)
        st.pyplot(fig)

        st.title("Weekday Activity Map")

        weekday_df = helper.weekday_activity_map(selected_user, df)

        if selected_user == "Overall":
            st.dataframe(weekday_df)  # Show full table: User, Day, Count

            # Pivot for heatmap (users vs days)
            pivot_df = weekday_df.pivot(index='user', columns='day_name', values='message').fillna(0)

            st.subheader("Heatmap of Active Users by Day")
            fig, ax = plt.subplots(figsize=(10, 5))
            import seaborn as sns

            sns.heatmap(pivot_df, annot=True, fmt="g", cmap="YlGnBu", ax=ax)
            st.pyplot(fig)

        else:
            st.subheader(f"{selected_user}'s activity by day")
            daywise = weekday_df.groupby('day_name').sum()['message']
            fig, ax = plt.subplots()
            ax.bar(daywise.index, daywise.values, color="orange")
            plt.xticks(rotation=45)
            st.pyplot(fig)
            st.title("Most Active Days")

            active_days = helper.most_active_days(selected_user, df)

            fig, ax = plt.subplots()
            ax.bar(active_days['day'], active_days['message_count'], color="purple")
            plt.xticks(rotation=45)
            st.pyplot(fig)


        # Most Busy Users
        if selected_user == "Overall":
            st.title('Most Busy Users')
            x, new_df = helper.most_busy_users(df)
            fig, ax = plt.subplots()

            col1, col2 = st.columns(2)
            with col1:
                ax.bar(x.index, x.values, color='red')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)

        # WordCloud
        st.title("WordCloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)

        # Most Common Words
        st.title("Most Common Words")
        most_common_df = helper.most_common_words(selected_user, df)
        fig, ax = plt.subplots()
        ax.barh(most_common_df['word'], most_common_df['count'], color="skyblue")
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        import matplotlib.pyplot as plt
        import matplotlib


        try:
            matplotlib.rcParams['font.family'] = 'Segoe UI Emoji'  # Windows
        except:
            matplotlib.rcParams['font.family'] = 'Noto Color Emoji'  # Linux/Mac


        st.title("Emoji Analysis")
        emoji_df = helper.emoji_helper(selected_user, df)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Emoji Data")
            st.dataframe(emoji_df)

        with col2:
            if not emoji_df.empty:
                st.subheader("Emoji Distribution")
                fig, ax = plt.subplots()
                ax.pie(
                    emoji_df['count'].head(10),
                    labels=emoji_df['emoji'].head(10),
                    autopct="%0.2f%%",
                    startangle=90
                )
                st.pyplot(fig)


