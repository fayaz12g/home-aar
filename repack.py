import os
import sys
import time

try:
    import SarcLib
except ImportError:
    print("SarcLib is not installed!")
    ans = input("Do you want to install it now? (y/n)\t")
    if ans.lower() == 'y':
        import pip
        pip.main(['install', 'SarcLib==0.3'])
        del pip
        import SarcLib
    else:
        sys.exit(1)

try:
    import libyaz0
except ImportError:
    print("libyaz0 is not installed!")
    ans = input("Do you want to install it now? (y/n)\t")
    if ans.lower() == 'y':
        import pip
        pip.main(['install', 'libyaz0==0.5'])
        del pip
        import libyaz0
    else:
        sys.exit(1)

def pack_folder_to_blarc(folder_path, output_file, x):
    """
    Pack the files and folders in the folder_path to a .blarc output_file.
    """
    root = os.path.abspath(folder_path)
    endianness = '>'
    level = 9

    pack(root, endianness, level, output_file, x)

def pack(root, endianness, level, outname, x):
    """
    Pack the files and folders in the root folder.
    """
    if "\\" in root:
        root = "/".join(root.split("\\"))

    if root[-1] == "/":
        root = root[:-1]

    arc = SarcLib.SARC_Archive(endianness=endianness)
    lenroot = len(root.split("/"))

    for path, dirs, files in os.walk(root):
        if "\\" in path:
            path = "/".join(path.split("\\"))

        lenpath = len(path.split("/"))

        if lenpath == lenroot:
            path = ""

        else:
            path = "/".join(path.split("/")[lenroot - lenpath:])

        for file in files:
            if path:
                filename = ''.join([path, "/", file])

            else:
                filename = file

            print(f"Repacking {filename}")
            
            if filename == "timg/__Combined.bntx":
                print("Writing file. Please wait. This step takes the longest, and will happen a few times due to strict compression.")
                print(f"({x}/12)")

            fullname = ''.join([root, "/", filename])

            i = 0
            for folder in filename.split("/")[:-1]:
                if not i:
                    exec("folder%i = SarcLib.Folder(folder + '/'); arc.addFolder(folder%i)".replace('%i', str(i)))

                else:
                    exec("folder%i = SarcLib.Folder(folder + '/'); folder%m.addFolder(folder%i)".replace('%i', str(i)).replace('%m', str(i - 1)))

                i += 1

            with open(fullname, "rb") as f:
                inb = f.read()

            hasFilename = True
            if file[:5] == "hash_":
                hasFilename = False

            if not i:
                arc.addFile(SarcLib.File(file, inb, hasFilename))

            else:
                exec("folder%m.addFile(SarcLib.File(file, inb, hasFilename))".replace('%m', str(i - 1)))

    data, maxAlignment = arc.save()

    if level != -1:
        outData = libyaz0.compress(data, maxAlignment, level)
        del data

        if not outname:
            outname = ''.join([root, ".szs"])
            print(f"Writing {outname}")

    else:
        outData = data
        if not outname:
            outname = ''.join([root, ".sarc"])
            # print(f"Writing {outname}")

    with open(outname, "wb+") as output:
        # print(f"Writing {outname}")
        output.write(outData)