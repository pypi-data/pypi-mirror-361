use bytemate_patch::{BytematePatch, BytemateError, PatchOperation};
use serde_json::json;

#[test]
fn test_edit_nested_object() {
    let data = json!({
        "b": 7,
        "c": {
            "d": 8,
            "e": 9,
        },
    });

    let patch_json = json!({"c": {"d": 3}});
    let patch = BytematePatch::from_json(&patch_json).unwrap();
    let result = patch.apply(&data).unwrap();

    let expected = json!({"b": 7, "c": {"d": 3, "e": 9}});
    assert_eq!(result, expected);
}

#[test]
fn test_overwrite_with_star() {
    let data = json!({
        "b": 7,
        "c": {
            "d": 8,
            "e": 9,
        },
    });

    let patch_json = json!({"c": {"*": {"d": 3}}});
    let patch = BytematePatch::from_json(&patch_json).unwrap();
    let result = patch.apply(&data).unwrap();

    let expected = json!({"b": 7, "c": {"d": 3}});
    assert_eq!(result, expected);
}

#[test]
fn test_edit_by_serial() {
    let data = json!({
        "a": [
            {
                "_": "123456",
                "b": 1,
            },
            {
                "_": "654321",
                "b": 2,
            },
        ]
    });

    let patch_json = json!({"a": {"123456": {"b": 3}}});
    let patch = BytematePatch::from_json(&patch_json).unwrap();
    let result = patch.apply(&data).unwrap();

    let expected = json!({
        "a": [
            {"_": "123456", "b": 3},
            {"_": "654321", "b": 2}
        ]
    });
    assert_eq!(result, expected);
}

#[test]
fn test_edit_by_serial_not_found() {
    let data = json!({
        "a": [
            {
                "_": "123456",
                "b": 1,
            },
            {
                "_": "654321",
                "b": 2,
            },
        ]
    });

    let patch_json = json!({"a": {"999999": {"b": 3}}});
    let patch = BytematePatch::from_json(&patch_json).unwrap();
    
    let result = patch.apply(&data);
    assert!(matches!(result, Err(BytemateError::InvalidSerial(_))));
}

#[test]
fn test_overwrite_by_serial_addition() {
    let data = json!({
        "a": [
            {
                "_": "123456",
                "b": 1,
            },
            {
                "_": "654321",
                "b": 2,
            },
        ]
    });

    let patch_json = json!({"a": {"999999": {"*": {"b": 3}}}});
    let patch = BytematePatch::from_json(&patch_json).unwrap();
    let result = patch.apply(&data).unwrap();

    let expected = json!({
        "a": [
            {"_": "123456", "b": 1},
            {"_": "654321", "b": 2},
            {"_": "999999", "b": 3},
        ]
    });
    assert_eq!(result, expected);
}

#[test]
fn test_set_null_value() {
    let data = json!({
        "a": 1,
        "b": 2,
        "c": 3,
    });

    let patch = BytematePatch::new().set("a", json!(null));
    let result = patch.apply(&data).unwrap();

    let expected = json!({"a": null, "b": 2, "c": 3});
    assert_eq!(result, expected);
}

#[test]
fn test_delete_with_star_notation() {
    let data = json!({
        "a": 1,
        "b": 2,
        "c": 3,
    });

    let patch_json = json!({"a": {"*": null}});
    let patch = BytematePatch::from_json(&patch_json).unwrap();
    let result = patch.apply(&data).unwrap();

    let expected = json!({"b": 2, "c": 3});
    assert_eq!(result, expected);
}

#[test]
fn test_merge_patches() {
    let minor_patch = BytematePatch::new()
        .set("a", json!(1))
        .set("b", json!(2));

    let major_patch = BytematePatch::new()
        .set("b", json!(999))
        .set("c", json!(3));

    let merged = BytematePatch::merge(minor_patch, major_patch);

    let data = json!({});
    let result = merged.apply(&data).unwrap();

    let expected = json!({"a": 1, "b": 999, "c": 3});
    assert_eq!(result, expected);
}

#[test]
fn test_array_index_operations() {
    let data = json!([1, 2, 3, 4]);

    let patch = BytematePatch::new()
        .set("[1]", json!(999))
        .delete("[3]");

    let result = patch.apply(&data).unwrap();
    let expected = json!([1, 999, 3]);
    assert_eq!(result, expected);
}

#[test]
fn test_move_operation() {
    let data = json!({"a": 1, "b": 2, "c": 3});

    let patch = BytematePatch::new()
        .move_key("a", "d");

    let result = patch.apply(&data).unwrap();
    let expected = json!({"b": 2, "c": 3, "d": 1});
    assert_eq!(result, expected);
}

#[test]
fn test_copy_operation() {
    let data = json!({"a": 1, "b": 2});

    let patch = BytematePatch::new()
        .copy_key("a", "c");

    let result = patch.apply(&data).unwrap();
    let expected = json!({"a": 1, "b": 2, "c": 1});
    assert_eq!(result, expected);
}

#[test]
fn test_test_operation_success() {
    let data = json!({"a": 1, "b": 2});

    let patch = BytematePatch::new()
        .test("a", json!(1))
        .set("b", json!(999));

    let result = patch.apply(&data).unwrap();
    let expected = json!({"a": 1, "b": 999});
    assert_eq!(result, expected);
}

#[test]
fn test_test_operation_failure() {
    let data = json!({"a": 1, "b": 2});

    let patch = BytematePatch::new()
        .test("a", json!(999))
        .set("b", json!(777));

    let result = patch.apply(&data);
    assert!(matches!(result, Err(BytemateError::TypeMismatch { .. })));
}

#[test]
fn test_json_serialization_roundtrip() {
    let original_patch = BytematePatch::new()
        .set("a", json!(42))
        .delete("b")
        .edit("c", vec![
            ("d".to_string(), PatchOperation::Set(json!(123)))
        ]);

    let json_patch = original_patch.to_json();
    let restored_patch = BytematePatch::from_json(&json_patch).unwrap();

    let data = json!({"a": 1, "b": 2, "c": {"d": 3, "e": 4}});

    let result1 = original_patch.apply(&data).unwrap();
    let result2 = restored_patch.apply(&data).unwrap();

    assert_eq!(result1, result2);
}

#[test]
fn test_complex_nested_operations() {
    let data = json!({
        "users": [
            {"_": "u1", "name": "Jan", "settings": {"theme": "light"}},
            {"_": "u2", "name": "Anna", "settings": {"theme": "dark"}}
        ],
        "config": {"debug": true}
    });

    let patch_json = json!({
        "users": {
            "u1": {"settings": {"theme": "dark"}},
            "u2": {"name": "Ania"}
        },
        "config": {"debug": false, "version": "1.0"}
    });

    let patch = BytematePatch::from_json(&patch_json).unwrap();
    let result = patch.apply(&data).unwrap();

    assert_eq!(result["users"][0]["settings"]["theme"], json!("dark"));
    assert_eq!(result["users"][1]["name"], json!("Ania"));
    assert_eq!(result["config"]["debug"], json!(false));
    assert_eq!(result["config"]["version"], json!("1.0"));
}
