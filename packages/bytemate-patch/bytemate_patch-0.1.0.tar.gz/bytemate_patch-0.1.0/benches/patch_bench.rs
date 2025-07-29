use criterion::{criterion_group, criterion_main, Criterion, BenchmarkId, Throughput};
use bytemate_patch::BytematePatch;
use serde_json::{json, Value};

fn generate_large_json(size: usize) -> Value {
    let mut users = Vec::new();
    for i in 0..size {
        users.push(json!({
            "_": format!("user_{}", i),
            "id": i,
            "name": format!("User {}", i),
            "email": format!("user{}@example.com", i),
            "profile": {
                "age": 20 + (i % 50),
                "settings": {
                    "theme": if i % 2 == 0 { "dark" } else { "light" },
                    "notifications": true,
                    "privacy": "public"
                },
                "scores": [i * 10, i * 20, i * 30]
            },
            "active": true,
            "created_at": "2025-01-01T00:00:00Z"
        }));
    }

    json!({
        "users": users,
        "settings": {
            "version": "1.0",
            "debug": false,
            "features": {
                "advanced_search": true,
                "real_time": false,
                "analytics": true
            }
        },
        "metadata": {
            "total_users": size,
            "last_updated": "2025-01-01T00:00:00Z",
            "server_info": {
                "version": "2.1.0",
                "uptime": 123456,
                "load": [1.2, 1.5, 1.1]
            }
        }
    })
}

fn generate_patch_operations(count: usize) -> BytematePatch {
    let mut patch = BytematePatch::new();

    for i in 0..count {
        match i % 6 {
            0 => {
                let patch_json = json!({
                    "users": {
                        format!("user_{}", i % 100): {
                            "name": format!("Updated User {}", i)
                        }
                    }
                });
                patch = BytematePatch::from_json(&patch_json).unwrap_or(patch);
            },
            1 => {
                let patch_json = json!({
                    "users": {
                        format!("new_user_{}", i): {
                            "*": {
                                "id": 9999 + i,
                                "name": format!("New User {}", i),
                                "active": true
                            }
                        }
                    }
                });
                patch = BytematePatch::from_json(&patch_json).unwrap_or(patch);
            },
            2 => {
                patch = patch.set("settings.version", json!("2.0"));
            },
            3 => {
                let patch_json = json!({
                    "settings": {
                        "features": {
                            "real_time": true
                        }
                    }
                });
                patch = BytematePatch::from_json(&patch_json).unwrap_or(patch);
            },
            4 => {
                patch = patch.set("[0]", json!({"updated": true}));
            },
            _ => {
                if i > 50 {
                    let patch_json = json!({
                        "users": {
                            format!("user_{}", i - 50): {"*": null}
                        }
                    });
                    patch = BytematePatch::from_json(&patch_json).unwrap_or(patch);
                }
            }
        }
    }

    patch
}

fn bench_basic_operations(c: &mut Criterion) {
    let mut group = c.benchmark_group("basic_operations");

    let small_data = json!({"a": 1, "b": {"c": 2, "d": 3}});
    let patch = BytematePatch::new()
        .set("a", json!(42))
        .set("b.e", json!(99));

    group.bench_function("small_patch_apply", |b| {
        b.iter(|| patch.apply(&small_data))
    });

    group.bench_function("small_patch_inplace", |b| {
        b.iter(|| {
            let mut data = small_data.clone();
            patch.apply_inplace(&mut data)
        })
    });

    group.finish();
}

fn bench_serial_operations(c: &mut Criterion) {
    let mut group = c.benchmark_group("serial_operations");

    for size in [10, 100, 1000].iter() {
        let data = json!({
            "items": (0..*size).map(|i| json!({
                "_": format!("item_{}", i),
                "value": i,
                "name": format!("Item {}", i)
            })).collect::<Vec<_>>()
        });

        let patch_json = json!({
            "items": {
                "item_5": {"value": 999},
                "item_50": {"name": "Updated Item"},
                "new_item": {"*": {"value": 777, "name": "New Item"}}
            }
        });
        let patch = BytematePatch::from_json(&patch_json).unwrap();

        group.throughput(Throughput::Elements(*size as u64));
        group.bench_with_input(
            BenchmarkId::new("serial_patch", size),
            size,
            |b, _| {
                b.iter(|| patch.apply(&data))
            }
        );
    }

    group.finish();
}

