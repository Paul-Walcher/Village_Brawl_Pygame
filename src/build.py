import os
import shutil
from distutils.dir_util import copy_tree



if __name__ == "__main__":

    pre_str = "python -m PyInstaller --clean --noconfirm --onedir --name VillageBrawl --collect-submodules playsets --add-data BaseAssets:BaseAssets "

    playset_path = "playsets"

    playsets = os.listdir(playset_path)

    if "build" in os.listdir("."):
        shutil.rmtree("build")

    add_folders = []
    for fname in playsets:
        prepath = os.path.join(playset_path, fname)
        if os.path.isdir(prepath):

            if "assets" in os.listdir(prepath):
                asset_path = os.path.join(prepath, "assets")
                pre_str += f"--add-data {asset_path}:{asset_path} "
            else:
                add_folders.append(fname)

    pre_str += "main.py"

    os.system(pre_str)

    #cleanup
    shutil.move("dist", "build", copy_function=shutil.copytree)
    shutil.move("VillageBrawl.spec", os.path.join("build", "VillageBrawl.spec"))

    #
    exe_path = os.path.join("build", "dist", "VillageBrawl")
    copy_tree(os.path.join(exe_path, "_internal", "BaseAssets"), os.path.join(exe_path, "BaseAssets"))
    copy_tree(os.path.join(exe_path, "_internal", "playsets"), os.path.join(exe_path, "playsets"))

    for folder in add_folders:
        os.makedirs(os.path.join(exe_path, "_internal", "playsets", folder), exist_ok=True)
        os.makedirs(os.path.join(exe_path, "playsets", folder), exist_ok=True)
