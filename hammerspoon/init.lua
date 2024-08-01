local k = hs.hotkey.modal.new({}, "F17")
local grid = require "grid"
local window = require "hs.window"
local hotkey = require "hs.hotkey"
local spaces = require("hs._asm.undocumented.spaces")

-- local spacesModifier = "ctrl"

hs.hints.style = "vimperator"

hs.grid.MARGINX = 0
hs.grid.MARGINY = 0
hs.grid.GRIDHEIGHT = 13
hs.grid.GRIDWIDTH = 13

-- Disable window animations (janky for iTerm)
window.animationDuration = 0

-- Snap Window
k:bind({}, 'U', nil, grid.snap_northwest)
k:bind({}, 'I', nil, grid.snap_north)
k:bind({}, 'O', nil, grid.snap_northeast)

k:bind({}, 'H', nil, grid.snap_west_more)
k:bind({}, 'J', nil, grid.snap_west)
k:bind({}, 'K', nil, grid.maximize_window)
k:bind({}, 'L', nil, grid.snap_east)
k:bind({}, ';', nil, grid.snap_east_more)

k:bind({}, 'M', nil, grid.snap_southwest)
k:bind({}, ',', nil, grid.snap_south)
k:bind({}, '.', nil, grid.snap_southeast)

k:bind({}, 'LEFT', nil, hs.grid.pushWindowLeft)
k:bind({}, 'RIGHT', nil, hs.grid.pushWindowRight)
k:bind({}, 'UP', nil, hs.grid.pushWindowUp)
k:bind({}, 'DOWN', nil, hs.grid.pushWindowDown)

k:bind({}, 'pad+', nil, hs.grid.pushWindowNextScreen)
k:bind({}, 'pad-', nil, hs.grid.pushWindowPrevScreen)
k:bind({}, 'pad9', nil, grid.snap_northeast)
k:bind({}, 'pad7', nil, grid.snap_northwest)
k:bind({}, 'pad8', nil, grid.snap_north)
k:bind({}, 'pad4', nil, grid.snap_west)
k:bind({}, 'pad5', nil, grid.maximize_window)
k:bind({}, 'pad6', nil, grid.snap_east)
k:bind({}, 'pad1', nil, grid.snap_southwest)
k:bind({}, 'pad2', nil, grid.snap_south)
k:bind({}, 'pad3', nil, grid.snap_southeast)

-- -- lock computer
k:bind({}, "Escape", nil, function() hs.caffeinate.lockScreen() end)

k:bind({}, "]", nil, function()
    local win = hs.window.focusedWindow()
    if win then
        hs.eventtap.keyStroke({"ctrl"}, "right")
        hs.timer.doAfter(0.5, function() -- Adjust delay as needed
            win:focus()
        end)
    end
end)


local function open_help()
  help_str = "q - Chrome\nw - Sublime, e - iTerm, r - HipChat "
  hs.alert.show(help_str, 2)
end

-- application shortcuts
k:bind({}, '2', nil, function () hs.application.launchOrFocus("IntelliJ IDEA CE") end)
k:bind({}, 'q', nil, function () hs.application.launchOrFocus("Google Chrome") end)
k:bind({}, 'w', nil, function () hs.application.launchOrFocus("Visual Studio Code") end)
k:bind({}, 'e', nil, function () hs.application.launchOrFocus("iTerm") end)
k:bind({}, '1', nil, function () hs.application.launchOrFocus("Slack") end)
k:bind({}, '`', nil, function () hs.application.launchOrFocus("Slack") end)

-- local wifiSSID = hs.menubar.new()
-- local SSID = hs.wifi.currentNetwork()

-- function ssidChangedCallback()
--   newSSID = hs.wifi.currentNetwork()
--   if newSSID ~= SSID and newSSID ~= nil then
--     wifiSSID:setTitle(newSSID)
--     SSID = newSSID
--   end
-- end

-- wifiWatcher = hs.wifi.watcher.new(ssidChangedCallback)
-- wifiWatcher:start()

-- reload config on save
function reloadConfig(files)
    doReload = false
    for _,file in pairs(files) do
        if file:sub(-4) == ".lua" then
            doReload = true
        end
    end
    if doReload then
        hs.reload()
    end
end
hs.pathwatcher.new(os.getenv("HOME") .. "/.hammerspoon/", reloadConfig):start()
-- hs.notify.new({title="Hammerspoon", informativeText="Config Reloaded", ""}):send():release()

-- Spaces
-- local spacesCount = spaces.count()
-- local spacesModifiers = {"fn", spacesModifier}

-- -- infinitely cycle through spaces using ctrl+left/right to trigger ctrl+[1..n]
-- local spacesEventtap = hs.eventtap.new({hs.eventtap.event.types.keyDown}, function(o)
--   local keyCode = o:getKeyCode()
--   local modifiers = o:getFlags()

--   --logger.i(keyCode, hs.inspect(modifiers))

--   -- check if correct key code
--   if keyCode ~= 123 and keyCode ~= 124 then return end
--   if not modifiers[spacesModifier] then return end

--   -- check if no other modifiers where pressed
--   local passed = hs.fnutils.every(modifiers, function(_, modifier)
--     return hs.fnutils.contains(spacesModifiers, modifier)
--   end)

--   if not passed then return end

--   -- switch spaces
--   local currentSpace = spaces.currentSpace()
--   local nextSpace

--   -- left arrow
--   if keyCode == 123 then
--     nextSpace = currentSpace ~= 1 and currentSpace - 1 or spacesCount
--    -- right arrow
--   elseif keyCode == 124 then
--     nextSpace = currentSpace ~= spacesCount and currentSpace + 1 or 1
--   end

--   hs.eventtap.keyStroke({spacesModifier}, string.format("%d", nextSpace))

--   -- stop propagation
--   return true
-- end):start()

-- Enter Hyper Mode when F18 (Hyper/Capslock) is pressed
pressedF18 = function()
  k.triggered = false
  k:enter()
end

-- Leave Hyper Mode when F18 (Hyper/Capslock) is pressed,
--   send ESCAPE if no other keys are pressed.
releasedF18 = function()
  k:exit()
  if not k.triggered then
    hs.eventtap.keyStroke({}, 'ESCAPE')
  end
end

-- Bind the Hyper key
f18 = hs.hotkey.bind({}, 'F18', pressedF18, releasedF18)


