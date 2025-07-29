--%%name:Timer Termination Test

print("=== TIMER TERMINATION TEST ===")

-- Set up a timer that fires after 2 seconds
print("Setting up timer for 2 seconds...")
setTimeout(function()
    print("Timer fired after 2 seconds!")
end, 2000)

-- Set up an interval that fires every 1 second, 3 times
print("Setting up interval for 1 second, 3 times...")
local count = 0
local interval_id = setInterval(function()
    count = count + 1
    print("Interval fired! Count:", count)
    if count >= 3 then
        print("Interval completed, clearing...")
        clearInterval(interval_id)
    end
end, 1000)

print("All timers set up. Script should terminate after all callbacks are processed.") 