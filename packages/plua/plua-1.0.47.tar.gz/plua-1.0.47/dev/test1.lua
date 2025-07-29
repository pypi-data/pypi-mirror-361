--%%name:Test1

-- local function async_call(str,func)
--   setTimeout(function()
--     func("echo:"..str)
--   end,1000)
-- end

local function async_call(str,func)
  local socket = net:TCPSocket()
  socket:connect("tcpbin.com", 4242,{
    success = function()
      socket:write(str.."\n",{
        success = function() 
          print("write success")
          socket:read({
            success = function(data) 
              print("read success")
              func(true,data)
            end,
            error = function(err) 
              print("read error")
              func(false,err) 
            end
          })
        end,
        error = function(err) 
          print("write error")
          func(false,err) 
        end
      })
    end
  })
end

local function ask(str)
  local co = coroutine.running()
  async_call(str,function(...) coroutine.resume(co,...) end)
  return coroutine.yield()
end

function QuickApp:onInit()
  print(ask("Hello"))
end