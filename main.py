import os
import shutil
import sys

from PIL import Image
from mutagen.flac import FLAC
from mutagen.id3 import ID3, ID3NoHeaderError
from mutagen.oggvorbis import OggVorbis
from pydub import AudioSegment


# Find .mp3, .wav, .flac, .ogg files in the given directory
def find_audio_files(directory):
    audio_files = []

    for file in os.listdir(directory):
        full_path = os.path.join(directory, file)
        if os.path.isfile(full_path):
            _, ext = os.path.splitext(full_path)
            if ext.lower() in ['.mp3', '.wav', '.flac', '.ogg']:
                audio_files.append(full_path)

    return audio_files


# Find .ogg files in the given directory
def find_ogg_files(directory):
    ogg_files = []

    for file in os.listdir(directory):
        full_path = os.path.join(directory, file)
        if os.path.isfile(full_path):
            _, ext = os.path.splitext(full_path)
            if ext.lower() in ['.ogg']:
                ogg_files.append(full_path)

    if len(ogg_files) > 0:
        sort_ogg_files_by_track_number(ogg_files)

    return ogg_files


# Check if all files are .ogg
def all_files_are_ogg(files):
    print(files)
    for file in files:
        _, ext = os.path.splitext(file)
        if ext.lower() not in ['.ogg']:
            return False
    return True


# Find a thumbnail (.png, .jpg, .jpeg) in the given directory
def find_thumbnail(directory):
    thumbnail = "resources/thumbnail.png"
    for file in os.listdir(directory):
        full_path = os.path.join(directory, file)
        if os.path.isfile(full_path):
            _, ext = os.path.splitext(full_path)
            if ext.lower() in ['.png', '.jpg', '.jpeg']:
                thumbnail = full_path
    return thumbnail


# Get the track number from an .ogg file
def get_track_number(ogg_file):
    try:
        audio = OggVorbis(ogg_file)
        track_number = audio.get('TRACKNUMBER', [None])[0]

        if track_number:
            track_number = int(track_number.split('/')[0])  # Handle TRACKNUMBER formatted as 'x/y'

        else:
            manual_input = input(
                f"Track number not found in {ogg_file}. Would you like to enter one manually? {{y\\N}}:")

            if manual_input.lower() == 'y':
                track_number = int(input("Enter track number: "))
                audio['TRACKNUMBER'] = str(track_number)  # Save track number to metadata
                audio.save()

            else:
                track_number = float('inf')  # Assign a high value to ensure it sorts last if no track number

        return track_number

    except Exception as e:
        print(f"Error reading {ogg_file}: {e}")
        return float('inf')  # Assign a high value to ensure it sorts last on error


# Sort .ogg files by track number (otherwise they will be sorted by filename)
def sort_ogg_files_by_track_number(ogg_files):
    ogg_files_with_track = [(get_track_number(file), file) for file in ogg_files]
    ogg_files_with_track.sort(key=lambda x: x[0])  # Sort by track number
    sorted_ogg_files = [file for _, file in ogg_files_with_track]
    return sorted_ogg_files


# Convert .mp3, .wav, .flac files to .ogg
def convert_to_ogg(audio_files, mod_name):
    for file_path in audio_files:
        _, ext = os.path.splitext(file_path)
        audio = AudioSegment.from_file(file_path, format=ext.replace('.', ''))

        if audio:
            new_file_path = file_path.replace(ext, '.ogg')

        audio.export(new_file_path, format='ogg')

        copy_metadata(file_path, new_file_path, mod_name)

        print(f"Converted {file_path} to {new_file_path}")


# Copy metadata from .mp3, .flac to .ogg. Create Metadata from .wav title.
def copy_metadata(old_file, new_file, mod_name):
    _, old_ext = os.path.splitext(old_file)

    if not os.path.exists(new_file):
        shutil.copyfile(old_file, new_file)

    if old_ext.lower() == '.mp3':
        try:
            old_metadata = ID3(old_file)
            new_metadata = OggVorbis(new_file)

            if 'TIT2' in old_metadata:
                new_title = f"{old_metadata['TIT2'].text[0]} - {mod_name}"
                new_metadata['TITLE'] = new_title

            if 'TRCK' in old_metadata:
                new_metadata['TRACKNUMBER'] = old_metadata['TRCK'].text[0]

            else:  # If no title is found, use the filename
                new_title = f"{os.path.basename(old_file).replace('.mp3', '')} - {mod_name}"
                new_metadata['TITLE'] = new_title

            new_metadata.save()

        except ID3NoHeaderError:
            print("No ID3 header found in MP3 file.")

    elif old_ext.lower() == '.flac':
        old_metadata = FLAC(old_file)
        new_metadata = OggVorbis(new_file)

        if 'title' in old_metadata:
            new_title = f"{old_metadata['title'][0]} - {mod_name}"
            new_metadata['TITLE'] = new_title

        else:  # If no title is found, use the filename
            new_title = f"{os.path.basename(old_file).replace('.flac', '')} - {mod_name}"
            new_metadata['TITLE'] = new_title

        for key, value in old_metadata.tags.items():
            if key.lower() != 'title':  # Avoid duplicating the title modification
                new_metadata[key.upper()] = value

        new_metadata.save()

    elif old_ext.lower() == '.wav':
        new_metadata = OggVorbis(new_file)
        new_title = f"{os.path.basename(old_file).replace('.wav', '')} - {mod_name}"
        new_metadata['TITLE'] = new_title
        new_metadata.save()

    else:
        print(f"Copying metadata from {old_ext} to .ogg is not supported.")


