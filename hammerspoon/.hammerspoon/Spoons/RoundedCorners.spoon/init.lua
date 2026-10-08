--- === RoundedCorners ===
--- Give your screens rounded corners.
--- Upstream: https://github.com/Hammerspoon/Spoons
--- MIT-licensed Spoon by Chris Jones.

local obj = {}
obj.__index = obj

obj.name = "RoundedCorners"
obj.version = "1.0"
obj.author = "Chris Jones"
obj.homepage = "https://github.com/Hammerspoon/Spoons"
obj.license = "MIT"

obj.corners = {}
obj.screenWatcher = nil
obj.allScreens = true
obj.radius = 18
obj.level = hs.canvas.windowLevels["screenSaver"] + 1

function obj:init()
  self.screenWatcher = hs.screen.watcher.new(function()
    self:screensChanged()
  end)
end

function obj:start()
  self.screenWatcher:start()
  self:render()
  return self
end

function obj:stop()
  self.screenWatcher:stop()
  self:deleteAllCorners()
  return self
end

function obj:deleteAllCorners()
  hs.fnutils.each(self.corners, function(corner)
    corner:delete()
  end)
  self.corners = {}
end

function obj:screensChanged()
  self:deleteAllCorners()
  self:render()
end

function obj:getScreens()
  if self.allScreens then
    return hs.screen.allScreens()
  end
  return { hs.screen.primaryScreen() }
end

function obj:render()
  local radius = self.radius

  hs.fnutils.each(self:getScreens(), function(screen)
    local frame = screen:fullFrame()
    local corners = {
      { x = frame.x, y = frame.y, center = { x = radius, y = radius } },
      { x = frame.x + frame.w - radius, y = frame.y, center = { x = 0, y = radius } },
      { x = frame.x, y = frame.y + frame.h - radius, center = { x = radius, y = 0 } },
      { x = frame.x + frame.w - radius, y = frame.y + frame.h - radius, center = { x = 0, y = 0 } },
    }

    hs.fnutils.each(corners, function(corner)
      local canvas = hs.canvas.new({ x = corner.x, y = corner.y, w = radius, h = radius })
      canvas:appendElements(
        { action = "build", type = "rectangle" },
        { action = "clip", type = "circle", center = corner.center, radius = radius, reversePath = true },
        {
          action = "fill",
          type = "rectangle",
          frame = { x = 0, y = 0, w = radius, h = radius },
          fillColor = { alpha = 1 },
        },
        { type = "resetClip" }
      )
      canvas:behavior(hs.canvas.windowBehaviors.canJoinAllSpaces)
      canvas:level(self.level)
      canvas:show()
      self.corners[#self.corners + 1] = canvas
    end)
  end)
end

return obj
