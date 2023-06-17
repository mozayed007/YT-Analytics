import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import re

figure_size = (20, 15)

# Set the DPI (dots per inch) for the saved image
dpi = 100
import os

def load_data():

    channels_df = pd.read_csv("M:/Repos/YT-Analytics/Datasets/channels.csv")
    playlists_df = pd.read_csv('M:/Repos/YT-Analytics/Datasets/playlists.csv')
    videos_df = pd.read_csv('M:/Repos/YT-Analytics/Datasets/videos.csv')
    
    videos_df['video_duration'] = videos_df['video_duration'].apply(convert_duration_to_seconds)
    return channels_df, playlists_df, videos_df

def calculate_average_engagement_rate(df):
    return (df["video_likes"].sum() / df["video_view_count"].sum()) * 100

def find_popular_video_categories(df):
    return df.groupby("video_category_id")["video_view_count"].sum().sort_values(ascending=False)

def find_upload_frequency(df):
    df["published_at"] = pd.to_datetime(df["published_at"])
    df["year"] = df["published_at"].dt.year
    return df.groupby("year")["video_id"].count()

# Set figure size in inches (width, height)

def plot_channel_statistics(data, channel_title, statistic_name):
    plt.figure(figsize=figure_size, dpi=dpi)
    plt.hist(data["video_" + statistic_name], bins=20)
    plt.title(f"{statistic_name.capitalize()} distribution for Channel {channel_title}")
    plt.xlabel(statistic_name.capitalize())
    plt.ylabel("Number of videos")
    folder_path = f"data_images/{channel_title}"
    os.makedirs(folder_path, exist_ok=True)  
    plt.savefig(f"{folder_path}/{channel_title}_{statistic_name}_distribution.png", dpi=dpi)
    plt.clf()



def plot_video_category_statistics(data, channel_title, statistic_name):
    video_categories = data.groupby("video_category_id")[f"video_{statistic_name}"].sum()
    plt.figure(figsize=figure_size, dpi=dpi)
    plt.bar(video_categories.index, video_categories.values)
    plt.title(f"Total {statistic_name.capitalize()} per Video Category for Channel {channel_title}")
    plt.xlabel("Video Category ID")
    plt.ylabel(f"Total {statistic_name.capitalize()}")
    folder_path = f"data_images/{channel_title}"
    os.makedirs(folder_path, exist_ok=True)
    plt.savefig(f"{folder_path}/{channel_title}_video_category_{statistic_name}.png", dpi=dpi)
    plt.clf()



def plot_comparison_statistics(channels_data, statistic_name):
    channel_statistics = {channel_title: data["videos"][f"video_{statistic_name}"].sum() for channel_title, data in channels_data.items()}
    channel_statistics_df = pd.Series(channel_statistics).to_frame(f"total_{statistic_name}")
    channel_statistics_df.to_csv(f"channel_{statistic_name}_comparison.csv",mode='a')

    plt.figure(figsize=figure_size, dpi=dpi)
    plt.bar(channel_statistics_df.index, channel_statistics_df[f"total_{statistic_name}"])
    plt.title(f"Total {statistic_name.capitalize()} Comparison for Channels")
    plt.xlabel("Channel Title")
    plt.ylabel(f"Total {statistic_name.capitalize()}")
    plt.xticks(rotation=90)
    plt.savefig(f"channel_{statistic_name}_comparison.png", dpi=dpi)
    plt.clf()

# Step 1: Add a function to convert video_duration to seconds
def convert_duration_to_seconds(duration):
    pattern = re.compile(r"PT(\d+M)?(\d+S)?")
    match = pattern.match(duration)
    minutes = int(match.group(1)[:-1]) if match.group(1) else 0
    seconds = int(match.group(2)[:-1]) if match.group(2) else 0
    return 60 * minutes + seconds

# Step 2: Modify the load_data function
import os

# def load_data():
#     script_dir = os.path.dirname(os.path.abspath(__file__)) # Get the script directory
#     parent_dir = os.path.dirname(script_dir) # Get the parent directory

#     channels_file = os.path.join(parent_dir, "Datasets", "channels.csv")
#     playlists_file = os.path.join(parent_dir, "Datasets", "playlists.csv")
#     videos_file = os.path.join(parent_dir, "Datasets", "videos.csv")

#     channels_df = pd.read_csv(channels_file)
#     playlists_df = pd.read_csv(playlists_file)
#     videos_df = pd.read_csv(videos_file)
    
