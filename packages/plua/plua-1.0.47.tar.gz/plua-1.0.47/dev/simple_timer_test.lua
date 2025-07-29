--%%name:Simple Timer Test

print("=== SIMPLE TIMER TEST ===")

-- Test basic setTimeout
print("Setting up timer...")
setTimeout(function()
    print("Timer fired!")
end, 1000)

print("Timer set, waiting...")

-- Keep the main coroutine alive
_PY.sleep(2)
print("Test completed!") 