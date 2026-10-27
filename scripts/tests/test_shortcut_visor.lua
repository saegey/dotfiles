local visor = dofile(os.getenv('HOME') .. '/.dotfiles/hammerspoon/.hammerspoon/shortcut-visor.lua')
local style = {padding = 24, textSize = 17, textFont = 'JetBrains Mono'}
-- Long two-column content must remain inside each usable display frame,
-- including laptop scaling and external displays with negative origins.
local content = string.rep(string.rep('W', 105) .. '\n', 36) .. 'Escape to dismiss'
for _, screen in ipairs({
  {x = 0, y = 32, w = 1512, h = 950},
  {x = 0, y = 32, w = 1280, h = 720},
  {x = 0, y = 38, w = 1024, h = 600},
  {x = -2560, y = -458, w = 2560, h = 1400},
}) do
  local frame, fontSize = visor.layout(content, style, screen)
  assert(frame.x >= screen.x + 24 and frame.y >= screen.y + 24)
  assert(frame.x + frame.w <= screen.x + screen.w - 24)
  assert(frame.y + frame.h <= screen.y + screen.h - 24)
  local textSize = hs.drawing.getTextDrawingSize(content, {font = style.textFont, size = fontSize})
  assert(textSize.w <= frame.w - style.padding * 2)
  assert(textSize.h <= frame.h - style.padding * 2)
end
print('Shortcut visor: content fits all four screen sizes and origins')
