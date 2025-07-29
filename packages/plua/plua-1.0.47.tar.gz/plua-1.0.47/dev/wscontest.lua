--%%name:WSTest

local mobdebug = require("mobdebug")

local function WebSocketChannel(host,port,cb,debugFlag)
  
  local server = net.WebSocketServer(false)
  local clients = {}
  
  local function Client(client_id)
    local self = {}
    function self:send(str) server:send(client_id,str) end
    function self:_receive(msg) if self.receive then  self:receive(msg) end end
    return self
  end
  
  local function debug(...)
    if debugFlag then print("[WSC] "..tostring(server.server_id), string.format(...)) end
  end
  
  server:start(host, port, {
    receive = function(client_id, msg)
      --debug("Received from client: %s", #msg)
      if clients[client_id] then
        clients[client_id]:_receive(msg)
      end
    end,
    connected = function(client_id)
      debug("Client connected: %s", tostring(client_id))
      local client = Client(client_id)
      clients[client_id] = client
      cb(client)
    end,
    disconnected = function(client_id)
      debug("Client disconnected: %s", tostring(client_id))
      clients[client_id] = nil
    end
  })
  
  return server
end

local channel = nil
local function Channel(client)
  mobdebug.on()
  local self = {}
  local co = nil
  function client:receive(msg) 
    coroutine.resume(co,msg)
  end
  function self:send(str)
    co = coroutine.running()
    client:send(str)
    return coroutine.yield()
  end
  
  return self
end

local function tester(client)
  local ch = Channel(client)
  print("Channel set")
  channel = ch
end

function QuickApp:onInit()
  mobdebug.on()
  WebSocketChannel("192.168.1.33", 8769, tester, true)
  setTimeout(function() fibaro.call(4102,"connect","ws://192.168.1.33:8769") end,10)
  
  local msg = ("***"):rep(1024)
  local function test_send()
    print("Try to send")
    if not channel then setTimeout(test_send,1000) end
    for i=1,5 do
      local response = channel:send(msg)
      print("Received:", #response,i)
    end
  end

  test_send()
  
  setInterval(function() end, 2000) -- Keep alive
end