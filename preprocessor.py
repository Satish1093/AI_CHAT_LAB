import re
import pandas as pd
import re
import pandas as pd
import os

def preprocess(data):
    """
    Preprocess WhatsApp chat export (file path or raw text) into a DataFrame.

    Returns DataFrame with columns:
    ['date', 'user', 'message', 'year', 'month', 'day', 'hour', 'minute']
    """

    # Regex to capture date, time, user, message
    pattern = re.compile(
        r'^(\d{1,2}/\d{1,2}/\d{2}),\s*'         # date
        r'(\d{1,2}:\d{2}\s*[APMapm]{2})\s*-\s*' # time
        r'(.*?):\s'                             # user
        r'(.*)$'                                # message
    )

    messages, dates, users = [], [], []

    # --- 1) If input is a file path ---
    if os.path.exists(data):
        with open(data, encoding="utf-8") as f:
            lines = f.readlines()
    else:
        # --- 2) If input is raw text ---
        lines = data.split("\n")

    # Parse each line
    for line in lines:
        line = line.strip().replace("\u202f", " ")  # fix special spaces
        match = pattern.match(line)
        if match:
            date_str, time_str, user, message = match.groups()
            dates.append(f"{date_str}, {time_str} -")
            users.append(user)
            messages.append(message)
        else:
            # continuation of previous message
            if messages:
                messages[-1] += " " + line

    # Build DataFrame
    df = pd.DataFrame({"date": dates, "user": users, "message": messages})

    # Convert to datetime (default WhatsApp US-style: month/day/year)
    df["date"] = pd.to_datetime(
        df["date"],
        format="%m/%d/%y, %I:%M %p -",  # change to "%d/%m/%y..." if your export is day-first
        errors="coerce"
    )

    # Extract extra features
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month_name()
    df["day"] = df["date"].dt.day
    df["hour"] = df["date"].dt.hour
    df["minute"] = df["date"].dt.minute

    return df
