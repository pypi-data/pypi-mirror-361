#!/usr/bin/env python3

def test_python_bindings():
    """Test basic Python bindings functionality"""

    print("🧪 Testing BYTEMATE:PATCH Python bindings...")

    try:
        from bytemate_patch import BytematePatch
        print("✅ Import successful")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

    try:
        patch = BytematePatch()
        patch.set("name", "John")
        patch.set("age", 30)
        print("✅ Set operations successful")
    except Exception as e:
        print(f"❌ Set operations failed: {e}")
        return False

    try:
        data = {"city": "Warsaw", "country": "Poland"}
        result = patch.apply(data)
        print(f"✅ Apply result: {result}")

        # Verify result
        expected_keys = {"city", "country", "name", "age"}
        if not expected_keys.issubset(result.keys()):
            print(f"❌ Missing keys in result: {expected_keys - result.keys()}")
            return False

    except Exception as e:
        print(f"❌ Apply failed: {e}")
        return False

    # Test 4: From JSON
    try:
        patch_json = {
            "users": {
                "user1": {"name": "Alice"},
                "user2": {"*": None}
            }
        }

        patch2 = BytematePatch.from_json(patch_json)
        print("✅ from_json successful")
    except Exception as e:
        print(f"❌ from_json failed: {e}")
        return False

    try:
        complex_data = {
            "users": [
                {"_": "user1", "name": "Bob", "active": True},
                {"_": "user2", "name": "Charlie", "active": False}
            ]
        }

        result2 = patch2.apply(complex_data)
        print(f"✅ Complex data result: {result2}")

        # Verify serial key operations worked
        if len(result2["users"]) != 1:
            print(f"❌ Expected 1 user after deletion, got {len(result2['users'])}")
            return False

        if result2["users"][0]["name"] != "Alice":
            print(f"❌ Expected Alice, got {result2['users'][0]['name']}")
            return False

    except Exception as e:
        print(f"❌ Complex data test failed: {e}")
        return False

    # Test 6: Merge patches
    try:
        minor_patch = BytematePatch()
        minor_patch.set("a", 1)
        minor_patch.set("b", 2)

        major_patch = BytematePatch()
        major_patch.set("b", 999)
        major_patch.set("c", 3)

        merged = BytematePatch.merge(minor_patch, major_patch)

        test_data = {}
        merge_result = merged.apply(test_data)

        expected_merge = {"a": 1, "b": 999, "c": 3}
        if merge_result != expected_merge:
            print(f"❌ Merge failed: expected {expected_merge}, got {merge_result}")
            return False

        print("✅ Merge operations successful")

    except Exception as e:
        print(f"❌ Merge test failed: {e}")
        return False

    # Test 7: Performance test
    try:
        import time

        large_data = {
            "items": [
                {"_": f"item_{i}", "value": i, "data": f"data_{i}"}
                for i in range(1000)
            ]
        }

        perf_patch = BytematePatch()
        perf_patch.set("item_500", {"value": 999, "updated": True})

        start_time = time.time()
        perf_result = perf_patch.apply(large_data)
        end_time = time.time()

        duration = (end_time - start_time) * 1000
        print(f"✅ Performance test: {duration:.2f}ms for 1000 items")

        if duration > 100:
            print(f"⚠️  Performance warning: {duration:.2f}ms seems slow")

    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

    print("🎉 All Python tests passed!")

    return True

if __name__ == "__main__":
    success = test_python_bindings()
    if success:
        print("\n🚀 Python bindings are working perfectly!")
    else:
        print("\n💥 Some tests failed!")
        exit(1)
