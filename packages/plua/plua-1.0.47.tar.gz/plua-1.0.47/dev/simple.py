#!/usr/bin/env python3
"""
Simple example of using Lupa to run Lua code from Python
"""

import lupa
import asyncio
from datetime import datetime

initScript = """
-- Initialize Lua environment

  local _timers = {}
  function _runTimers(t)
    if t then _timers[#_timers+1] = t return end
    while #_timers > 0 do
      local t = table.remove(_timers, 1)
      if t then t() end
    end
  end

  -- Keep coroutine handling in Lua
  local function _timer(fun,ms,...)
    local co = coroutine.create(fun)
    local args = {...}
    pythonTimer(function()
       print("PT resume")
      coroutine.resume(co,table.unpack(args))
    end, ms)
  end

  -- Simulate a Python timer function in Lua
  function netWorkIO(callback)
    _timer(callback,1000,"xyz")
  end

  function sleep(ms)
    local co = coroutine.running()
    pythonTimer(function()
       coroutine.resume(co)
    end, ms)
    coroutine.yield()
  end

  function setTimeout(fun,ms)
    _timer(fun, ms)
  end
"""

testScript = """
  local function foo()
    local function loop()
      print("PING")
      netWorkIO(function(data) print("Network callback", data) end)
      setTimeout(loop,5000)
    end
    setTimeout(loop,100)
  end
  foo()
"""

testScript2 = """
  local function foo()
    print("A")
    local co = coroutine.running()
    setTimeout(function() print("D",coroutine.status(co)) coroutine.resume(co) print("E") end, 1000)
    print("B")
    coroutine.yield()
    print("C")
  end
  coroutine.wrap(foo)()
"""


def create_timer(lua_runtime, lua_function, delay_ms):
    """Create a timer that calls the lua_function after delay_ms milliseconds with optional arguments"""
    loop = asyncio.get_event_loop()

    def timer_callback():
        try:
            current_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]  # Format: HH:MM:SS.mmm
            print(f"[{current_time}] Timer firing (scheduled for {delay_ms}ms), calling lua function: {lua_function}")
            lua_runtime.globals()['_runTimers'](lua_function)
            completion_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"[{completion_time}] Lua function completed successfully")
        except Exception as e:
            error_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"[{error_time}] Timer callback error: {e}")
            import traceback
            traceback.print_exc()

    # Convert milliseconds to seconds for asyncio
    delay_seconds = delay_ms / 1000.0
    schedule_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{schedule_time}] Setting timer for {delay_seconds} seconds")
    return loop.call_later(delay_seconds, timer_callback)


async def startLua():
    """
    Initialize the Lua runtime and execute a simple Lua script.
    """
    start_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{start_time}] Starting Lua runtime...")

    lua = lupa.LuaRuntime(unpack_returned_tuples=True)
    lua.execute(initScript)

    # Create a continuous loop
    async def keep_alive_loop():
        counter = 0
        while True:
            current_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"[{current_time}] Keep-alive loop iteration {counter}")
            lua.execute("__runTimers()")
            counter += 1
            await asyncio.sleep(0.5)  # Use asyncio.sleep instead of time.sleep

    # Start the keep-alive loop
    # print(f"[{execution_time}] Starting continuous loop...")
    keep_alive_task = asyncio.create_task(keep_alive_loop())

    # Add a print function to Lua that includes timestamps
    def lua_print(*args):
        current_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        message = " ".join(str(arg) for arg in args)
        print(f"[{current_time}] LUA: {message}")

    lua.globals().print = lua_print

    # Create a wrapper function that captures the lua runtime
    def pythonTimer(lua_function, delay_ms):
        return create_timer(lua, lua_function, delay_ms)

    # Set up the pythonTimer function
    lua.globals().pythonTimer = pythonTimer

    # Execute the test script directly in a coroutine and resume it immediately
    execution_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{execution_time}] Executing Lua test script...")
    lua.execute(f"coroutine.wrap(function () {testScript2} end)()")

    # Keep the event loop running for a while to see the timers fire
    print(f"[{execution_time}] Waiting for timers to fire for 30 seconds...")

    # Add periodic status checks
    for i in range(30):
        await asyncio.sleep(1)
        current_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        pending_tasks = len([task for task in asyncio.all_tasks() if not task.done()])
        print(f"[{current_time}] Second {i+1}/30 - Pending tasks: {pending_tasks}")

    end_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{end_time}] Program ending")

    return lua


async def main():
    await startLua()

if __name__ == "__main__":
    asyncio.run(main())