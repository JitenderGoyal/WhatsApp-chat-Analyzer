import re
import pandas as pd
from dateutil import parser

def preprocess(data):
    # Define the pattern to extract the date/time and the entire message
    # This pattern assumes that the date and time are followed by " - " and the sender's name
    pattern = r'(\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2}(?: [APap][Mm])?| \d{1,2}:\d{2}) - (.+)'

    # Find all occurrences of the pattern in the data
    matches = re.findall(pattern, data)

    # Create a DataFrame from the extracted information
    df = pd.DataFrame(matches, columns=['Date', 'Message'])

    # Parse the "Date" column to datetime objects with dateutil
    df['Date'] = df['Date'].apply(lambda x: parser.parse(x, fuzzy=True))

    # Split messages into user and message text
    users = []
    messages = []
    for message in df['Message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:  # user name
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('group_notification')
            messages.append(entry[0])

    # Add parsed data to the DataFrame
    df['user'] = users
    df['message'] = messages
    df.drop(columns=['Message'], inplace=True)

    # Extract date and time components
    df['year'] = df['Date'].dt.year
    df['month_num'] = df['Date'].dt.month
    df['month'] = df['Date'].dt.month_name()
    df['day'] = df['Date'].dt.day
    df['day_name'] = df['Date'].dt.day_name()
    df['hour'] = df['Date'].dt.hour
    df['minute'] = df['Date'].dt.minute

    # Determine the period of the day for the message
    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + '00')
        elif hour == 0:
            period.append('00' + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period

    # Extract only the date part for daily timeline analysis
    df['only_date'] = df['Date'].dt.date

    return df
