import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
channels_df = pd.read_csv(r"Datasets/channels.csv")
playlists_df = pd.read_csv(r'Datasets/playlists.csv')
videos_df = pd.read_csv(r'Datasets/videos.csv')
def calculate_average_engagement_rate(df):
    return (df["video_likes"].sum() / df["video_view_count"].sum()) * 100

def find_popular_video_categories(df):
    return df.groupby("video_category_id")["video_view_count"].sum().sort_values(ascending=False)

def find_upload_frequency(df):
    df["published_at"] = pd.to_datetime(df["published_at"])
    df["year"] = df["published_at"].dt.year
    return df.groupby("year")["video_id"].count()
# Calculate average engagement rate for videos
avg_engagement_rate = calculate_average_engagement_rate(videos_df)

# Find popular video categories
popular_video_categories = find_popular_video_categories(videos_df)

# Find patterns in video upload frequency
upload_frequency = find_upload_frequency(videos_df)

# Save the results to CSV files
popular_video_categories.to_csv(r"Datasets/popular_video_categories.csv")
upload_frequency.to_csv(r"Datasets/upload_frequency.csv")
channels_data = {}
for channel_id in channels_df["channel_id"].unique():
    channel_title = channels_df.loc[channels_df["channel_id"] == channel_id, "channel_title"].values[0]
    channels_data[channel_title] = {
        "channel": channels_df[channels_df["channel_id"] == channel_id],
        "videos": videos_df[videos_df["channel_id"] == channel_id]
    }
for channel_title, data in channels_data.items():
    data["avg_engagement_rate"] = calculate_average_engagement_rate(data["videos"])
    data["popular_video_categories"] = find_popular_video_categories(data["videos"])
    data["upload_frequency"] = find_upload_frequency(data["videos"])
    
# Set figure size in inches (width, height)
figure_size = (20, 15)

# Set the DPI (dots per inch) for the saved image
dpi = 100
for channel_title, data in channels_data.items():
    # Example: bar chart for popular video categories
    plt.figure(figsize=figure_size, dpi=dpi)
    plt.bar(data["popular_video_categories"].index, data["popular_video_categories"].values)
    plt.title(f"Popular Video Categories for Channel {channel_title}")
    plt.xlabel("Video Category ID")
    plt.ylabel("Views")
    plt.savefig(f"{channel_title}_popular_video_categories.png", dpi=dpi)
    plt.clf()
# Example: Compare average engagement rates between channels
channel_engagement_rates = {channel_title: data["avg_engagement_rate"] for channel_title, data in channels_data.items()}
channel_engagement_rates_df = pd.Series(channel_engagement_rates).to_frame("avg_engagement_rate")
channel_engagement_rates_df.to_csv(r"Datasets/channel_engagement_rates.csv")
# Example: Bar chart comparing average engagement rates between channels
plt.figure(figsize=figure_size, dpi=dpi)
plt.bar(channel_engagement_rates_df.index, channel_engagement_rates_df["avg_engagement_rate"])
plt.title("Average Engagement Rates for Channels")
plt.xlabel("Channel Title")
plt.ylabel("Average Engagement Rate")
plt.xticks(rotation=90)
plt.savefig("channel_engagement_rates_comparison.png", dpi=dpi)
plt.clf()
def plot_channel_statistics(data, channel_title, statistic_name):
    plt.figure(figsize=figure_size, dpi=dpi)
    plt.hist(data["video_" + statistic_name], bins=20)
    plt.title(f"{statistic_name.capitalize()} distribution for Channel {channel_title}")
    plt.xlabel(statistic_name.capitalize())
    plt.ylabel("Number of videos")
    folder_path = f"images/{channel_title}"
    os.makedirs(folder_path, exist_ok=True)  
    plt.savefig(f"{folder_path}/{channel_title}_{statistic_name}_distribution.png", dpi=dpi)
    plt.clf()

for channel_title, data in channels_data.items():
    for statistic_name in ["view_count", "likes", "dislikes", "comments"]:
        plot_channel_statistics(data["videos"], channel_title, statistic_name)

def plot_video_category_statistics(data, channel_title, statistic_name):
    video_categories = data.groupby("video_category_id")[f"video_{statistic_name}"].sum()
    plt.figure(figsize=figure_size, dpi=dpi)
    plt.bar(video_categories.index, video_categories.values)
    plt.title(f"Total {statistic_name.capitalize()} per Video Category for Channel {channel_title}")
    plt.xlabel("Video Category ID")
    plt.ylabel(f"Total {statistic_name.capitalize()}")
    folder_path = f"images/{channel_title}"
    os.makedirs(folder_path, exist_ok=True)
    plt.savefig(f"{folder_path}/{channel_title}_video_category_{statistic_name}.png", dpi=dpi)
    plt.clf()

for channel_title, data in channels_data.items():
    for statistic_name in ["view_count", "likes", "dislikes", "comments"]:
        plot_video_category_statistics(data["videos"], channel_title, statistic_name)

def plot_comparison_statistics(channels_data, statistic_name):
    channel_statistics = {channel_title: data["videos"][f"video_{statistic_name}"].sum() for channel_title, data in channels_data.items()}
    channel_statistics_df = pd.Series(channel_statistics).to_frame(f"total_{statistic_name}")
    channel_statistics_df.to_csv(f"channel_{statistic_name}_comparison.csv")

    plt.figure(figsize=figure_size, dpi=dpi)
    plt.bar(channel_statistics_df.index, channel_statistics_df[f"total_{statistic_name}"])
    plt.title(f"Total {statistic_name.capitalize()} Comparison for Channels")
    plt.xlabel("Channel Title")
    plt.ylabel(f"Total {statistic_name.capitalize()}")
    plt.xticks(rotation=90)
    plt.savefig(f"channel_{statistic_name}_comparison.png", dpi=dpi)
    plt.clf()

for statistic_name in ["view_count", "likes", "dislikes", "comments"]:
    plot_comparison_statistics(channels_data, statistic_name)

# Group videos by channel_title
grouped_videos = videos_df.groupby("channel_title")

# Create the channels_data dictionary
channels_data = {}
for channel_title, group in grouped_videos:
    channels_data[channel_title] = {"videos": group}

# Apply the functions to the grouped data
for channel_title, data in channels_data.items():
    for statistic_name in ["view_count", "likes", "dislikes", "comments"]:
        plot_channel_statistics(data["videos"], channel_title, statistic_name)
        plot_video_category_statistics(data["videos"], channel_title, statistic_name)

for statistic_name in ["view_count", "likes", "dislikes", "comments"]:
    plot_comparison_statistics(channels_data, statistic_name)
