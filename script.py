import os
import sys
import time
import argparse

from fontTools import ttLib
from pywinauto.keyboard import SendKeys
from pywinauto.application import Application


def process_params():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='path to a font file or to a folder containing fonts.')
    parser.add_argument('-aegisub', help='path to executable of Aegisub application. ' \
        '[default: C:\Program Files (x86)\Aegisub\aegisub32.exe]',
        default='C:\\Program Files (x86)\\Aegisub\\aegisub32.exe')
    
    args = parser.parse_args()
    print(args.__dict__)

    return args

def get_font_name(font_file):
    font = ttLib.TTFont(font_file)
    for record in font['name'].names:
        if record.platformID == 3 and record.nameID == 1:
            return str(record)

def take_fontshot(font_name):
    font_name = font_name.replace(' ', '{SPACE}')
    SendKeys(font_name)
    SendKeys('{TAB}' * 2)
    SendKeys('%{PRTSC}')

def save_fontshot(image_name, folder_name):
    image_name = image_name.replace(' ', '{SPACE}')
    SendKeys('^v')
    SendKeys('%fa')

    full_image_path = os.path.join(folder_name,
      image_name + '.jpg')

    index = 2
    while os.path.exists(full_image_path.replace(
      '{SPACE}', ' ').replace('+9', '(').replace('+0', ')')):
      
      name, ext = os.path.splitext(full_image_path)
      if '{SPACE}+9' in name:
        name = name[:name.find('{SPACE}+9')]

      full_image_path = name + ('{SPACE}+9%d+0' % (index)) + ext
      index += 1

    SendKeys(full_image_path)
    SendKeys('{ENTER}' * 2)

def start_aegisub_routine():
    SendKeys('%ss')
    SendKeys('%e')
    SendKeys('{TAB}' * 5)
    SendKeys('{TAB}' * 2)

def start_paint_routine():
    time.sleep(1)
    SendKeys('%hre{RIGHT}{TAB}200{ENTER}')

def initializeDesktopApps(aegisub):

    app = Application(backend='uia')
    app.start(aegisub)
    start_aegisub_routine()

    app.start('mspaint.exe')
    start_paint_routine()

def automate_process(fontname, params):

    shot_folder = os.path.abspath(os.path.dirname(params.path))
    shot_folder = os.path.join(shot_folder, 'fontshots')

    if not os.path.isdir(shot_folder):
      os.mkdir(shot_folder)

    SendKeys('%{TAB}')
    SendKeys('+{TAB}' * 2)
    take_fontshot(fontname)
    SendKeys('%{TAB}')
    save_fontshot(fontname, shot_folder)

if __name__ == '__main__':

  params = process_params()

  if not params.path:
    exit('Insufficient arguments. You MUST provide target folder / font path.')
  
  if os.path.exists(params.path):

    has_initialized = False
    if os.path.isfile(params.path):
      font_name = get_font_name(params.path)

      if font_name:
        initializeDesktopApps(params.aegisub)
        has_initialized = True
        automate_process(font_name, params)
      else:
        print('Font name could not be detected. ' \
          'Skipping file: %s' % (
            os.path.basename(params.path)))

    else:
      files = [os.path.join(params.path, x) for x
        in os.listdir(params.path) if x.endswith(
          ('.ttf', '.TTF', '.otf', '.OTF'))]
      
      if files:
        initializeDesktopApps(params.aegisub)
        has_initialized = True

      for font_filename in files:
        font_name = get_font_name(font_filename)

        if font_name:
          automate_process(font_name, params)
        else:
          print('Font name could not be detected. ' \
            'Skipping file: %s' % (
              os.path.basename(font_filename)))

    if has_initialized:
      SendKeys('%{F4}' * 4)
