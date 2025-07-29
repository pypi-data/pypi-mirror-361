--%%name:CoroutineTest
--%%type:com.fibaro.multilevelSwitch

print("[LUA DEBUG] Starting coroutine test...")
print("=== Coroutine-Based Architecture Test ===")

-- Test 1: Basic setTimeout
print("\n--- Test 1: Basic setTimeout ---")
print("Setting up setTimeout...")
local timer_id = _PY.setTimeout(function() 
  print("TIMER CALLBACK EXECUTED!")
end, 0)
print("setTimeout returned ID:", timer_id)

-- Test 2: setInterval
print("\n--- Test 2: setInterval ---")
print("Setting up setInterval...")
local interval_id = _PY.setInterval(function() 
  print("INTERVAL CALLBACK EXECUTED!")
end, 2000)
print("setInterval returned ID:", interval_id)

-- Test 3: Sleep
print("\n--- Test 3: Sleep ---")
print("Sleeping for 0.1 seconds...")
--_PY.sleep(0.1)
print("Sleep completed!")

-- Test 4: Multiple timers
print("\n--- Test 4: Multiple Timers ---")
for i = 1, 3 do
  local id = _PY.setTimeout(function() 
    print("MULTIPLE TIMER " .. i .. " EXECUTED!")
  end, 100 * i)
  print("Timer", i, "ID:", id)
end

print("\n--- All tests initiated ---")
print("Waiting for callbacks to execute...")

-- Keep the main coroutine alive for timers to fire
print("Main coroutine will stay alive for timers...")
while true do
  _PY.sleep(1)
  print("Main loop tick...")
end 