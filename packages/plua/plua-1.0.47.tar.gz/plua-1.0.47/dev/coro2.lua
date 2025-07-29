--%%name:Coro2

-- This test demonstrates the correct pattern for timers and coroutines in PLua
-- The key is to NOT call coroutine.resume from within the timer callback

local function test()
  print("A")
  
  -- Use a flag to signal completion instead of direct coroutine.resume
  local done = false
  
  setTimeout(function() 
    print("D") 
    done = true  -- Just set a flag, don't call coroutine.resume
  end, 1000)
  
  print("B")
  
  -- Yield and wait for the flag to be set
  while not done do
    coroutine.yield()
  end
  
  print("C")
end

local co = coroutine.create(test)
coroutine.resume(co) 