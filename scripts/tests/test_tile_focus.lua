local focus = dofile(os.getenv('HOME') .. '/.dotfiles/hammerspoon/.hammerspoon/tile-focus.lua')
local origin = {x = 100, y = 100, w = 100, h = 100}
local candidates = {
  {id = 'left', frame = {x = -20, y = 100, w = 100, h = 100}},
  {id = 'right', frame = {x = 220, y = 100, w = 100, h = 100}},
  {id = 'up', frame = {x = 100, y = -20, w = 100, h = 100}},
  {id = 'down', frame = {x = 100, y = 220, w = 100, h = 100}},
  {id = 'diagonal', frame = {x = 210, y = 210, w = 100, h = 100}},
}
for _, direction in ipairs({'left', 'right', 'up', 'down'}) do
  assert(focus.neighbor(origin, candidates, direction).id == direction)
end
assert(focus.neighbor(origin, {}, 'right') == nil)
assert(focus.neighbor(origin, {candidates[1]}, 'right') == nil)
assert(focus.neighbor(origin, {{frame = origin}}, 'right') == nil)
print('Tile focus: four directions, nearest aligned tile, and missing neighbors passed')