# Clean up existing mod files
def clean_mod_files(mod_directory):
    if not os.path.exists(mod_directory):
        print("Please create mod first using the Stellaris Launcher. If you have, double check that you copied the "
              "directory path correctly.")
        sys.exit()

    try:
        if os.listdir(mod_directory) != ['descriptor.mod']:
            delete_confirmation = input("Mod directory is not empty. Do you wish to delete all files except "
                                        "descriptor.mod? {Y\\n}: ")

            if delete_confirmation.lower() == 'n':
                print("Exiting...")
                sys.exit()

            else:
                for item in os.listdir(mod_directory):
                    item_path = os.path.join(mod_directory, item)

                    if item == "descriptor.mod":
                        continue  # Skip the descriptor.mod file

                    if os.path.isfile(item_path):
                        os.remove(item_path)  # Delete file

                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)  # Delete directory and all its contents

                print("All files except descriptor.mod have been deleted.")

    except Exception as e:
        print(f"An error occurred: {e}")


# Create songlist.asset, songlist.txt, and description.txt files
def create_mod_files(mod_directory, mod_name, ogg_files):
    if not os.path.exists(mod_directory):
        print("Please create mod first using the Stellaris Launcher. If you have, double check that you copied the "
              "directory path correctly.")
        sys.exit()

    os.makedirs(mod_directory + "/music", exist_ok=True)
    music_directory = os.path.join(mod_directory, "music")
    mod_name = mod_name.replace(" ", "-")

    # songlist.asset must have unique name to not overwrite existing game tracks
    with open(music_directory + f"/songlist-{mod_name}.asset", "w") as f:
        print(f"Creating songlist-{mod_name}.asset")

        for ogg_file in ogg_files:
            root, _ = os.path.splitext(ogg_file)
            f.write("music = {\n")
            f.write(f"\tname = \"{os.path.basename(root)}\"\n")
            f.write(f"\tfile = \"{os.path.basename(ogg_file)}\"\n")
            f.write(f"\tvolume = 1\n")
            f.write("}\n")

    # songlist.txt must have unique name to not overwrite existing game tracks
    with open(music_directory + f"/songlist-{mod_name}.txt", "w") as f:
        print(f"Creating songlist-{mod_name}.txt")

        for ogg_file in ogg_files:
            root, _ = os.path.splitext(ogg_file)
            f.write("song = {\n")
            f.write(f"\tname = \"{os.path.basename(root)}\"\n")
            f.write("}\n")

    with open(mod_directory + f"/description.txt", "w") as f:
        print("Initializing description.txt")
        f.write(f"Mod generated using the Stellaris Music Mod Maker by nop990")

    print(f"Created mod files in {mod_directory}")


# Deploy music files to mod directory
def deploy_mod(mod_directory, mod_name, ogg_files, audio_files, thumbnail):
    if not os.path.exists(mod_directory):
        print("Please create mod first using the Stellaris Launcher. If you have, double check that you copied the "
              "directory path correctly.")
        sys.exit()

    create_mod_files(mod_directory, mod_name, ogg_files)

    if ogg_files != audio_files:
        for ogg_file in ogg_files:
            shutil.move(ogg_file, mod_directory + "/music")

    else:
        for ogg_file in ogg_files:
            shutil.copy(ogg_file, mod_directory + "/music")

    if thumbnail != "resources/thumbnail.png":
        print(thumbnail)
        thumbnail_dir = os.path.dirname(thumbnail)
        new_thumbnail_path = os.path.join(thumbnail_dir, "thumbnail.png")

        if not thumbnail.lower().endswith('.png'):
            img = Image.open(thumbnail)
            img.convert('RGB').save(new_thumbnail_path, "PNG")
            thumbnail = new_thumbnail_path
            shutil.move(thumbnail, mod_directory)
        else:
            shutil.copy(thumbnail, new_thumbnail_path)
            thumbnail = new_thumbnail_path
            shutil.move(thumbnail, mod_directory)

    else:
        shutil.copy(thumbnail, mod_directory)

    print(f"Deployed mod to {mod_directory}")


def main():
    music_directory = input("Enter Music Directory: ")
    mod_directory = input("Enter Mod Directory: ")
    mod_name = input("Enter Mod Name: ")

    audio_files = find_audio_files(music_directory)
    thumbnail = find_thumbnail(music_directory)

    clean_mod_files(mod_directory)

    if all_files_are_ogg(audio_files):
        print("All files are .ogg, skipping conversion...")
        audio_files = sort_ogg_files_by_track_number(audio_files)
        ogg_files = audio_files

    else:
        print(f"Found {len(audio_files)} audio files")
        convert_to_ogg(audio_files, mod_name)
        ogg_files = find_ogg_files(music_directory)

    deploy_mod(mod_directory, mod_name, ogg_files, audio_files, thumbnail)

    print("Mod deployed, opening in file explorer...")
    os.startfile(mod_directory)


if __name__ == '__main__':
    main()
