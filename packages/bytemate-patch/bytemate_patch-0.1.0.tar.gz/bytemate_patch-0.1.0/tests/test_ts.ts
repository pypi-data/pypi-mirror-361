
import pkg from '../pkg/bytemate_patch.js';
const { JsBytematePatch, version } = pkg;

async function testJavaScriptBindings() {
    console.log('🧪 Testing BYTEMATE:PATCH JavaScript bindings...');

    console.log(`📦 Version: ${version()}`);

    // Test 1: Import and constructor
    try {
        const patch = new JsBytematePatch();
        console.log('✅ Import and constructor successful');
    } catch (e) {
        console.log(`❌ Import failed: ${e}`);
        return false;
    }

    // Test 2: Basic operations
    try {
        const patch = new JsBytematePatch();
        patch.set("name", "John");
        patch.set("age", 30);
        console.log('✅ Set operations successful');
    } catch (e) {
        console.log(`❌ Set operations failed: ${e}`);
        return false;
    }

    // Test 3: Apply patch
    try {
        const patch = new JsBytematePatch();
        patch.set("name", "John");
        patch.set("age", 30);

        const data = { city: "Warsaw", country: "Poland" };
        const result = patch.apply(data);
        console.log(`✅ Apply result:`, result);

        // Verify result
        const expectedKeys = new Set(["city", "country", "name", "age"]);
        const resultKeys = new Set(Object.keys(result));
        const hasAllKeys = [...expectedKeys].every(key => resultKeys.has(key));

        if (!hasAllKeys) {
            console.log(`❌ Missing keys in result`);
            return false;
        }
    } catch (e) {
        console.log(`❌ Apply failed: ${e}`);
        return false;
    }

    // Test 4: From JSON
    try {
        const patchJson = {
            users: {
                user1: { name: "Alice" },
                user2: { "*": null }  // Delete syntax
            }
        };

        const patch2 = JsBytematePatch.fromJson(patchJson);
        console.log('✅ fromJson successful');
    } catch (e) {
        console.log(`❌ fromJson failed: ${e}`);
        return false;
    }

    // Test 5: Complex data with serial keys
    try {
        const patchJson = {
            users: {
                user1: { name: "Alice" },
                user2: { "*": null }
            }
        };
        const patch2 = JsBytematePatch.fromJson(patchJson);

        const complexData = {
            users: [
                { _: "user1", name: "Bob", active: true },
                { _: "user2", name: "Charlie", active: false }
            ]
        };

        const result2 = patch2.apply(complexData);
        console.log(`✅ Complex data result:`, result2);

        // Verify serial key operations worked
        if (result2.users.length !== 1) {
            console.log(`❌ Expected 1 user after deletion, got ${result2.users.length}`);
            return false;
        }

        if (result2.users[0].name !== "Alice") {
            console.log(`❌ Expected Alice, got ${result2.users[0].name}`);
            return false;
        }
    } catch (e) {
        console.log(`❌ Complex data test failed: ${e}`);
        return false;
    }

    // Test 6: Merge patches
    try {
        const minorPatch = new JsBytematePatch();
        minorPatch.set("a", 1);
        minorPatch.set("b", 2);

        const majorPatch = new JsBytematePatch();
        majorPatch.set("b", 999);
        majorPatch.set("c", 3);

        const merged = JsBytematePatch.merge(minorPatch, majorPatch);

        const testData = {};
        const mergeResult = merged.apply(testData);

        const expected = { a: 1, b: 999, c: 3 };
        const isEqual = JSON.stringify(mergeResult) === JSON.stringify(expected);

        if (!isEqual) {
            console.log(`❌ Merge failed: expected ${JSON.stringify(expected)}, got ${JSON.stringify(mergeResult)}`);
            return false;
        }

        console.log('✅ Merge operations successful');
    } catch (e) {
        console.log(`❌ Merge test failed: ${e}`);
        return false;
    }

    // Test 7: Performance test
    try {
        const largeData = {
            items: Array.from({ length: 1000 }, (_, i) => ({
                _: `item_${i}`,
                value: i,
                data: `data_${i}`
            }))
        };

        const perfPatch = new JsBytematePatch();
        perfPatch.set("item_500", { value: 999, updated: true });

        const startTime = performance.now();
        const perfResult = perfPatch.apply(largeData);
        const endTime = performance.now();

        const duration = endTime - startTime;
        console.log(`✅ Performance test: ${duration.toFixed(2)}ms for 1000 items`);

        if (duration > 100) {
            console.log(`⚠️  Performance warning: ${duration.toFixed(2)}ms seems slow`);
        }
    } catch (e) {
        console.log(`❌ Performance test failed: ${e}`);
        return false;
    }

    // Test 8: Length and isEmpty
    try {
        const patch = new JsBytematePatch();
        if (!patch.isEmpty()) {
            console.log(`❌ New patch should be empty`);
            return false;
        }

        patch.set("test", 123);
        if (patch.length !== 1) {
            console.log(`❌ Patch length should be 1, got ${patch.length}`);
            return false;
        }

        if (patch.isEmpty()) {
            console.log(`❌ Patch with operations should not be empty`);
            return false;
        }

        console.log('✅ Length and isEmpty operations successful');
    } catch (e) {
        console.log(`❌ Length/isEmpty test failed: ${e}`);
        return false;
    }

    console.log('🎉 All JavaScript tests passed!');
    return true;
}

testJavaScriptBindings().then(success => {
    if (success) {
        console.log('\n🚀 JavaScript bindings are working perfectly!');
        process.exit(0);
    } else {
        console.log('\n💥 Some tests failed!');
        process.exit(1);
    }
}).catch(e => {
    console.error('💥 Test runner failed:', e);
    process.exit(1);
});
