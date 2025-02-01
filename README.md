🇷🇺 Русская версия README доступна здесь: [README_RU.md](https://github.com/FluffyKn1ght/Titleify/blob/main/README_RU.md.

# Titleify
A video to Minecraft Java 1.20+ /title convrter. Powered by Python and FFmpeg.

## Can it play Bad Apple?
A question so old and important, I'm just gonna put the answer here, at the top. **Yes, it can, here's proof:** [Click!](https://www.youtube.com/watch?v=enCyQBkFMSw)

## How does it work?
Titleify utilizes Minecraft's bitmap font feature, which allows users to replace any character in the game with a PNG file. The size is, unfortunately, limited to 256x256, however, that's still enough to play most videos.

Titleify uses FFmpeg to extract all frames from a given video, changing the framerate to 20FPS (the max that Minecraft can do) and limiting the size to 256x256 (resized to match source aspect ratio). Then, it generates a resourcepack and a datapack, which, when combined, allow players to see any video in Minecraft in **real-time!**

## How do I use it?
**Note:** This requires Minecraft *JAVA EDITION*, specifically, 1.20+ (older versions may or may not work).

To use Titleify, download it from the repo, extract it somewhere, and drag any video file onto it!

*Or, if you'd like to use the terminal, run `python titleify.py <pathToYourVideo>`.*

## I get an FFmpeg conversion error!
Try a different video format, or a different video file.

## When I load my world, the video plays with no sound
Disable the datapack, and re-enable it again.

## Instead of a video, I see a square.
You didn't apply the resourcepack. (It may take a while to load it)