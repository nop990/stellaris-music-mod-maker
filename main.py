import os
import sys

from audio_processing import convert_to_ogg
from display import print_title
from file_management import find_audio_files, find_thumbnail, clean_mod_files, all_files_are_ogg, \
    sort_ogg_files_by_track_number, find_ogg_files, deploy_mod
from util import delete_smmm_copy_files


def main():
    try:
        print_title()

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
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.tracebacklimit = 1
        raise ValueError()
    finally:
        delete_smmm_copy_files(music_directory)
        input("Press Enter to exit...")


if __name__ == '__main__':
    main()