fn bench_large_documents(c: &mut Criterion) {
    let mut group = c.benchmark_group("large_documents");
    group.sample_size(20);
    group.warm_up_time(std::time::Duration::from_secs(2));

    for size in [100, 500, 1000].iter() {
        let data = generate_large_json(*size);
        let patch = generate_patch_operations(*size / 10);

        group.throughput(Throughput::Elements(*size as u64));
        group.bench_with_input(
            BenchmarkId::new("large_document", size),
            size,
            |b, _| {
                b.iter(|| patch.apply(&data))
            }
        );
    }

    group.finish();
}

fn bench_nested_operations(c: &mut Criterion) {
    let mut group = c.benchmark_group("nested_operations");

    let deep_data = json!({
        "level1": {
            "level2": {
                "level3": {
                    "level4": {
                        "level5": {
                            "value": 42,
                            "items": [1, 2, 3, 4, 5]
                        }
                    }
                }
            }
        }
    });

    let deep_patch_json = json!({
        "level1": {
            "level2": {
                "level3": {
                    "level4": {
                        "level5": {
                            "value": 999,
                            "new_field": "added"
                        }
                    }
                }
            }
        }
    });

    let deep_patch = BytematePatch::from_json(&deep_patch_json).unwrap();

    group.bench_function("deep_nesting", |b| {
        b.iter(|| deep_patch.apply(&deep_data))
    });

    group.finish();
}

fn bench_merge_operations(c: &mut Criterion) {
    let mut group = c.benchmark_group("merge_operations");

    for patch_count in [10, 50, 100].iter() {
        let patches: Vec<BytematePatch> = (0..*patch_count).map(|i| {
            BytematePatch::new()
                .set(format!("field_{}", i), json!(i * 10))
                .set("shared_field", json!(i))
        }).collect();

        group.bench_with_input(
            BenchmarkId::new("merge_patches", patch_count),
            patch_count,
            |b, _| {
                b.iter(|| {
                    let mut result = BytematePatch::new();
                    for patch in &patches {
                        result = BytematePatch::merge(result, patch.clone());
                    }
                    result
                })
            }
        );
    }

    group.finish();
}

fn bench_json_serialization(c: &mut Criterion) {
    let mut group = c.benchmark_group("json_serialization");

    let complex_patch = BytematePatch::new()
        .set("users", json!([{"_": "u1", "name": "John"}]))
        .delete("old_field")
        .move_key("temp", "permanent")
        .copy_key("source", "destination");

    let json_patch = complex_patch.to_json();

    group.bench_function("to_json", |b| {
        b.iter(|| complex_patch.to_json())
    });

    group.bench_function("from_json", |b| {
        b.iter(|| BytematePatch::from_json(&json_patch))
    });

    group.finish();
}

fn bench_memory_usage(c: &mut Criterion) {
    let mut group = c.benchmark_group("memory_efficiency");

    for size in [100, 500, 1000].iter() {
        let data = generate_large_json(*size);
        let patch = generate_patch_operations(10);

        // Test copy vs in-place
        group.bench_with_input(
            BenchmarkId::new("copy_approach", size),
            size,
            |b, _| {
                b.iter(|| patch.apply(&data))
            }
        );

        group.bench_with_input(
            BenchmarkId::new("inplace_approach", size),
            size,
            |b, _| {
                b.iter(|| {
                    let mut data_copy = data.clone();
                    patch.apply_inplace(&mut data_copy)
                })
            }
        );
    }

    group.finish();
}

criterion_group!(
    benches,
    bench_basic_operations,
    bench_serial_operations,
    bench_large_documents,
    bench_nested_operations,
    bench_merge_operations,
    bench_json_serialization,
    bench_memory_usage
);
criterion_main!(benches);
