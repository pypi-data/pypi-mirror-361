--%%name:Coro5

-- Test that mimics coro1.lua: resume the main coroutine from a timer callback

local function test()
  print("A")
  local co = coroutine.running()  -- Get the current coroutine
  setTimeout(function() 
    print("D") 
    print("About to resume main coroutine...")
    coroutine.resume(co)  -- Resume the main coroutine
    print("Resume call completed")
  end, 1000)
  print("B")
  coroutine.yield()
  print("C")
end

-- Run this as the main function (like PLua does)
test() 