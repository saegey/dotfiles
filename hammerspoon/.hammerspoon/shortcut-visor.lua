local M = {}

function M.layout(content, style, screenFrame)
  local padding = style.padding
  local maxWidth = math.min(1240, screenFrame.w - 48)
  local maxHeight = screenFrame.h - 48
  local fontSize = style.textSize
  local size
  repeat
    size = hs.drawing.getTextDrawingSize(content, {font = style.textFont, size = fontSize})
    if size.w + padding * 2 <= maxWidth and size.h + padding * 2 <= maxHeight then break end
    fontSize = fontSize - 0.5
  until fontSize <= 1
  local width = math.ceil(size.w + padding * 2)
  local height = math.ceil(size.h + padding * 2)
  return {
    x = screenFrame.x + (screenFrame.w - width) / 2,
    y = screenFrame.y + (screenFrame.h - height) / 2,
    w = width, h = height,
  }, fontSize
end

function M.show(content, style, screen)
  local frame, fontSize = M.layout(content, style, screen:frame())
  return hs.canvas.new(frame):appendElements(
    {
      type = 'rectangle', action = 'strokeAndFill',
      fillColor = style.fillColor, strokeColor = style.strokeColor,
      strokeWidth = style.strokeWidth,
      roundedRectRadii = {xRadius = style.radius, yRadius = style.radius},
    },
    {
      type = 'text', text = content, textFont = style.textFont,
      textSize = fontSize, textColor = style.textColor,
      frame = {x = style.padding, y = style.padding,
               w = frame.w - style.padding * 2, h = frame.h - style.padding * 2},
    }
  ):level(hs.canvas.windowLevels.overlay):show()
end

return M
