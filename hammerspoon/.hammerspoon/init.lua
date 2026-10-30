-- Center a lone tiled window, then return it to normal tiling when another
-- opens. Leave Ghostty to AeroSpace because Hammerspoon frame changes can
-- make its separate windows overlap.
local aerospace = '/opt/homebrew/bin/aerospace'
local settingsKey = 'aerospaceCenteredWindowIds'
local centered = hs.settings.get(settingsKey) or {}
require('hs.ipc')

hs.window.animationDuration = 0
hs.autoLaunch(true)

hs.loadSpoon('RoundedCorners')
spoon.RoundedCorners.allScreens = true
spoon.RoundedCorners.radius = 18
spoon.RoundedCorners:start()

local hyper = {'ctrl', 'alt', 'shift', 'cmd'}
tileFocus = require('tile-focus').new('/opt/homebrew/bin/dinky')
local tileFocusBindings = {
  {key = 'left', vim = 'h', direction = 'left'},
  {key = 'down', vim = 'j', direction = 'down'},
  {key = 'up', vim = 'k', direction = 'up'},
  {key = 'right', vim = 'l', direction = 'right'},
}
for _, binding in ipairs(tileFocusBindings) do
  local direction = binding.direction
  local function focusTile()
    if hs.application.get('com.brnbw.dinky') then
      tileFocus:focus(direction)
    else
      hs.execute(aerospace .. ' focus ' .. direction, false)
    end
  end
  hs.hotkey.bind(hyper, binding.key, focusTile)
  hs.hotkey.bind({'alt'}, binding.vim, focusTile)
end
-- Karabiner's driver is blocked by system policy; use the driver-free fallback.
capsHyper = require('caps-hyper').new()
local hyperStarted, hyperError = capsHyper:start()
if not hyperStarted then
  hs.printf('Caps Lock Hyper: %s', hyperError)
  hs.alert.show('Caps Lock Hyper: ' .. hyperError)
end
hs.shutdownCallback = function() capsHyper:stop() end

local appShortcuts = {
  {key = 't', name = 'Ghostty', bundleID = 'com.mitchellh.ghostty'},
  {key = 'b', name = 'Chrome', bundleID = 'com.google.Chrome'},
  {key = 'l', name = 'Linear', bundleID = 'com.linear'},
  {key = 's', name = 'Slack', bundleID = 'com.tinyspeck.slackmacgap'},
  {key = 'p', name = '1Password', bundleID = 'com.1password.1password'},
  {key = 'k', name = 'Secretive', bundleID = 'com.maxgoedjen.Secretive.Host'},
}

for _, app in ipairs(appShortcuts) do
  local bundleID, name = app.bundleID, app.name
  hs.hotkey.bind(hyper, app.key, function()
    if not hs.application.launchOrFocusByBundleID(bundleID) then
      hs.alert.show('Could not open ' .. name)
    end
  end)
end

-- Match Herdr's sidebar shortcut in Chrome and Linear.
local sidebarShortcuts = {
  ['com.google.Chrome'] = {modifiers = {'cmd', 'shift'}, key = 'l'},
  ['com.linear'] = {modifiers = {}, key = '['},
}
local appSidebarHotkey = hs.hotkey.new({'cmd'}, '[', function()
  local app = hs.application.frontmostApplication()
  local shortcut = app and sidebarShortcuts[app:bundleID()]
  if shortcut then
    hs.eventtap.keyStroke(shortcut.modifiers, shortcut.key, 0, app)
  end
end)
local function updateAppSidebarHotkey()
  local app = hs.application.frontmostApplication()
  if app and sidebarShortcuts[app:bundleID()] then
    appSidebarHotkey:enable()
  else
    appSidebarHotkey:disable()
  end
end
appSidebarWatcher = hs.application.watcher.new(function(_, event)
  if event == hs.application.watcher.activated then
    updateAppSidebarHotkey()
  end
end):start()
updateAppSidebarHotkey()

-- Generate the help text from the bindings so it stays in sync.
local appShortcutLines = {'Apps · Hyper = hold Caps Lock (⌃⌥⇧⌘)'}
for _, app in ipairs(appShortcuts) do
  table.insert(appShortcutLines, string.format('Hyper %s  %s', app.key:upper(), app.name))
end
table.insert(appShortcutLines, '\nSidebars\n⌘ [                 Chrome tabs / Linear sidebar')

