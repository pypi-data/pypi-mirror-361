--%%name:Coro
local mobdebug = require("mobdebug")

print("setTimeout is:", setTimeout)
print("_PY.setTimeout is:", _PY and _PY.setTimeout)

local function test()
  mobdebug.on()
  print("A")
  local co = coroutine.running()
  print("Coroutine created:", co)
  print("Coroutine status:", coroutine.status(co))
  
  setTimeout(function() 
    print("D") 
    print("About to resume coroutine:", co)
    print("Coroutine type:", type(co))
    print("Coroutine is nil:", co == nil)
    if co then
      print("Coroutine status before resume:", coroutine.status(co))
      print("About to call coroutine.resume...")
      if coroutine.status(co) == "suspended" then
        local success, result = coroutine.resume(co)
        print("Resume result:", success, result)
      else
        print("Cannot resume coroutine - status is:", coroutine.status(co))
      end
    else
      print("ERROR: Coroutine reference is nil!")
    end
    print("E") 
  end, 1000)
  
  print("B")
  print("About to yield...")
  coroutine.yield()
  print("C")
end

-- local co = coroutine.create(test)
-- print("Main coroutine status before first resume:", coroutine.status(co))
-- coroutine.resume(co)
function QuickApp:onInit()
  test()
end






