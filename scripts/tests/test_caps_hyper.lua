-- Run in Hammerspoon: hs -c 'dofile(".../scripts/tests/test_caps_hyper.lua")'
local new = dofile(os.getenv('HOME') .. '/.dotfiles/hammerspoon/.hammerspoon/caps-hyper.lua').new
local function key(name, down)
  return hs.eventtap.event.newKeyEvent({}, name, down)
end
local function hasHyper(event)
  local flags = event:getFlags()
  return flags.ctrl and flags.alt and flags.shift and flags.cmd
end

local handler = new()
assert(handler.handle(key('f18', true)))
local suppressed, events = handler.handle(key('f18', false))
assert(suppressed and #events == 2)
assert(events[1]:getKeyCode() == hs.keycodes.map.escape)
assert(events[1]:getType() == hs.eventtap.event.types.keyDown)
assert(events[2]:getType() == hs.eventtap.event.types.keyUp)

handler.handle(key('f18', true))
local down = key('t', true)
assert(not handler.handle(down) and hasHyper(down))
local _, escape = handler.handle(key('f18', false))
assert(not escape, 'Chord must not send Escape')
local up = key('t', false)
handler.handle(up)
assert(hasHyper(up), 'Key-up must match the Hyper key-down after Caps release')
local ordinary = key('a', true)
handler.handle(ordinary)
assert(not hasHyper(ordinary), 'Hyper must not leak into ordinary typing')

handler.handle(key('f18', true))
handler.started = handler.started - 300000000
local _, heldEscape = handler.handle(key('f18', false))
assert(not heldEscape, 'Long hold must not send Escape')

handler.handle(key('f18', true))
handler.handle(hs.eventtap.event.newMouseEvent(hs.eventtap.event.types.leftMouseDown, {x = 0, y = 0}))
local _, clickEscape = handler.handle(key('f18', false))
assert(not clickEscape, 'Click while held must cancel Escape')
print('Caps Hyper: tap, chord, release order, ordinary typing, long hold, and click checks passed')
