# Titleify - A video to Minecraft Java 1.20+ /title convrter. Powered by Python and FFmpeg.
# Written by FluffyKn1ght
# https://github.com/fluffykn1ght/titleify

# Import modules
try:
    import ffmpeg
    import ffmpeg.asyncio
    import asyncio
    import ffprobe # ffprobe-python
    import os
    import pathlib
    import json
    from PIL import Image # pillow
    from tqdm import tqdm # tqdm
    import sys
except ModuleNotFoundError:
    print("ERROR: Not all required modules present!")
    input("Press Enter to run 'pip install -r req.txt'")
    os.system("pip install -r req.txt")
    print("Finished! Restart the script now.")
    done()

lastFrame: int = 0 # fix "name lastFrame is not defined"

# A function to stop the program in case of completion/an error
def done():
    input("\nPress Enter to exit...")
    exit()

# Probe file for metadata using FFprobe
def getMetadata(filename: str):
    try: return ffprobe.FFProbe(filename)
    except OSError as e:
        # huge shoutout to gbstack for making all errors go to OSError
        if e.args[0] == "ffprobe not found.":
            print("ERROR: FFprobe not found! Please install FFmpeg it from https://ffmpeg.org/download.html and add it to PATH.")
            done()
        elif "No such media file" in e.args[0]:
            print(f"ERROR: Could not find input video file.")
            done()

# Extracts the audio from an input video and saves it as an .ogg
async def extractAudio(input: str, output: str):
    print("Extracting audio...")
    # Create the FFmpeg instance
    ff = (
        ffmpeg.asyncio.FFmpeg()
        .option("y")
        .input(input)
        .option("vn") # Strip the video
        .output(
            f"{output}/audio.ogg"
        )
    )
    
    # Do the thing
    try:
        await ff.execute()
    except FileNotFoundError as e:
        print("ERROR: FFmpeg not found! Please install FFmpeg from https://ffmpeg.org/download.html and add it to PATH.")
        done()
    except ffmpeg.errors.FFmpegFileNotFound as e:
        print(f"ERROR: Could not find input video file.")
        done()
    except ffmpeg.errors.FFmpegError as e:
        print(f"ERROR: FFmpeg has reported a conversion failure. Try again?")
        done()

# Extracts the frames from an input video to a bunch of images
async def extractFrames(input: str, output: str):
    print("Extracting frames... (this may take some time!)")
    # FFprobe the video for metadata
    probe = getMetadata(input)
    meta = None
    for stream in probe.streams:
        if stream.is_video():
            meta = stream
    
    # Ensure we have a video stream to titleify
    if not meta:
        print("ERROR: Input file doesn't have any video streams!")
        done()
    
    # Decide on a resolution
    if meta.frame_size()[0] < meta.frame_size()[1]:
        vf = "scale=-1:256"
    else:
        vf = "scale=256:-1"

    # Create the FFmpeg instance
    ff = (
        ffmpeg.asyncio.FFmpeg()
        .option("y")
        .input(input)
        .output(
            f"{output}/frame%00d.png",
            {"vf": vf, "r": 20}
        )
    )
    try: f = meta.frames()
    except ffprobe.exceptions.FFProbeError:
        print("WARN: FFprobe reported a probe error. Things may break")
        f = None
    # Do the thing
    try:
        with tqdm(total=f) as pbar:
            # Set up progress bar updates
            @ff.on("progress")
            def updatePbar(progress: ffmpeg.progress.Progress):
                global lastFrame
                pbar.update(progress.frame - lastFrame)
                lastFrame = progress.frame
            await ff.execute()

    except FileNotFoundError as e:
        print("ERROR: FFmpeg not found! Please install FFmpeg from https://ffmpeg.org/download.html and add it to PATH.")
        done()
    except ffmpeg.errors.FFmpegFileNotFound as e:
        print(f"ERROR: Could not find input video file.")
        done()
    except ffmpeg.errors.FFmpegError as e:
        print(f"ERROR: FFmpeg has reported a conversion failure. Try again?")
        done()

