-- This example iterates through the field tree of the packets, and prints out the tree field information in a text window.
-- It shows the current tree for the selected packet, but this does not mean it always shows the full tree,
-- because wireshark performs multiple dissection passes of a packet, with the initial pass only being high-level and not
-- dissecting fully (for performance reasons).  You can see this behavior better by changing line 30 of this example
-- to this, so it concatenates output instead of clearing it every time: 
-- output = output .. "\nTree fields for packet #".. pinfo.number .. ":\n"

-- this only works in wireshark
if not gui_enabled() then return end

function string.starts(String,Start)
 return string.sub(String,1,string.len(Start)) == Start
end

function string.ends(String,End)
   return End == '' or string.sub(String,-string.len(End)) == End
end

local function getAllData(t, prevData)
  -- if prevData == nil, start empty, otherwise start with prevData
  local data = prevData or {}

  -- copy all the attributes from t
  for k,v in pairs(t) do
    data[k] = data[k] or v
  end

  -- get t's metatable, or exit if not existing
  local mt = getmetatable(t)
  if type(mt)~='table' then return data end

  -- get the __index from mt, or exit if not table
  local index = mt.__index
  if type(index)~='table' then return data end

  -- include the data from index into data, recursively, and return
  return getAllData(index, data)
end


local ascii = {["20"]=" ",  ["21"]="!", ["22"]="\"", ["23"]="#", ["24"]="$", ["25"]="%",
               ["26"]="&",  ["27"]="'", ["28"]="(",  ["29"]=")", ["2A"]="*", ["2B"]="+",
               ["2C"]=",",  ["2D"]="-", ["2E"]=".",  ["2F"]="/", ["30"]="0", ["31"]="1",
               ["32"]="2",  ["33"]="3", ["34"]="4",  ["35"]="5", ["36"]="6", ["37"]="7",
               ["38"]="8",  ["39"]="9", ["3A"]=":",  ["3B"]=";", ["3C"]="<", ["3D"]="=",
               ["3E"]=">",  ["3F"]="?", ["40"]="@",  ["41"]="A", ["42"]="B", ["43"]="C",
               ["44"]="D",  ["45"]="E", ["46"]="F",  ["47"]="G", ["48"]="H", ["49"]="I",
               ["4A"]="J",  ["4B"]="K", ["4C"]="L",  ["4D"]="M", ["4E"]="N", ["4F"]="O",
               ["50"]="P",  ["51"]="Q", ["52"]="R",  ["53"]="S", ["54"]="T", ["55"]="U",
               ["56"]="V",  ["57"]="W", ["58"]="X",  ["59"]="Y", ["5A"]="Z", ["5B"]="[",
               ["5C"]="\\", ["5D"]="]", ["5E"]="^",  ["5F"]="_", ["60"]="`", ["61"]="a",
               ["62"]="b",  ["63"]="c", ["64"]="d",  ["65"]="e", ["66"]="f", ["67"]="g",
               ["68"]="h",  ["69"]="i", ["6A"]="j",  ["6B"]="k", ["6C"]="l", ["6D"]="m",
               ["6E"]="n",  ["6F"]="o", ["70"]="p",  ["71"]="q", ["72"]="r", ["73"]="s",
               ["74"]="t",  ["75"]="u", ["76"]="v",  ["77"]="w", ["78"]="x", ["79"]="y",
               ["7A"]="z",  ["7B"]="{", ["7C"]="|",  ["7D"]="}"}

local function to_python_string(bytes)
  local out = ""
  for hex in string.gmatch(tostring(bytes), "[0-9A-F][0-9A-F]") do
    local chr = ascii[hex]
    if chr == nil then
      out = out .. "\\x" .. hex 
    else
      out = out .. chr
    end
  end
  return out
end


local function to_python_hex(bytes)
  local out = ""
  for hex in string.gmatch(tostring(bytes), "[0-9A-F][0-9A-F]") do
    out = out .. "\\x" .. hex
  end
  return out
end

local function create_listener_function(frame, directory)
  local function packet(pinfo, tvb, tabinfo)
    local header
    local fields = { all_field_infos() }
    local packet = {}
    local prev_name = "."
    local prev_end = -1
      
    for index, finfo in pairs(fields) do
      if header ~= nil then
        if finfo.len == 0 or finfo.hidden or finfo.generated or type(finfo.value) == "boolean" then
          goto for_end
        end
        if string.starts(finfo.name, prev_name .. ".") or finfo.offset < prev_end then
          table.remove(packet, #packet)
        end
        table.insert(packet, finfo)
        prev_name = finfo.name
        prev_end = finfo.offset + finfo.len
      elseif frame == finfo.name then
        header = finfo
      end
      ::for_end::
    end

    if header == nil then
      return
    end

    prev_end = header.offset
    source = header.source
    dizzy = {}
    i = 0
    for index, finfo in pairs(packet) do
      if prev_end ~= finfo.offset then
        table.insert(dizzy, {name="Unknown_" .. i,
          value=to_python_hex(source:bytes(prev_end, finfo.offset - prev_end))})
        i = i + 1
      end
      
      local val = source:bytes(finfo.offset, finfo.len)
      if finfo.type == ftypes.STRING or finfo.type == ftypes.STRINGZ then
        val = to_python_string(source:bytes(finfo.offset, finfo.len))
      else
        val = to_python_hex(source:bytes(finfo.offset, finfo.len))
      end
      table.insert(dizzy, {name=finfo.name .. "_" .. i, value=val})
      i = i + 1
      prev_end = finfo.offset + finfo.len
    end

    local file = io.open(directory .. pinfo.number .. ".dizz", "w")
    file:write("objects = [\n")
    for index, element in pairs(dizzy) do
      file:write("  Field(\"" .. element.name .. "\", b\""  .. element.value .. "\"),\n")
    end
    --output = output .. "  ]\n\n"
    file:write("  ]\n\n")
    file:write("functions = []\n")
    file:close()
  end
  return packet
end

local function export_to_dizzy(filter, frame, directory)
  if string.ends(directory, "/") == false then
    directory = directory .. "/"
  end
  local tap = Listener.new(frame, filter, true)
  tap.packet = create_listener_function(frame, directory)
end

local function dialog()
  new_dialog("Set Dizzy Listener", export_to_dizzy, "Filter", "Frame", "Directory")
end

-- add this to the Tools->Lua submenu
register_menu("Set Dizzy Listener", dialog, MENU_TOOLS_UNSORTED)
