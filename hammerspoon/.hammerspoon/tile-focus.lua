-- Focus only Dinky's tiled windows on the current workspace and display.
local M = {}

function M.neighbor(origin, candidates, direction)
  local horizontal = direction == 'left' or direction == 'right'
  local sign = (direction == 'left' or direction == 'up') and -1 or 1
  local ox, oy = origin.x + origin.w / 2, origin.y + origin.h / 2
  local best, bestScore
  for _, candidate in ipairs(candidates) do
    local f = candidate.frame
    local dx, dy = f.x + f.w / 2 - ox, f.y + f.h / 2 - oy
    local primary, perpendicular = horizontal and dx or dy, horizontal and dy or dx
    if primary * sign > 1 then
      local score = primary * primary + 4 * perpendicular * perpendicular
      if not bestScore or score < bestScore then
        best, bestScore = candidate, score
      end
    end
  end
  return best
end

function M.new(binary)
  local self = {}
  function self:focus(direction)
    if self.task then return end
    local origin = hs.window.focusedWindow()
    if not origin or not origin:screen() then return end
    local originID, screenID = origin:id(), origin:screen():id()
    self.task = hs.task.new(binary, function(code, stdout, stderr)
      self.task = nil
      if code ~= 0 then
        hs.alert.show('Dinky focus failed: ' .. (stderr or ''))
        return
      end
      local current = hs.window.focusedWindow()
      if not current or current:id() ~= originID then return end
      local candidates = {}
      for id, floating in stdout:gmatch('(%d+)|(%a+)') do
        local window = hs.window.get(tonumber(id))
        if floating == 'false' and window and window:id() ~= originID
            and window:isVisible() and not window:isMinimized()
            and window:screen() and window:screen():id() == screenID then
          table.insert(candidates, {window = window, frame = window:frame()})
        end
      end
      local nextWindow = M.neighbor(current:frame(), candidates, direction)
      if nextWindow then nextWindow.window:focus() end
    end, {'list-windows', '--workspace', 'focused', '--monitor', 'focused',
          '--format', '%{window-id}|%{window-is-floating}'})
    if not self.task or not self.task:start() then
      self.task = nil
      hs.alert.show('Could not run Dinky to focus a tile.')
    end
  end
  return self
end

return M
