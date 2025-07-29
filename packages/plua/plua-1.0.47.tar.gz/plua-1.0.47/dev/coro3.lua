--%%name:Coro3

-- Simple test: just resume a coroutine from a timer callback
-- No yielding involved

local function test()
  print("A")
  print("B")
  print("C")
end

local co = coroutine.create(test)
print("Created coroutine")

-- Start the coroutine
coroutine.resume(co)
print("First resume done")

-- Set a timer that will try to resume the already-dead coroutine
setTimeout(function() 
  print("Timer fired, attempting to resume coroutine...")
  local status = coroutine.status(co)
  print("Coroutine status:", status)
  
  if status == "dead" then
    print("Coroutine is dead, not resuming")
  else
    print("Attempting to resume...")
    coroutine.resume(co)  -- This should be safe since coroutine is dead
  end
  
  print("Timer callback completed")
end, 1000)

print("Timer set, waiting...") 