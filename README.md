A simple script to take screenshots of fonts.
You will need to provide:
 - path to folder containing fonts or font path.
 - path to aegisub executable.

This script is not fail-safe at all. You MUST not press any key during
execution of this script. Your open windows might close abruptly.

```python script.py -h
usage: script.py [-h] [-aegisub AEGISUB] path

positional arguments:
  path              path to a font file or to a folder containing fonts.

optional arguments:
  -h, --help        show this help message and exit
  -aegisub AEGISUB  path to executable of Aegisub application. [default:
                    C:\Program Files (x86)\Aegisubegisub32.exe]
```
