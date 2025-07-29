import time
import subprocess
import sys
from importlib.metadata import version as get_installed_version, PackageNotFoundError
from packaging.version import parse as parse_version


def check_for_package_updates(package_name):
    try:
        try:
            installed_version = get_installed_version(package_name)
        except PackageNotFoundError:
            return f"{package_name} is not installed.", 404
        result = subprocess.run(
            [sys.executable, "-m", "pip", "index", "versions", package_name],
            capture_output=True, text=True
        )

        if result.returncode != 0:
            return f"Failed to fetch versions from PyPI: {result.stderr.strip()}", 403

        output = result.stdout
        lines = output.splitlines()
        for line in lines:
            if line.startswith("Available versions:"):
                latest_version = line.split(":")[1].split(",")[0].strip()
                break
        else:
            return f"Could not find version info for {package_name}.", 404

        if parse_version(latest_version) > parse_version(installed_version):
            return f"Update available for {package_name}! Installed: {installed_version}, Latest: {latest_version}", 202
        else:
            return f"{package_name} is up to date (version {installed_version}).", 200

    except Exception as e:
        return f"An error occurred: {e}", 500


def pretty_print(text, delay=0.05, end=True, flush=True):
    for char in text:
        print(char, end='' ,flush=True)
        time.sleep(delay)
    print(end='\n' if end else '', flush=flush)

def reverse_pretty_print(text, delay=0.05, end=False, flush=True):
    result = ""
    for char in reversed(text):
        result = char + result
        print('\r' + result, end='', flush=True)
        time.sleep(delay)
    print(end='\n' if end else '', flush=flush)



def rgb_text(r, g, b, text):
    return f"\033[38;2;{r};{g};{b}m{text}\033[0m"

def interpolate_color(color1, color2, factor):
    return tuple(int(c1 + (c2 - c1) * factor) for c1, c2 in zip(color1, color2))

def generate_gradient_colors(text_length, color_points):
    if text_length < 2 or len(color_points) < 2:
        return [color_points[0]] * text_length

    segment_length = text_length / (len(color_points) - 1)
    colors = []

    for i in range(text_length):
        segment = int(i / segment_length)
        factor = (i % segment_length) / segment_length

        if segment >= len(color_points) - 1:
            segment = len(color_points) - 2
            factor = 1.0

        start_color = color_points[segment]
        end_color = color_points[segment + 1]
        colors.append(interpolate_color(start_color, end_color, factor))

    return colors

def gradient_text(text, *color_points):
    colors = generate_gradient_colors(len(text), color_points)
    gradient_text = "".join(
        f"\033[38;2;{r};{g};{b}m{c}" for c, (r, g, b) in zip(text, colors)
    )
    gradient_text += "\033[0m"
    return gradient_text

def pretty_gradient_print(text, *color_points, delay=0.05, end=True, flush=True):
    colors = generate_gradient_colors(len(text), color_points)
    for c, (r, g, b) in zip(text, colors):
        print(f"\033[38;2;{r};{g};{b}m{c}\033[0m", end='', flush=True)
        time.sleep(delay)
    print(end='\n' if end else '', flush=flush)


def help():
    info = """
Available Functions:

1. check_for_package_updates(package_name)
   - Checks if the given package has a newer version on PyPI.
   - Returns a tuple: (message, status_code)
   - Status Codes:
       200: Package is up to date
       202: Update available
       403: Failed to fetch version info
       404: Package not installed or info not found
       500: Unknown error

2. pretty_print(text, delay=0.05, end=True, flush=False)
   - Prints text one character at a time with an optional delay.
   - Use for animated output.

3. reverse_pretty_print(text, delay=0.05, end=False)
   - Prints text in reverse typing effect (right to left).

4. rgb_text(r, g, b, text)
   - (Deprecated for basic terminals)
   - Originally used to color text with RGB values using ANSI escape codes.
   - On basic terminals, this will just return the plain text.

5. gradient_text(text, *color_points)
   - (Deprecated for basic terminals)
   - Returns the text with gradient RGB coloring (if supported).

6. pretty_gradient_print(text, *color_points, delay=0.05, end=True)
   - (Deprecated for basic terminals)
   - Prints text character by character with color gradient (if supported).

7. help()
   - Displays this help message.
"""
    print(info)




