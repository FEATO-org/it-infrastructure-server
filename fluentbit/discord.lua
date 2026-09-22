local CHAT_LIMIT = 1900
local ERROR_LIMIT = 1800
local DEATH_PREFIXES = {
  "was slain", "was shot", "was squashed", "was pummeled", "was pricked",
  "was impaled", "was fireballed", "was roasted", "was blown", "was struck",
  "was killed", "was doomed", "was hurt", "was drowned", "was suffocated",
  "was burned", "fell", "drowned", "starved", "withered", "blew up",
  "hit the ground", "went up in flames", "froze to death", "tried to swim",
  "experienced kinetic energy", "walked into",
}

local function json_string(value)
  value = value:gsub("\\", "\\\\")
  value = value:gsub('"', '\\"')
  value = value:gsub("\b", "\\b")
  value = value:gsub("\f", "\\f")
  value = value:gsub("\n", "\\n")
  value = value:gsub("\r", "\\r")
  value = value:gsub("\t", "\\t")
  value = value:gsub("[%z\1-\8\11\12\14-\31]", function(character)
    return string.format("\\u%04x", character:byte())
  end)
  return '"' .. value .. '"'
end

local function truncate(value, limit)
  if #value <= limit then return value end
  local end_index = limit - 3
  while end_index > 0 and value:byte(end_index) >= 128 and value:byte(end_index) < 192 do
    end_index = end_index - 1
  end
  return value:sub(1, end_index) .. "..."
end

local function parse_log(log)
  local time, thread, level, message = log:match("^%[(%d%d:%d%d:%d%d)%] %[([^/%]]+)/([A-Z]+)%]: (.*)$")
  if not level then return nil end
  return { time = time, thread = thread, level = level, message = message }
end

local function classify_event(entry)
  if entry.level == "ERROR" then return "ERROR", entry.message end
  if entry.level ~= "INFO" then return nil end
  local player, chat = entry.message:match("^<([^>]+)> (.*)$")
  if player then return "CHAT", { player = player, message = chat } end
  player = entry.message:match("^(.+) joined the game$")
  if player then return "PLAYER_JOIN", player end
  player = entry.message:match("^(.+) left the game$")
  if player then return "PLAYER_LEAVE", player end
  local death_player, death_detail = entry.message:match("^([%w_]+) (.+)$")
  if death_player then
    for _, prefix in ipairs(DEATH_PREFIXES) do
      local following = death_detail:sub(#prefix + 1, #prefix + 1)
      if death_detail:sub(1, #prefix) == prefix and (following == "" or following == " " or following == "(") then
        return "PLAYER_DEATH", entry.message
      end
    end
  end
  local version = entry.message:match("^Starting minecraft server version (.+)$")
  if version then return "SERVER_STARTING", version end
  local duration = entry.message:match('^Done %(([%d%.]+)s%)! For help, type "help"$')
  if duration then return "SERVER_STARTED", duration end
  if entry.message == "Stopping server" then return "SERVER_STOPPING" end
end

local function build_payload(event, value)
  local content
  local title
  local description
  local color
  if event == "CHAT" then
    content = "**" .. value.player .. "**: " .. truncate(value.message, CHAT_LIMIT - #value.player - 6)
  elseif event == "PLAYER_JOIN" then
    title, description, color = "🟢 プレイヤー参加", "**" .. value .. "** がサーバーに参加しました", 0x57F287
  elseif event == "PLAYER_LEAVE" then
    title, description, color = "⚫ プレイヤー退出", "**" .. value .. "** がサーバーから退出しました", 0x99AAB5
  elseif event == "PLAYER_DEATH" then
    title, description, color = "💀 プレイヤー死亡", value, 0x992D22
  elseif event == "SERVER_STARTING" then
    title, description, color = "🟡 サーバー起動中", "Minecraft **" .. value .. "** を起動しています", 0xFEE75C
  elseif event == "SERVER_STARTED" then
    title, description, color = "✅ サーバー起動完了", "Minecraftサーバーが起動しました\n起動時間: **" .. value .. " 秒**", 0x57F287
  elseif event == "SERVER_STOPPING" then
    title, description, color = "🟠 サーバー停止中", "Minecraftサーバーを停止しています", 0xE67E22
  elseif event == "ERROR" then
    title, description, color = "🚨 Minecraft ERROR", "```text\n" .. truncate(value, ERROR_LIMIT) .. "\n```", 0xED4245
  end
  local payload = '{"allowed_mentions":{"parse":[]}'
  if content then
    payload = payload .. ',"content":' .. json_string(content)
  else
    payload = payload .. ',"embeds":[{"title":' .. json_string(title) .. ',"description":' .. json_string(description) .. ',"color":' .. color .. "}]"
  end
  return payload .. "}"
end

function process_minecraft_log(tag, timestamp, record)
  local entry = parse_log(record.log or "")
  if not entry then return -1, timestamp, record end
  local event, value = classify_event(entry)
  if not event then return -1, timestamp, record end
  return 2, timestamp, {
    body = build_payload(event, value),
    headers = { ["Content-Type"] = "application/json" },
    route = event == "ERROR" and "error" or "notify",
  }
end