# Packages up the media files into a resource pack. Returns the amount of packaged frames
async def packageMedia(output: str, tempdir: str) -> int:
    print("Creating folder structure...")
    # First of all, create the basic resourcepack structure
    pathlib.Path(os.path.join(os.getcwd(), output, "assets", "minecraft", "font")).mkdir(parents=True, exist_ok=True) # Frame config
    pathlib.Path(os.path.join(os.getcwd(), output, "assets", "minecraft", "textures", "frames")).mkdir(parents=True, exist_ok=True) # Frames
    pathlib.Path(os.path.join(os.getcwd(), output, "assets", "minecraft", "sounds")).mkdir(parents=True, exist_ok=True) # Sound
    
    # Write the font, sound and resourcepack configs
    # Sound config
    print("Writing sounds.json...")
    with open(os.path.join(os.getcwd(), output, "assets", "minecraft", "sounds.json"), "w") as f:
        json.dump({"titleifysound": {"sounds": ["audio"]}}, f)
    # Font config
    with open(os.path.join(os.getcwd(), output, "assets", "minecraft", "font", "default.json"), "w", encoding="utf-8") as f:
        fontconfig = {"providers": []}
        count = 0xE001
        tooManyFramesWarnFlag = False
        print("Writing rp/font/default.json...")
        for filename in tqdm(os.listdir(tempdir)):
            if not filename.startswith("frame") or not filename.endswith(".png"): continue # Skip non-frame files
            img = Image.open(os.path.join(os.getcwd(), "temp", filename))
            fontconfig["providers"].append({"type": "bitmap", "file": f"minecraft:frames/frame{int(count - 0xE000)}.png", "height": img.height, "ascent": int(img.height/2), "chars": [chr(count)]})
            img.close()
            count += 0x0001
            if count > 0xEFFF and not tooManyFramesWarnFlag:
                tooManyFramesWarnFlag = True
            if count >= 0xFFFF:
                print("\nERROR: Ran out of Unicode symbols while writing\n font/default.json! Converted video has too way many frames.")
                print("CONVERSION NOT COMPLETE - PACKS WON'T WORK!")
                done()
        if tooManyFramesWarnFlag: print("\nWARN: Converted video has more than 4094 frames! Possible breakage may occur.")
        json.dump(fontconfig, f)

    # Resourcepack config
    print("Writing rp/pack.mcmeta...")
    with open(os.path.join(os.getcwd(), output, "pack.mcmeta"), "w") as f:
        f.write('{"pack": {"pack_format": 32, "description": "Titleify Resourcepack"}}')
        
    # Finally, move the files
    print("Moving files...")
    for filename in tqdm(os.listdir(tempdir)):
        if filename.endswith(".png"):
            try: os.rename(os.path.join(os.getcwd(), tempdir, filename), os.path.join(os.getcwd(), output, "assets", "minecraft", "textures", "frames", filename))
            except FileExistsError: pass
        elif filename == "audio.ogg":
            try: os.rename(os.path.join(os.getcwd(), tempdir, filename), os.path.join(os.getcwd(), output, "assets", "minecraft", "sounds", filename))
            except FileExistsError: pass

    return int(count - 0xE000) # Return frame count

# Creates the datapack which will handle the video playback
async def generateDatapack(output: str, frames: int):
    print("Creating folder structure...")
    # Generate folder structure
    pathlib.Path(os.path.join(os.getcwd(), output, "titleify", "data", "titleify", "functions")).mkdir(parents=True, exist_ok=True) # Frame config
    pathlib.Path(os.path.join(os.getcwd(), output, "titleify", "data", "minecraft", "tags", "functions")).mkdir(parents=True, exist_ok=True) # Frame config
    
    print("Writing dp/pack.mcmeta...")
    # Create pack.mcmeta
    with open(os.path.join(os.getcwd(), output, "titleify", "pack.mcmeta"), "w") as f:
        f.write('{"pack":{"pack_format":18,"description":"Titleify Datapack"}}')
    
    print("Writing datapack files... (1/3)")
    # Create tag files and some startup QoL stuff
    with open(os.path.join(os.getcwd(), output, "titleify", "data", "titleify", "functions", "load.mcfunction"), "w") as f:
        f.write('tellraw @a {"text": "Titleify datapack loaded!", "color": "#00FF00", "bold": true}\n')
        f.write("scoreboard players set timer timer 0\n")
        f.write("playsound minecraft:titleifysound master @a ~ ~ ~ 100 1 0\n")
    with open(os.path.join(os.getcwd(), output, "titleify", "data", "minecraft", "tags", "functions", "load.json"), "w") as f:
        f.write('{"values":["titleify:load"]}')
    with open(os.path.join(os.getcwd(), output, "titleify", "data", "minecraft", "tags", "functions", "tick.json"), "w") as f:
        f.write('{"values":["titleify:play"]}')
        
    print("Writing datapack files... (2/3)")
    # Finally, write the playback function
    with open(os.path.join(os.getcwd(), output, "titleify", "data", "titleify", "functions", "play.mcfunction"), "w", encoding="utf-8") as f:
        f.write("title @a reset\n")
        f.write("title @a times 0 5 0\n")
        f.write("scoreboard players add timer timer 1\n")
        print("Writing datapack files... (3/3)")
        for frame in tqdm(range(frames)):
            f.write(f'execute if score timer timer matches {frame} run title @a title ' + '[{"text": "' + chr(int(0xE000 + frame)) + '", "color": "white"}]\n')
        
