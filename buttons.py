from typing import List, Tuple, Callable, Any, Text

from pygame.color import Color
from pygame.math import Vector2

from ui import Component
from ui import Text, Style

COLOR_WHITE = Color(255, 255, 255, 0)


class Button(Component):
  def __init__(self, size: Tuple[int, int], screen, text: Text, **kwargs):
    super().__init__(size, screen, **kwargs)
    self.callback = kwargs.get('callback')
    self.text = text
    self.style_on_click = kwargs.get('style_onclick')
    self._cooldown = 0

  def update(self, elapsed_time: int):
    if self._cooldown > 0:
      self._cooldown = max(self._cooldown - elapsed_time, 0)
      if self._cooldown == 0:
        self.active_style = self.style_hovered if self.is_hovered else self.style

  def set_callback(self, callback: Callable[[], Any]):
    self.callback = callback

  def set_pos(self, pos: Vector2):
    super().set_pos(pos)
    text_pos = Vector2(self.rect.centerx - self.text.size[0] / 2,
                       self.rect.centery - self.text.size[1] / 2)
    self.text.set_pos(text_pos)

  def _render(self):
    self.text.render()

  def _on_click(self, mouse_pos: Tuple[int, int]):
    if self.callback:
      self.callback()
    self.active_style = self.style_on_click
    self._cooldown = 150


class ColorToggler(Button):
  def __init__(self, size: Tuple[int, int], screen, text: Text, colors: List[Color], **kwargs):
    super().__init__(size, screen, text, **kwargs)
    self.colors = colors
    self.index = 0
    self.background = self.colors[self.index]

  def _on_click(self, mouse_pos: Tuple[int, int]):
    self.index = (self.index + 1) % len(self.colors)
    self.background = self.colors[self.index]


def button(font, screen, size, callback, text: str):
  return Button(size=size, screen=screen, callback=callback,
                text=Text(screen, font, COLOR_WHITE, text),
                style=Style(background=Color(50, 50, 100, 0), border_color=Color(150, 150, 150, 0)),
                style_hovered=Style(background=Color(80, 80, 120), border_color=Color(180, 180, 180, 0)),
                style_onclick=Style(background=Color(80, 80, 120), border_color=Color(200, 255, 200, 0),
                                    border_width=2))
