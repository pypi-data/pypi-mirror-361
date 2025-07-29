--%%name:Coro6

-- Test using polling pattern instead of direct coroutine resume

local function test()
  print("A")
  
  -- Use a flag to signal completion
  local done = false
  
  setTimeout(function() 
    print("D") 
    done = true  -- Just set a flag
  end, 1000)
  
  print("B")
  
  -- Poll for completion instead of yielding
  while not done do
    -- Small sleep to prevent busy waiting
    _PY.sleep(0.1)
  end
  
  print("C")
end

-- Run this as the main function
test() 