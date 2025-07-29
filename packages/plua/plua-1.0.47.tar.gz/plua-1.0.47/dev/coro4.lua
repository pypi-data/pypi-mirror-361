--%%name:Coro4

-- Test: resume a suspended coroutine from a timer callback

local function test()
  print("A")
  coroutine.yield()  -- Suspend the coroutine
  print("B")
  coroutine.yield()  -- Suspend again
  print("C")
end

local co = coroutine.create(test)
print("Created coroutine")

-- Start the coroutine (it will yield after printing "A")
coroutine.resume(co)
print("First resume done")

-- Set a timer that will resume the suspended coroutine
setTimeout(function() 
  print("Timer fired, attempting to resume suspended coroutine...")
  local status = coroutine.status(co)
  print("Coroutine status:", status)
  
  if status == "suspended" then
    print("Attempting to resume suspended coroutine...")
    coroutine.resume(co)  -- This should resume the coroutine
    print("Resume call completed")
  else
    print("Coroutine is not suspended, status:", status)
  end
  
  print("Timer callback completed")
end, 1000)

print("Timer set, waiting...") 