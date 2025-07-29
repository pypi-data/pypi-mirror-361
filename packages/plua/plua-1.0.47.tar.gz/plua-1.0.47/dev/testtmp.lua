-- Test the new create_temp_directory function
  print("Testing create_temp_directory function...")
  
  -- Create a temporary directory
  local temp_dir = _PY.create_temp_directory("my_lua_app")
  print("Created temporary directory: " .. (temp_dir or "failed"))
  -- /var/folders/qf/141n5pm13kvdgc8nk_y7bkpw0000gn/T/
  if temp_dir then
      -- Check if it exists
      if _PY.file_exists(temp_dir) then
          print("✓ Directory exists")
      else
          print("✗ Directory does not exist")
      end
  
      -- List contents (should be empty)
      local files = _PY.list_files(temp_dir)
      if files then
          print("Directory contents: " .. #files .. " items")
          for i, file in ipairs(files) do
              print("  " .. i .. ": " .. file)
          end
      end
  
      -- Create a test file in the temp directory
      local test_file = temp_dir .. "/test.txt"
      if _PY.write_file(test_file, "Hello from Lua!") then
          print("✓ Created test file")
  
          -- Read it back
          local content = _PY.read_file(test_file)
          if content then
              print("✓ Read test file: " .. content)
          else
              print("✗ Failed to read test file")
          end
      else
          print("✗ Failed to create test file")
      end
  
      print("Temp directory path: " .. temp_dir)
      print("Note: You may want to clean up this directory manually")
  else
      print("✗ Failed to create temporary directory")
  end