# Actual script control flow logic
async def Titleify():
    # Welcome thing
    print("TITLEIFY - A video to MC Java /title converter\nMade by FluffyKn1ght\nhttps://github.com/fluffykn1ght/titleify\n")

    # Input video file path check
    if len(sys.argv) < 1:
        print("ERROR: Bad input video file!\n")
        print(
            "No input video file specified! Please provide one\n by either:\n- Dragging it onto the script in your file manager\n- Running 'python titleify.py path/to/file' in your terminal")
        done()
    if not os.path.exists(sys.argv[1]):
        print("ERROR: Bad input video file!\n")
        print("The provided input video file no longer exists\n or the path to it is not valid!")
        done()

    # Output folder check
    if os.path.exists(os.path.join(os.getcwd(), "resourcepack")):
        print("ERROR: 'resourcepack' folder already present\nin script directory! Please delete it.")
        done()
    if os.path.exists(os.path.join(os.getcwd(), "datapack")):
        print("ERROR: 'datapack' folder already present\nin script directory! Please delete it.")
        done()
    if os.path.exists(os.path.join(os.getcwd(), "temp")):
        print("ERROR: 'temp' folder already present\nin script directory! Please delete it.")
        done()

    # Create (now guaranteed to be empty) output folders
    print("Creating output folders...")
    pathlib.Path(os.path.join(os.getcwd(), "temp")).mkdir(parents=True)
    pathlib.Path(os.path.join(os.getcwd(), "resourcepack")).mkdir(parents=True)
    pathlib.Path(os.path.join(os.getcwd(), "datapack")).mkdir(parents=True)

    print("=== Starting generation with input video file:\n" + sys.argv[1])

    # Extract frames
    await extractFrames(sys.argv[1], "temp")
    # Extract audio
    await extractAudio(sys.argv[1], "temp")

    # Create resourcepack
    print("Packaging media into resourcepack... (may take some time!)")
    frames = await packageMedia("resourcepack", "temp")
    # Create datapack
    print("Creating datapack...")
    await generateDatapack("datapack", frames)

    # Final instuctions
    print("\n=== SUCCESS! Conversion finished.")
    print("\nNOTICE: 1.20+ RECOMMENDED! Older versions may not work.")
    print("\nNow, here's how to play it in MC Java:\n> Drop the 'resourcepack' folder into '.minecraft/resourcepacks', and apply it ingame.\n- Drop the folder itself, not its contents!\n> Go into the 'datapack' folder and drop the 'titleify' folder\n  into '.minecraft/saves/<your world>/datapacks'\n> Don't drop 'datapack', it won't work! Make sure you're moving 'titleify'!\n> Open your world, and type '/scoreboard objectives add timer dummy'\n- You only have to do this once per world.\nThen, type '/datapack enable ""file/titleify"" (or /reload)'. The video will start.\n- GUI Scale of 1 is recommended for this. Modded users - make sure you have titles on!\n> Enjoy!")
    done()

# Finally, run the script
if __name__ == "__main__":
    asyncio.run(Titleify())