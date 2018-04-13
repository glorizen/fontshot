import os
import sys
import time
import argparse

from fontTools import ttLib
from pywinauto.keyboard import SendKeys
from pywinauto.application import Application


def _SendKeys(keys, pause=0.05, wait=0):

  global params

  SendKeys(keys, pause)
  if wait or params.force_delay:
    time.sleep(wait + params.delay)

def process_params():
  parser = argparse.ArgumentParser()
  parser.add_argument('path', help='path to a font file or to a ' \
    'folder containing fonts.')
  
  parser.add_argument('--force-delay', action='store_true',
    help='forces delay (if given) after each key input.')
    
  parser.add_argument('-delay', type=float, default=0,
    help='adds delay (in seconds) to keyboard inputs. Values can be ' \
      'float too. (e.g. -delay 0.25)')

  parser.add_argument('-aegisub', default='C:\\Program Files (x86)\\' \
    'Aegisub\\aegisub32.exe', help='path to executable of Aegisub ' \
    'application. [default: C:\Program Files (x86)\Aegisub\aegisub32.exe]')
  
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
  _SendKeys(font_name, pause=0)
  _SendKeys('{TAB}' * 2)
  _SendKeys('%{PRTSC}')

def save_fontshot(image_name, folder_name):
  image_name = image_name.replace(' ', '{SPACE}')
  _SendKeys('^v')
  _SendKeys('%fa', wait=1)

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

  _SendKeys(full_image_path, pause=0.01, wait=0.2)
  _SendKeys('{ENTER}' * 2, wait=0.1)

def start_aegisub_routine(app):

  window = app.window(best_match='Untitled - Aegisub')
  window.wait('visible')
  _SendKeys('%ss', wait=0.5)
  _SendKeys('%e', wait=0.5)

  _SendKeys('{TAB}' * 5)
  _SendKeys('{TAB}' * 2)

def start_paint_routine(app):

  window = app.window(best_match='Untitled - Paint')
  window.wait('visible')
  
  _SendKeys('%hre{RIGHT}{TAB}200{ENTER}', wait=0.5)

def initializeDesktopApps(aegisub):

  app = Application(backend='uia')
  app.start(aegisub)
  start_aegisub_routine(app)

  app.start('mspaint.exe')
  start_paint_routine(app)

def automate_process(fontname, params):

  shot_folder = os.path.abspath(os.path.dirname(params.path))
  shot_folder = os.path.join(shot_folder, 'fontshots')

  if not os.path.isdir(shot_folder):
    os.mkdir(shot_folder)

  _SendKeys('%{TAB}', wait=0.5)
  _SendKeys('+{TAB}' * 2)
  take_fontshot(fontname)
  _SendKeys('%{TAB}', wait=0.5)
  save_fontshot(fontname, shot_folder)

if __name__ == '__main__':

  global params
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
      _SendKeys('%{F4}' * 4, pause=0.1)
