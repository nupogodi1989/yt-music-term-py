from ytmusicapi import YTMusic
from InquirerPy import inquirer
import subprocess
import threading
import sys

def play_song(url):
    """
    Plays the song using yt-dlp piped to ffplay.
    Returns the Popen objects so we can control them.
    """
    # Start yt-dlp process
    ytdlp = subprocess.Popen(
        ["yt-dlp", "-q", "-o", "-", "-f", "bestaudio", url],
        stdout=subprocess.PIPE
    )

    # Start ffplay process
    ffplay = subprocess.Popen(
        ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", "-"],
        stdin=ytdlp.stdout,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    ytdlp.stdout.close() # allow yt-dlp to receive a SIGPIPE if ffplay exits
    return ytdlp, ffplay

def search_and_play_song(ytmusic):
    query = inquirer.text(message="Search for:").execute()
    results = ytmusic.search(query, filter="songs")

    if not results:
        print("No results found.")
        return
    
    choices = [
        {
            "name": f"{song['title']} - {song['artists'][0]['name']}",
            "value": song
        }
        for song in results[:5]
    ]

    selected_song = inquirer.select(
        message="Selected a song:",
        choices=choices,
    ).execute()

    url = f"https://music.youtube.com/watch?v={selected_song['videoId']}"
    print(f"Playing: {selected_song['title']} by {selected_song['artists'][0]['name']}")

    # Start playback in a separate thread
    ytdlp, ffplay = play_song(url)

    print("\nControls: [p]ause/resume, [s]top, [q]uit playback")
    paused = False
    
    while True:
        cmd = input().lower()
        if cmd == "p":
            if not paused:
                ffplay.send_signal(subprocess.signal.SIGSTOP) # pause
                paused = True
                print("Paused")
            else:
                ffplay.send_signal(subprocess.signal.SIGCONT) # resume
                paused = False
                print("Resumed")
        elif cmd == "s" or cmd == "q":
            ffplay.terminate()
            ytdlp.terminate()
            print("Stopped playback")
            break
    
    # Wait to make sure processes have exited
    ffplay.wait()
    ytdlp.wait()

def main():
    ytmusic = YTMusic("headers_auth.json")

    while True:
        choice = inquirer.select(
            message="Choose an action:",
            choices=["Search song", "Quit"],
        ).execute()

        if choice == "Quit":
            print("Goodbye!")
            break
        elif choice == "Search song":
            search_and_play_song(ytmusic)

if __name__ == "__main__":
    main()
