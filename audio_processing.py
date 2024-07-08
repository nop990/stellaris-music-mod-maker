from mutagen.flac import FLAC
from mutagen.id3 import ID3, ID3NoHeaderError
from mutagen.mp4 import MP4
from pydub import AudioSegment
from mutagen.oggvorbis import OggVorbis
import shutil
import os


# Convert .mp3, .wav, .flac files to .ogg
def convert_to_ogg(audio_files, mod_name):
    for file_path in audio_files:
        _, ext = os.path.splitext(file_path)
        audio = AudioSegment.from_file(file_path, format=ext.replace('.', ''))

        new_file_path = file_path.replace(ext, '-smmm-copy.ogg')

        audio.export(new_file_path, format='ogg')

        copy_metadata(file_path, new_file_path, mod_name)

        if ext.lower() != '.ogg':
            print(f"Copied/Converted {os.path.basename(file_path)} to {os.path.basename(new_file_path)}")

        else:
            print(f"Copied {os.path.basename(file_path)} to {os.path.basename(new_file_path)}")


# Copy metadata from .mp3, .flac to .ogg. Create metadata from .wav title
def copy_metadata(old_file, new_file, mod_name):
    _, old_ext = os.path.splitext(old_file)

    if not os.path.exists(new_file):
        shutil.copyfile(old_file, new_file)

    # MP3
    if old_ext.lower() == '.mp3':
        copy_id3_metadata(old_file, new_file, old_ext, mod_name)

    # FLAC
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

    # M4A
    elif old_ext.lower() == '.m4a':
        old_metadata = MP4(old_file)
        new_metadata = OggVorbis(new_file)

        if '\xa9nam' in old_metadata:
            new_title = f"{old_metadata['\xa9nam'][0]} - {mod_name}"
            new_metadata['TITLE'] = new_title

        else:
            new_title = f"{os.path.basename(old_file).replace('.m4a', '')} - {mod_name}"
            new_metadata['TITLE'] = new_title

        if '\xa9ART' in old_metadata:
            new_metadata['ARTIST'] = str(old_metadata['\xa9ART'][0])

        if '\xa9alb' in old_metadata:
            new_metadata['ALBUM'] = str(old_metadata['\xa9alb'][0])

        if 'trkn' in old_metadata:
            new_metadata['TRACKNUMBER'] = str(old_metadata['trkn'][0][0])

        if '\xa9wrt' in old_metadata:
            new_metadata['COMPOSER'] = str(old_metadata['\xa9wrt'][0])

        new_metadata.save()

    # WAV
    elif old_ext.lower() == '.wav':
        copy_id3_metadata(old_file, new_file, old_ext, mod_name)

    elif old_ext.lower() == '.ogg':
        old_metadata = OggVorbis(old_file)
        new_metadata = OggVorbis(new_file)

        for key, value in old_metadata.items():
            new_metadata[key] = value

        if 'TITLE' not in new_metadata:
            new_title = f"{os.path.basename(old_file).replace('.ogg', '')} - {mod_name}"
            new_metadata['TITLE'] = new_title

        new_metadata.save()

    # Unsupported Format
    else:
        print(f"Copying metadata from {old_ext} to .ogg is not supported.")


# Copy ID3 metadata from .mp3/.wav to .ogg
def copy_id3_metadata(old_file, new_file, old_ext, mod_name):
    try:
        old_metadata = ID3(old_file)
        new_metadata = OggVorbis(new_file)

        if 'TIT2' in old_metadata:
            new_title = f"{old_metadata['TIT2'].text[0]} - {mod_name}"
            new_metadata['TITLE'] = new_title
        else:  # If no title is found, use the filename
            new_title = f"{os.path.basename(old_file).replace(f'{old_ext}', '')} - {mod_name}"
            new_metadata['TITLE'] = new_title

        if 'TPE1' in old_metadata:  # Artist
            new_metadata['ARTIST'] = old_metadata['TPE1'].text[0]

        if 'TALB' in old_metadata:  # Album
            new_metadata['ALBUM'] = old_metadata['TALB'].text[0]

        if 'TRCK' in old_metadata:
            new_metadata['TRACKNUMBER'] = old_metadata['TRCK'].text[0]

        new_metadata.save()

    except ID3NoHeaderError:
        print(f"No ID3 header found in {old_ext} file, or {old_ext} does not support ID3 tags. "
              "Generating metadata from file name.")
        new_metadata = OggVorbis(new_file)
        new_title = f"{os.path.basename(old_file).replace('.wav', '')} - {mod_name}"
        new_metadata['TITLE'] = new_title
        new_metadata.save()
