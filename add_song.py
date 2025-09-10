import argparse
import os
import subprocess
import glob
import configparser

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

music_home_dir = config['addsong']['music_home_dir']
audio_ext = config['addsong']['audio_ext']
browser = config['addsong']['browser']

verbose = False
ansi_orange = "38;5;208"
ansi_red = "38;5;196"


def color_text(text, color_code):
    return f"\033[{color_code}m{text}\033[0m"


def list_playlists():
    playlists = list(
            filter(
                lambda f: os.path.isdir(os.path.join(music_home_dir, f)) and not f.startswith('.'), 
                os.listdir(music_home_dir)
            )
        )
    print(*playlists, sep="  ")


def get_args(parser):
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true", 
        help="Output helpful information during script execution"
    )

    parser.add_argument(
        "-l", "--list",
        action="store_true",
        help="List all available playlists"
    )

    parser.add_argument(
        "-r", "--remove",
        type=str,
        help="Remove a song from the music library"
    )


def write_to_m3u(playlist):
    with open(f"{music_home_dir}/{playlist}/{playlist}.m3u", 'w+') as f:
            for file in glob.glob(os.path.join(f"{music_home_dir}/{playlist}", f'*{audio_ext}')):
                f.write(f"{os.path.basename(file)}\n")


def remove_song(target_name):
    search_path = os.path.join(music_home_dir, '**', f'{target_name}{audio_ext}')
    song_paths = glob.glob(search_path, recursive=True)
                
    if song_paths is None:
        print(color_text(f"Error: Song '{target_name}' not found in any playlist", ansi_red))
        exit(1)

    os.remove(song_paths[0])

    playlist = "music library"
    if os.path.dirname(song_paths[0]) != music_home_dir:
        playlist = os.path.basename(os.path.dirname(song_paths[0]))
        write_to_m3u(playlist)

    print(f"Removed '{target_name}' from {playlist}")


def handle_args(parser):
    args, _ = parser.parse_known_args()

    global verbose 
    verbose = args.verbose
    if verbose: print("Verbose mode enabled")

    if args.list:
        list_playlists()
        exit(0)

    if args.remove is not None:
        remove_song(args.remove)
        exit(0)


def get_metadata_args(parser):
    parser.add_argument(
        "-p", "--playlist", 
        type=str, 
        default=music_home_dir,
        help=f"The playlist you want to save the file to (default: {music_home_dir})"
    )

    parser.add_argument(
        "-t", "--title", 
        type=str, 
        default="%(title)s",
        help=f"The title for the songs metadata you want to change (default: from video metadata)"
    )

    parser.add_argument(
        "-a", "--artist", 
        type=str, 
        default="Unknown Artist",
        help="The artist for the songs metadata you want to change (default: Unknown Artist)"
    )

    parser.add_argument(
        "-s", "--show",
        type=str,
        help="The show for the songs metadata you want to specify"
    )


def get_user_input(args, parser):
    if (args.playlist == parser.get_default("playlist") and
        args.title == parser.get_default("title") and
        args.artist == parser.get_default("artist") and
        args.show is None 
    ):
        list_playlists()
        args.playlist = input(f"Enter playlist from above (skip for none): ") or args.playlist
        args.title = input(f"Enter title (skip for from video metadata): ") or args.title
        args.artist = input(f"Enter artist (skip for {args.artist}): ") or args.artist
        args.show = input(f"Enter show (skip for {args.show}): ") or args.show


def validate_args(args):
    if args.playlist != music_home_dir and not os.path.isdir(os.path.join(music_home_dir, args.playlist)):
        print(color_text(f"Error: Playlist '{args.playlist}' does not exist. Use -l to list available playlists", ansi_red))
        exit(1)
    
    if not args.url.startswith("http"):
        print(color_text(f"Error: URL '{args.url}' is not valid", ansi_red))
        exit(1)


def download_song(args):
    metadata = f"title:{args.title},artist:{args.artist}"
    if args.show is not None:
        metadata += f",show:{args.show}"

    artist_or_blank = f"{args.artist} - " if args.artist != "Unknown Artist" else ""
    show_or_blank = f" ({args.show})" if args.show is not None else ""
    filename = f"{artist_or_blank}{args.title}{show_or_blank}{audio_ext}"

    cmd = [
        "yt-dlp",
        "-x",
        "--audio-format", audio_ext.lstrip('.'),
        "--audio-quality", "0",
        "--cookies-from-browser", browser,
        "--ppa", "EmbedThumbnail+ffmpeg_o:-c:v mjpeg -vf crop=\"'if(gt(ih,iw),iw,ih)':'if(gt(iw,ih),ih,iw)'\"",
        "--embed-thumbnail",
        "--add-metadata",
        "--parse-metadata", metadata,
        "-o", os.path.join(music_home_dir, args.playlist, filename),
        args.url
    ]
    if not verbose: cmd.insert(1, "-q")

    try:
        if subprocess.run(['which', 'yt-dlp'], capture_output=True).returncode != 0:
            print("yt-dlp not found, installing...")
            subprocess.run(['pip', 'install', '--upgrade', 'yt-dlp'], check=True)
            print("yt-dlp installed successfully")

        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(color_text(f"Error: {e}", ansi_red))
        exit(1)


def main():
    parser = argparse.ArgumentParser(
        description=f"{os.path.basename(__file__)} downloads a youtube mp3 file to {music_home_dir}"
    )

    get_args(parser)
    handle_args(parser)

    get_metadata_args(parser)

    parser.add_argument(
        "url",
        type=str, 
        help="The youtube url of the song you want to download"
    )

    args, unknown_args = parser.parse_known_args()

    validate_args(args)
    get_user_input(args, parser)
    validate_args(args)

    if verbose:
        if unknown_args != []: print(color_text(f"Warning: Unknown args: {unknown_args}", ansi_orange))
        print(", ".join(f"{key}: {value}" for key, value in args.__dict__.items()))
    
    print("Downloading song...")
    download_song(args)
    print("Download complete!")

    mp3_files = glob.glob(os.path.join(music_home_dir, f'*{audio_ext}')) + glob.glob(os.path.join(music_home_dir, args.playlist, f'*{audio_ext}'))
    most_recent_mp3_file = max(mp3_files, key=os.path.getctime)
    song_name = os.path.basename(most_recent_mp3_file).rsplit('.', 1)[0]

    print(f'"{song_name}" added to {args.playlist}')

    if args.playlist != music_home_dir:
        write_to_m3u(args.playlist)


if __name__ == "__main__":
    main()