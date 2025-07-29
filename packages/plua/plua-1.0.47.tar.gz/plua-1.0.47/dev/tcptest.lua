--%%name:TCPTest

local function TCPChannel(host,port,cb,debugFlag)
  
  local server = net.TCPServer(false)
  local clients = {}

  local function Client(client,cb)
    local self = {}
    function self:send(str) server:send(client,str) end
    function self:_receive(msg) if self.receive then  self:receive(msg) end end
    return self
  end
end
