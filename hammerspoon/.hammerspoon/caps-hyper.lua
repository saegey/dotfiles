-- Driver-free Caps Lock: hidutil supplies real down/up events as F18.
local M = {}
local capsUsage = 0x700000039
local f18Usage = 0x70000006d

-- Newer macOS versions print one plist per HID service, prefixed by a table
-- header and registry ID. Only apply a global update when unrelated maps agree;
-- a newly connected service may not have our own Caps Lock mapping yet.
function M.parseMappings(output)
  local values = {}
  if output:match('^%s*RegistryID%s+Key%s+Value') then
    local current
    for line in output:gmatch('[^\r\n]+') do
      local value = line:match('^%s*%x+%s+UserKeyMapping%s+(.+)$')
      if value then
        current = #values + 1
        values[current] = value
      elseif current then
        values[current] = values[current] .. '\n' .. line
      end
    end
    if #values == 0 then return nil, 'hidutil returned no HID services' end
  else
    values[1] = output
  end
  local mappings, hasCapsHyper
  for _, value in ipairs(values) do
    if not value:match('^%s*%(') and not value:match('^%s*<') then
      return nil, 'Could not parse hidutil key mappings'
    end
    local parsed = value:match('^%s*%(null%)%s*$') and {} or hs.plist.readString(value)
    if type(parsed) ~= 'table' then return nil, 'Could not parse hidutil key mappings' end
    local unrelated = {}
    for _, mapping in ipairs(parsed) do
      if type(mapping) ~= 'table' or not tonumber(mapping.HIDKeyboardModifierMappingSrc)
        or not tonumber(mapping.HIDKeyboardModifierMappingDst) then
        return nil, 'Invalid hidutil key mapping'
      end
      if tonumber(mapping.HIDKeyboardModifierMappingSrc) == capsUsage
        and tonumber(mapping.HIDKeyboardModifierMappingDst) == f18Usage then
        hasCapsHyper = true
      else
        table.insert(unrelated, mapping)
      end
    end
    parsed = unrelated
    if mappings then
      if #mappings ~= #parsed then return nil, 'HID services have different key mappings' end
      for i, mapping in ipairs(mappings) do
        if tonumber(mapping.HIDKeyboardModifierMappingSrc) ~= tonumber(parsed[i].HIDKeyboardModifierMappingSrc)
          or tonumber(mapping.HIDKeyboardModifierMappingDst) ~= tonumber(parsed[i].HIDKeyboardModifierMappingDst) then
          return nil, 'HID services have different key mappings'
        end
      end
    end
    mappings = parsed
  end
  if hasCapsHyper then
    table.insert(mappings, {HIDKeyboardModifierMappingSrc = capsUsage, HIDKeyboardModifierMappingDst = f18Usage})
  end
  return mappings
end

local function remap(enabled)
  local output, ok = hs.execute('/usr/bin/hidutil property --get UserKeyMapping', false)
  if not ok then return false, 'Could not read hidutil key mappings' end
  local mappings, reason = M.parseMappings(output)
  if not mappings then return false, reason end
  local updated = {}
  for _, mapping in ipairs(mappings) do
    local src = tonumber(mapping.HIDKeyboardModifierMappingSrc)
    local dst = tonumber(mapping.HIDKeyboardModifierMappingDst)
    if not src or not dst then return false end
    if src == capsUsage then
      -- Never replace someone else's Caps Lock remap.
      if dst ~= f18Usage then return false, 'Caps Lock already has a different key mapping' end
    else
      table.insert(updated, {HIDKeyboardModifierMappingSrc = src, HIDKeyboardModifierMappingDst = dst})
    end
  end
  if enabled then
    table.insert(updated, {HIDKeyboardModifierMappingSrc = capsUsage, HIDKeyboardModifierMappingDst = f18Usage})
  end
  local json = #updated == 0 and '{"UserKeyMapping":[]}' or hs.json.encode({UserKeyMapping = updated})
  local _, success = hs.execute("/usr/bin/hidutil property --set '" .. json .. "'", false)
  return success, success and nil or 'Could not write hidutil key mappings'
end

function M.new()
  local self = {held = false, used = false, keys = {}}
  local types = hs.eventtap.event.types
  local f18 = hs.keycodes.map.f18
  local mouseTypes = {
    [types.leftMouseDown] = true, [types.rightMouseDown] = true,
    [types.otherMouseDown] = true, [types.scrollWheel] = true,
  }
  function self.handle(event)
    local kind = event:getType()
    local code = event:getKeyCode()
    if (kind == types.keyDown or kind == types.keyUp) and code == f18 then
      if kind == types.keyDown and not self.held then
        self.held, self.used, self.started = true, false, hs.timer.absoluteTime()
      elseif kind == types.keyUp and self.held then
        local tapped = not self.used and hs.timer.absoluteTime() - self.started < 250000000
        self.held = false
        if tapped then
          return true, {hs.eventtap.event.newKeyEvent({}, 'escape', true),
                        hs.eventtap.event.newKeyEvent({}, 'escape', false)}
        end
      end
      return true
    end
    if mouseTypes[kind] and self.held then self.used = true end
    if kind == types.keyDown or kind == types.keyUp then
      -- Remember keys until key-up even if Caps Lock was released first.
      if self.held or self.keys[code] then
        self.used = true
        self.keys[code] = kind == types.keyDown or nil
        local flags = event:getFlags()
        flags.capslock = nil
        flags.ctrl, flags.alt, flags.shift, flags.cmd = true, true, true, true
        event:setFlags(flags)
      end
    end
    return false
  end
  self.tap = hs.eventtap.new({types.keyDown, types.keyUp, types.leftMouseDown,
                             types.rightMouseDown, types.otherMouseDown, types.scrollWheel}, self.handle)
  function self:start()
    if not hs.accessibilityState() then return false, 'Enable Hammerspoon in System Settings → Privacy & Security → Accessibility, then quit and reopen Hammerspoon' end
    self.tap:start()
    if not self.tap:isEnabled() then
      return false, 'Keyboard listener could not start; check Accessibility access and restart Hammerspoon'
    end
    local ok, reason = remap(true)
    if not ok then
      self.tap:stop()
      return false, reason
    end
    hs.hid.capslock.set(false)
    -- Reapply after sleep or keyboard connection without discarding other remaps.
    self.watcher = hs.caffeinate.watcher.new(function(event)
      if event == hs.caffeinate.watcher.systemDidWake then remap(true) end
    end):start()
    self.keyboardWatcher = hs.usb.watcher.new(function(event)
      if event.eventType == 'added' then remap(true) end
    end):start()
    return true
  end
  function self:stop()
    remap(false)
    self.tap:stop()
    if self.watcher then self.watcher:stop() end
    if self.keyboardWatcher then self.keyboardWatcher:stop() end
  end
  return self
end

return M
