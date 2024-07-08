import os
import shutil
import sys

version = '1.1.0'

# Creates a file with information about the program
def create_about_file():
    with open("resources/about.txt", "w") as f:
        f.write(f"Stellaris Music Mod Maker v{version}\n")
        f.write("Created by nop990\n")
        f.write("Link to GitHub: https://github.com/nop990/stellaris-music-mod-maker\n")

    print("Created resources/about.txt")


# Zips the dist folder
def zip_dist():
    if not os.path.exists('package'):
        os.mkdir('package')

    if os.path.exists(f"package/SMMM_{version}.zip"):
        os.remove(f"package/SMMM_{version}.zip")

    shutil.copy('resources/about.txt', 'dist/about.txt')
    shutil.copy('ReadMe.md', 'dist/ReadMe.md')
    shutil.copy('LICENSE', 'dist/LICENSE')
    shutil.make_archive(f"package/SMMM_{version}", 'zip', 'dist')
    print(f"Created dist/SMMM_{version}.zip")


# Installs the program using PyInstaller
def py_install():
    if os.path.exists('dist'):
        shutil.rmtree('dist')

    os.system(f"python -m PyInstaller main.spec")

    print("PyInstaller finished")


# Deletes all files with the name '-smmm-copy.ogg' in the music directory
def delete_smmm_copy_files(music_directory):
    if music_directory:
        for file in os.listdir(music_directory):
            if file.endswith('-smmm-copy.ogg'):
                os.remove(os.path.join(music_directory, file))


# Stops the program without closing the console
def stop():
    sys.tracebacklimit = 1
    raise ValueError("Exiting...")


if __name__ == "__main__":
    option = input('Specify option (about, install, zip, all): ')

    if option == 'about':
        create_about_file()
    elif option == 'install':
        py_install()
    elif option == 'zip':
        zip_dist()
    elif option == 'all':
        create_about_file()
        py_install()
        zip_dist()
    else:
        raise ValueError('Invalid option')
