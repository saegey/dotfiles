-- AeroSpace fills a workspace with its only tiled window. Keep that window
-- square and centered, then return it to normal tiling when another opens.
local aerospace = '/opt/homebrew/bin/aerospace'
local settingsKey = 'aerospaceCenteredWindowIds'
local centered = hs.settings.get(settingsKey) or {}
require('hs.ipc')

hs.window.animationDuration = 0
hs.autoLaunch(true)

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

local function updateLayout()
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
        if centered[only.id] then
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