#     videos_df['video_duration'] = videos_df['video_duration'].apply(convert_duration_to_seconds)
#     return channels_df, playlists_df, videos_df

# Step 3: Implement the new suggestion functions
def calculate_average_video_length(df):
    return df["video_duration"].mean()

def plot_video_length_distribution(data, channel_title):
    plt.figure(figsize=figure_size, dpi=dpi)
    plt.hist(data["video_duration"], bins=20)
    plt.title(f"Video Length Distribution for Channel {channel_title}")
    plt.xlabel("Video Length (seconds)")
    plt.ylabel("Number of videos")
    folder_path = f"data_images/{channel_title}"
    os.makedirs(folder_path, exist_ok=True)  
    plt.savefig(f"{folder_path}/{channel_title}_video_length_distribution.png", dpi=dpi)
    plt.clf()
def analyze_statistics_per_channel(channels_data, statistic_name):
    channel_statistics = {
        channel_title: {
            "sum": data["videos"][f"video_{statistic_name}"].sum(),
            "mean": data["videos"][f"video_{statistic_name}"].mean(),
            "std": data["videos"][f"video_{statistic_name}"].std(),
        }
        for channel_title, data in channels_data.items()
    }
    channel_statistics_df = pd.DataFrame(channel_statistics).T
    channel_statistics_df.to_csv(f"Datasets/channel_{statistic_name}_analysis.csv", mode='a')

def main():
    
    channels_df, playlists_df, videos_df = load_data()

    # Calculate average engagement rate for videos
    avg_engagement_rate = calculate_average_engagement_rate(videos_df)

    # Find popular video categories
    popular_video_categories = find_popular_video_categories(videos_df)

    # Find patterns in video upload frequency
    upload_frequency = find_upload_frequency(videos_df)

    # Save the results to CSV files
    popular_video_categories.to_csv("M:/Repos/YT-Analytics/Datasets/popular_video_categories.csv", mode='a')
    upload_frequency.to_csv("M:/Repos/YT-Analytics/Datasets/upload_frequency.csv", mode='a')
    grouped_videos = videos_df.groupby("channel_title")
    for channel_title, group in grouped_videos:
        channels_data[channel_title] = {"videos": group} 
    for statistic_name in ["view_count", "likes", "comments"]:
        analyze_statistics_per_channel(channels_data, statistic_name)

    # Create the channels_data dictionary
    channels_data = {}


    # Apply the functions to the grouped data
    for channel_title, data in channels_data.items():
        for statistic_name in ["view_count", "likes", "dislikes", "comments"]:
            plot_channel_statistics(data["videos"], channel_title, statistic_name)
            plot_video_category_statistics(data["videos"], channel_title, statistic_name)

    for statistic_name in ["view_count", "likes", "dislikes", "comments"]:
        plot_comparison_statistics(channels_data, statistic_name)

    # Calculate channel engagement rates and save the results to a CSV file
    channel_engagement_rates = {channel_title: calculate_average_engagement_rate(data["videos"]) for channel_title, data in channels_data.items()}
    channel_engagement_rates_df = pd.Series(channel_engagement_rates).to_frame("avg_engagement_rate")
    channel_engagement_rates_df.to_csv(r"Datasets/channel_engagement_rates.csv", mode='a')
    # Group videos by channel_title


    # Bar chart comparing average engagement rates between channels
    plt.figure(figsize=figure_size, dpi=dpi)
    plt.bar(channel_engagement_rates_df.index, channel_engagement_rates_df["avg_engagement_rate"])
    plt.title("Average Engagement Rates for Channels")
    plt.xlabel("Channel Title")
    plt.ylabel("Average Engagement Rate")
    plt.xticks(rotation=90)
    plt.savefig("channel_engagement_rates_comparison.png", dpi=dpi)
    plt.clf()
    # Calculate average video length for each channel
    channel_avg_video_lengths = {channel_title: calculate_average_video_length(data["videos"]) for channel_title, data in channels_data.items()}
    channel_avg_video_lengths_df = pd.Series(channel_avg_video_lengths).to_frame("avg_video_length")
    channel_avg_video_lengths_df.to_csv(r"Datasets/channel_avg_video_lengths.csv", mode='a')

    # Plot video length distribution for each channel
    for channel_title, data in channels_data.items():
        plot_video_length_distribution(data["videos"], channel_title)
if __name__ == "__main__":
    main()