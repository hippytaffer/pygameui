#!/usr/bin/env python3
import os
from typing import Tuple, Callable, Any, Optional

import pygame
from pygame.color import Color
from pygame.font import Font
from pygame.math import Vector2
from pygame.time import Clock

from button import HoldDownBehavior, Button, SingleClickBehavior
from containers import GridContainer, EvenSpacingContainer, AbsolutePosContainer
from images import Surface
from text import StaticText, TextArea
from ui import Style, Component

MATRIX_GREEN = Color(32, 194, 14)
WHITE = Color(255, 255, 255)
KEYBOARD_BACKGROUND_COLOR = Color(100, 100, 100)
COLOR_FILE = Color(50, 50, 50)
COLOR_DIR = Color(50, 50, 150)

SCREEN_RESOLUTION = (800, 600)
BUTTON_SIZE = (256, 24)
PADDING = 32


class FileBrowser:

  def __init__(self):
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_RESOLUTION)
    pygame.display.set_caption("File browser")
    clock = Clock()

    font = Font('resources/consola.ttf', 14)
    font_small = Font('resources/consola.ttf', 12)
    background_color = (0, 0, 0)

    grid_dimensions = (3, 10)
    self.buttons = [blank_button(font) for _ in range(grid_dimensions[0] * grid_dimensions[1])]

    grid = GridContainer(children=self.buttons, dimensions=grid_dimensions, padding=5, margin=1,
                         style=Style(background_color=KEYBOARD_BACKGROUND_COLOR, border_color=WHITE))
    width = SCREEN_RESOLUTION[0] - PADDING * 2
    grid_container = EvenSpacingContainer(width, "fit_contents", [grid], padding=0)

    dir_path = os.path.dirname(os.path.realpath(__file__))
    self.text_current_dir = StaticText(font, WHITE, dir_path,
                                       style=Style(background_color=Color(50, 50, 50)))
    self.file_names = os.listdir(".")
    self.preview = FilePreview((width, 230), font_small)

    container = AbsolutePosContainer(SCREEN_RESOLUTION,
                                     [(Vector2(PADDING, PADDING), self.text_current_dir),
                                      (Vector2(PADDING, 80), self.preview),
                                      (Vector2(PADDING, 330), grid_container)])
    container.set_pos(Vector2(0, 0))

    self.setup_keys()

    while True:
      for event in pygame.event.get():
        handle_exit(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
          container.handle_mouse_was_clicked(pygame.mouse.get_pos())
        elif event.type == pygame.MOUSEBUTTONUP:
          container.handle_mouse_was_released()
        elif event.type == pygame.MOUSEMOTION:
          container.handle_mouse_motion(pygame.mouse.get_pos())
        elif event.type == pygame.KEYDOWN:
          container.handle_key_was_pressed(event.key)
        elif event.type == pygame.KEYUP:
          container.handle_key_was_released(event.key)
      elapsed_time = clock.tick()

      container.update(elapsed_time)

      screen.fill(background_color)
      container.render(screen)
      pygame.display.flip()

  def change_dir(self, directory: str):
    os.chdir(directory)
    self.file_names = os.listdir(".")
    self.text_current_dir.set_text(os.getcwd())
    self.setup_keys()

  def create_file_callback(self, filename: str):
    def callback():
      if os.path.isdir(filename):
        self.change_dir(filename)
      else:
        try:
          with open(filename, "r") as f:
            text = f.read()
            self.preview.show_text(text)
        except UnicodeDecodeError:
          try:
            image = pygame.image.load(filename)
            self.preview.show_image(image)
          except pygame.error:
            self.preview.show_text("BINARY FILE - CONTENTS NOT SHOWN")

    return callback

  def setup_keys(self):
    self.buttons[0].set_label("..")
    self.buttons[0].set_callback(lambda: self.change_dir(".."))
    for i, btn in enumerate(self.buttons[1:]):
      if i < len(self.file_names):
        filename = self.file_names[i]
        btn.set_label(filename)
        btn.set_callback(self.create_file_callback(filename))
        btn.set_label_color(Color(150, 150, 255) if os.path.isdir(filename) else WHITE)
      else:
        btn.set_label("")
        btn.set_callback(lambda: None)


class FilePreview(Component):
  def __init__(self, size: Tuple[int, int], font):
    super().__init__(size)
    self._text_component = TextArea(font, WHITE, size, padding=16,
                                    style=Style(border_color=WHITE))
    self._image_component = Surface(None, style=Style(border_color=WHITE))

  def set_pos(self, pos: Vector2):
    super().set_pos(pos)
    self._text_component.set_pos(pos)
    self._image_component.set_pos(pos)

  def show_text(self, text: str):
    self._text_component.set_text(text)
    self._text_component.set_visible(True)
    self._image_component.set_visible(False)

  def show_image(self, image):
    image_rect = image.get_rect()
    scaled_rect = image_rect.fit(self._rect)
    scaled_image = pygame.transform.scale(image, scaled_rect.size)
    self._image_component.set_surface(scaled_image)
    self._text_component.set_visible(False)
    self._image_component.set_visible(True)

  def _render_contents(self, surface):
    self._text_component.render(surface)
    self._image_component.render(surface)


def handle_exit(event):
  if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
    pygame.quit()
    exit(0)


def button(font, size: Tuple[int, int], callback: Callable[[], Any], label: str, background_color: Color,
    hotkey: Optional[int] = None,
    hold: Optional[HoldDownBehavior] = None):
  return Button(size=size,
                callback=callback,
                label=StaticText(font, WHITE, label),
                behavior=hold if hold else SingleClickBehavior(),
                hotkey=hotkey,
                style=Style(background_color=background_color),
                style_hovered=Style(background_color=background_color, border_color=Color(210, 210, 210),
                                    border_width=1),
                style_onclick=Style(background_color=background_color, border_color=MATRIX_GREEN,
                                    border_width=3))


def dir_button(font):
  return button(font, BUTTON_SIZE, callback=lambda: None, label="", background_color=Color(255, 255, 0))


def blank_button(font):
  return button(font, BUTTON_SIZE, callback=lambda: None, label="", background_color=COLOR_FILE)


if __name__ == '__main__':
  FileBrowser()