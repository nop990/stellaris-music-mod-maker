import os
import shutil
from PIL import Image
from mutagen.oggvorbis import OggVorbis
from util import stop


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


# Find .mp3, .wav, .flac, .ogg, .m4a files in the given directory
def find_audio_files(directory):
    audio_files = []

    for file in os.listdir(directory):
        full_path = os.path.join(directory, file)
        if os.path.isfile(full_path):
            _, ext = os.path.splitext(full_path)
            if ext.lower() in ['.mp3', '.wav', '.flac', '.ogg', '.m4a']:
                audio_files.append(full_path)

    return audio_files


# Find .ogg files in the given directory
def find_ogg_files(directory):
    ogg_files = []

    for file in os.listdir(directory):
        full_path = os.path.join(directory, file)
        if os.path.isfile(full_path) and full_path.endswith('-smmm-copy.ogg'):
            ogg_files.append(full_path)

    if len(ogg_files) > 0:
        ogg_files = sort_ogg_files_by_track_number(ogg_files)

    return ogg_files


# Check if all files are .ogg
def all_files_are_ogg(files):
    for file in files:
        _, ext = os.path.splitext(file)
        if ext.lower() not in ['.ogg']:
            return False
    return True


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


# Clean up existing mod files
def clean_mod_files(mod_directory):
    if not os.path.exists(mod_directory):
        print("Please create mod first using the Stellaris Launcher. If you have, double check that you copied the "
              "directory path correctly.")
        stop()

    if 'descriptor.mod' not in os.listdir(mod_directory):
        print("descriptor.mod not found in mod directory. Please double check the mod path.")
        stop()

    try:
        if os.listdir(mod_directory) != ['descriptor.mod']:
            delete_confirmation = input("Mod directory is not empty. Do you wish to delete all files except "
                                        "descriptor.mod? {Y\\n}: ")

            if delete_confirmation.lower() == 'n':
                print("Exiting...")
                stop()

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
        stop()

    if 'descriptor.mod' not in os.listdir(mod_directory):
        print("descriptor.mod not found in mod directory. Please double check the mod path.")
        stop()

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
        print("Creating description.txt")
        f.write('[h2]Mod Author[/h2]\n')
        f.write('[h2]Description[/h2]\n')
        f.write('[h2]Compatibility[/h2]\n')
        f.write('[h2]Track List[/h2]\n')
        for ogg_file in ogg_files:
            audio = OggVorbis(ogg_file)
            root, _ = os.path.splitext(ogg_file)
            f.write(f"{audio.get('TRACKNUMBER', [None])[0]} - {os.path.basename(root)}\n")
        f.write('[h2]Credits[/h2]\n')
        f.write(f"Mod generated using the Stellaris Music Mod Maker by nop990")

    print(f"Created mod files in {mod_directory}")


# Deploy music files to mod directory
def deploy_mod(mod_directory, mod_name, ogg_files, audio_files, thumbnail):
    if not os.path.exists(mod_directory):
        print("Please create mod first using the Stellaris Launcher. If you have, double check that you copied the "
              "directory path correctly.")
        stop()

    if 'descriptor.mod' not in os.listdir(mod_directory):
        print("descriptor.mod not found in mod directory. Please double check the mod path.")
        stop()

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


