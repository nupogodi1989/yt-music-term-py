from ytmusicapi import YTMusic
from InquirerPy import inquirer
import subprocess

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

    # Open yt-dlp process to fetch audio
    ytdlp = subprocess.Popen(
        ["yt-dlp", "-q", "-o", "-", "-f", "bestaudio", url],
        stdout=subprocess.PIPE
    )

    # Open ffplay process to play audio
    ffplay = subprocess.Popen(
        ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", "-"],
        stdin=ytdlp.stdout
    )

    # Make sure yt-dlp's stdout is connected to ffplay
    ytdlp.stdout.close()

    # Wait until ffplay finishes playing
    ffplay.wait()



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
