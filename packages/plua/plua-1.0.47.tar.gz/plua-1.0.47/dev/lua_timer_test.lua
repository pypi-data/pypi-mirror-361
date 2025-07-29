--%%name:Lua Timer Test

-- Test the new Lua-based timer system

print("=== LUA TIMER TEST ===")

-- Test 1: Simple setTimeout
print("\n--- Test 1: Simple setTimeout ---")
local timer1 = setTimeout(function()
    print("Timer 1 fired!")
end, 1000)

print("Timer 1 ID:", timer1)

-- Test 2: setInterval
print("\n--- Test 2: setInterval ---")
local count = 0
local interval1 = setInterval(function()
    count = count + 1
    print("Interval fired, count:", count)
    if count >= 3 then
        print("Cancelling interval...")
        clearInterval(interval1)
    end
end, 500)

print("Interval 1 ID:", interval1)

-- Test 3: Multiple timers
print("\n--- Test 3: Multiple timers ---")
setTimeout(function()
    print("Quick timer (500ms)")
end, 500)

setTimeout(function()
    print("Medium timer (1000ms)")
end, 1000)

setTimeout(function()
    print("Slow timer (1500ms)")
end, 1500)

-- Keep the main coroutine alive
print("\nWaiting for all timers to complete...")
local wait_count = 0
while wait_count < 10 do
    _PY.sleep(1)
    wait_count = wait_count + 1
    print("Waited", wait_count, "seconds...")
end

print("=== TEST COMPLETED ===") 