local aerospaceShortcuts = [[
AEROSPACE SHORTCUTS

Focus windows
Hyper ← / ↓ / ↑ / → left / down / up / right
⌥ H / J / K / L     left / down / up / right

Move windows
⌥ ⇧ H / J / K / L   move left / down / up / right

Arrange windows
⌥ /                 cycle tile orientation
⌥ ,                 cycle accordion orientation
⌥ V                 stack focused window with the one to its right
⌥ ⇧ Space           toggle floating / tiling
⌥ ⇧ B               balance window sizes

Window controls
⌥ F                 AeroSpace fullscreen (keeps outer gaps)
⌘ ⌥ F               fullscreen
⌥ - / =             resize smaller / larger

Workspaces
⌥ 1–9               switch workspace
⌥ ⇧ 1–9             move window to workspace
⌥ Tab               previous workspace]]

local herdrShortcuts = [[
HERDR · inside Ghostty
⌘ D                 split right
⌘ ⇧ D               split down
⌘ T                 new tab
⌘ 1–9               switch tab
⌘ [                 toggle sidebar
⌘ P                 repo tasks
⌘ I                 worktree visor
⌘ ⇧ R               Review PR dashboard
⌘ ⇧ M / ⌘ ⌥ M       open / hide lounge player
⌘ K                 search tabs / agents / branches
⌃ ⌥ 1–9             switch Herdr workspace
⌃ ⌥ J / K           next / previous agent
⌘ ⌥ ←/↓/↑/→         focus pane left/down/up/right
⌃ B then Z           zoom focused pane
⌃ B then R           resize mode
⌃ B then ?           full Herdr shortcut help

Dedicated spaces · external preferred
1  Ghostty
2  Linear + Chrome
3  Slack
4  1Password + Secretive
⌘ ⌥ F  fill area / return to tiling]]

local function shortcutColumns(left, right)
  local function lines(value)
    local result = {}
    for line in (value .. '\n'):gmatch('(.-)\n') do table.insert(result, line) end
    return result
  end
  local a, b, width = lines(left), lines(right), 0
  for _, line in ipairs(a) do width = math.max(width, utf8.len(line) or #line) end
  local result = {}
  for i = 1, math.max(#a, #b) do
    local line = a[i] or ''
    table.insert(result, line .. string.rep(' ', width - (utf8.len(line) or #line) + 5) .. (b[i] or ''))
  end
  return table.concat(result, '\n') .. '\n\nEscape or ⌘ ⌥ / to dismiss · Caps Lock tap = Escape'
end

local shortcutVisor = require('shortcut-visor')
local shortcutsCanvas
local shortcutsEscapeHotkey
local shortcutsStyle = {
  fillColor = { red = 30 / 255, green = 30 / 255, blue = 46 / 255, alpha = 0.98 }, -- Catppuccin Mocha Base
  strokeColor = { red = 203 / 255, green = 166 / 255, blue = 247 / 255, alpha = 1 }, -- Mauve
  strokeWidth = 2,
  textColor = { red = 205 / 255, green = 214 / 255, blue = 244 / 255, alpha = 1 }, -- Text
  textFont = 'JetBrains Mono',
  textSize = 14,
  radius = 18,
  padding = 24,
  fadeInDuration = 0.12,
  fadeOutDuration = 0.12,
}

local function dismissShortcuts()
  if shortcutsCanvas then
    shortcutsCanvas:delete()
    shortcutsCanvas = nil
  end
  if shortcutsEscapeHotkey then
    shortcutsEscapeHotkey:delete()
    shortcutsEscapeHotkey = nil
  end
end

function showKeyboardShortcuts()
    if shortcutsCanvas then return shortcutsCanvas end
    local shortcuts = aerospaceShortcuts
    if hs.application.get('com.brnbw.dinky') then
      shortcuts = shortcuts:gsub('AEROSPACE SHORTCUTS', 'DINKY SHORTCUTS')
        :gsub('1–9', '1–5')
        :gsub('AeroSpace fullscreen %(keeps outer gaps%)', 'Dinky fullscreen')
        :gsub('Arrange windows\n', 'Arrange windows\n⌥ S                 cycle tiles / accordion / scrolling\n')
        :gsub('⌥ Tab               previous workspace',
          '⌥ Tab               previous workspace\n⌥ ⇧ N               move window to next display and follow')
    end
    shortcuts = shortcutColumns(shortcuts, table.concat(appShortcutLines, '\n') .. '\n\n' .. herdrShortcuts)
    shortcutsCanvas = shortcutVisor.show(shortcuts, shortcutsStyle, hs.screen.mainScreen())
    shortcutsEscapeHotkey = hs.hotkey.bind({}, 'escape', dismissShortcuts)
    return shortcutsCanvas
end

hs.hotkey.bind({'cmd', 'alt'}, '/', function()
  if shortcutsCanvas then
    dismissShortcuts()
  else
    showKeyboardShortcuts()
  end
end)

-- An open reference must fit the new display after docking, undocking or scaling.
shortcutsScreenWatcher = hs.screen.watcher.new(function()
  if shortcutsCanvas then
    dismissShortcuts()
    showKeyboardShortcuts()
  end
end):start()

local function run(command)
  local output, ok = hs.execute(aerospace .. ' ' .. command, false)
  if ok then return output end
  return nil
end

local function visibleWorkspaces()
  local output = run('list-workspaces --all --format %{workspace},%{workspace-is-visible}')
  if not output then return nil end

  local visible = {}
  for line in output:gmatch('[^\r\n]+') do
    local workspace, isVisible = line:match('^([^,]+),([^,]+)$')
    if workspace and isVisible == 'true' then visible[workspace] = true end
  end
  return visible
end

local function windowsByWorkspace()
  local output = run('list-windows --all --format %{window-id},%{workspace},%{window-layout},%{window-is-fullscreen}')
  if not output then return nil end

  local groups, liveIds = {}, {}
  for line in output:gmatch('[^\r\n]+') do
    local id, workspace, layout, fullscreen = line:match('^(%d+),([^,]+),([^,]+),([^,]+)$')
    if id then
      liveIds[id] = true
      groups[workspace] = groups[workspace] or {}
      table.insert(groups[workspace], {
        id = id,
        layout = layout,
        fullscreen = fullscreen == 'true',
      })
    end
  end
  return groups, liveIds
end

local function centerWindow(id)
  local window = hs.window.get(tonumber(id))
  if not window or not window:isVisible() then return end
  local screen = window:screen()
  if not screen then return end

  local frame = screen:frame()
  local side = math.min(frame.w - 20, frame.h - 20)
  local target = {
    x = frame.x + (frame.w - side) / 2,
    y = frame.y + (frame.h - side) / 2,
    w = side,
    h = side,
  }
  local current = window:frame()
  if math.abs(current.x - target.x) > 4 or math.abs(current.y - target.y) > 4
    or math.abs(current.w - target.w) > 4 or math.abs(current.h - target.h) > 4 then
    window:setFrame(target, 0)
  end
end

local function isGhostty(id)
  local window = hs.window.get(tonumber(id))
  local app = window and window:application()
  return app and app:bundleID() == 'com.mitchellh.ghostty'
end

local function updateLayout()
  -- Dinky owns window frames during its trial; keep only the screen decorations.
  if hs.application.get('com.brnbw.dinky') then return end
  if not hs.accessibilityState() then return end
  local visible = visibleWorkspaces()
  local groups, liveIds = windowsByWorkspace()
  if not visible or not groups then return end

  for id in pairs(centered) do
    if not liveIds[id] then centered[id] = nil end
  end

  for workspace, windows in pairs(groups) do
    if #windows == 1 and visible[workspace] then
      local only = windows[1]
      if not only.fullscreen then
        if isGhostty(only.id) then
          if centered[only.id] then
            run('layout tiling --window-id ' .. only.id)
            centered[only.id] = nil
          end
        elseif centered[only.id] then
          centerWindow(only.id)
        elseif only.layout ~= 'floating' and hs.window.get(tonumber(only.id)) then
          if run('layout floating --window-id ' .. only.id) then
            centered[only.id] = true
            hs.timer.doAfter(0.2, function() centerWindow(only.id) end)
          end
        end
      end
    elseif #windows > 1 then
      for _, window in ipairs(windows) do
        if centered[window.id] then
          run('layout tiling --window-id ' .. window.id)
          centered[window.id] = nil
        end
      end
    end
  end

  hs.settings.set(settingsKey, centered)
end

if not hs.accessibilityState() then hs.accessibilityState(true) end
hs.timer.doEvery(1.5, updateLayout)
hs.timer.doAfter(1.5, updateLayout)
