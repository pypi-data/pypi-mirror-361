use serde_json::{Value, Map};
use std::collections::{HashMap, HashSet};
use crate::{Result, BytemateError, PatchOperation};

#[derive(Debug, Clone)]
pub struct BytematePatch {
    operations: HashMap<String, PatchOperation>,
}

impl BytematePatch {
    #[inline]
    pub fn new() -> Self {
        Self {
            operations: HashMap::with_capacity(4),
        }
    }

    #[inline]
    pub fn apply(&self, target: &Value) -> Result<Value> {
        let mut result = target.clone();
        self.apply_inplace(&mut result)?;
        Ok(result)
    }

    #[inline]
    pub fn apply_inplace(&self, target: &mut Value) -> Result<()> {
        match target {
            Value::Object(obj) => self.apply_to_object(obj),
            Value::Array(arr) => self.apply_to_array(arr),
            _ => Err(BytemateError::InvalidOperation(
                "Can only patch objects and arrays".into()
            )),
        }
    }

    fn apply_to_object(&self, obj: &mut Map<String, Value>) -> Result<()> {
        for (key, operation) in &self.operations {
            if key == "_" {
                continue;
            }

            match operation {
                PatchOperation::Set(value) => {
                    obj.insert(key.clone(), value.clone());
                }
                PatchOperation::Delete => {
                    obj.remove(key);
                }
                PatchOperation::Edit(sub_ops) => {
                    if let Some(target_value) = obj.get_mut(key) {
                        Self::apply_operations_direct(target_value, sub_ops)?;
                    }
                }
                PatchOperation::Move { from, to } => {
                    if let Some(value) = obj.remove(from) {
                        obj.insert(to.clone(), value);
                    }
                }
                PatchOperation::Copy { from, to } => {
                    if let Some(value) = obj.get(from) {
                        obj.insert(to.clone(), value.clone());
                    }
                }
                PatchOperation::Test { expected } => {
                    if let Some(actual) = obj.get(key) {
                        if actual != expected {
                            return Err(BytemateError::TypeMismatch {
                                expected: expected.to_string(),
                                found: actual.to_string(),
                            });
                        }
                    } else {
                        return Err(BytemateError::KeyNotFound(key.clone()));
                    }
                }
            }
        }
        Ok(())
    }

    fn apply_to_array(&self, arr: &mut Vec<Value>) -> Result<()> {
        let serial_index: HashMap<String, usize> = arr
            .iter()
            .enumerate()
            .filter_map(|(i, item)| {
                item.get("_")?.as_str().map(|serial| (serial.to_string(), i))
            })
            .collect();

        let mut items_to_remove = Vec::new();
        let mut items_to_add = Vec::new();

        for (key, operation) in &self.operations {
            if key == "_" {
                continue;
            }

            if let Some(index) = Self::parse_array_index_fast(key) {
                if index < arr.len() {
                    match operation {
                        PatchOperation::Set(value) => {
                            arr[index] = value.clone();
                        }
                        PatchOperation::Delete => {
                            items_to_remove.push(index);
                        }
                        PatchOperation::Edit(sub_ops) => {
                            Self::apply_operations_direct(&mut arr[index], sub_ops)?;
                        }
                        PatchOperation::Test { expected } => {
                            if &arr[index] != expected {
                                return Err(BytemateError::TypeMismatch {
                                    expected: expected.to_string(),
                                    found: arr[index].to_string(),
                                });
                            }
                        }
                        _ => {
                            return Err(BytemateError::InvalidOperation(
                                "Operation not supported on array indices".into()
                            ));
                        }
                    }
                }
                continue;
            }

            if let Some(&index) = serial_index.get(key) {
                match operation {
                    PatchOperation::Set(value) => {
                        let mut new_value = value.clone();
                        if let Value::Object(ref mut obj) = new_value {
                            obj.insert("_".to_string(), Value::String(key.clone()));
                        }
                        arr[index] = new_value;
                    }
                    PatchOperation::Delete => {
                        items_to_remove.push(index);
                    }
                    PatchOperation::Edit(sub_ops) => {
                        Self::apply_operations_direct(&mut arr[index], sub_ops)?;
                    }
                    PatchOperation::Test { expected } => {
                        if &arr[index] != expected {
                            return Err(BytemateError::TypeMismatch {
                                expected: expected.to_string(),
                                found: arr[index].to_string(),
                            });
                        }
                    }
                    _ => {
                        return Err(BytemateError::InvalidOperation(
                            "Operation not supported on array serials".into()
                        ));
                    }
                }
            } else {
                match operation {
                    PatchOperation::Set(value) => {
                        let mut new_item = value.clone();
                        if let Value::Object(ref mut obj) = new_item {
                            obj.insert("_".to_string(), Value::String(key.clone()));
                        }
                        items_to_add.push(new_item);
                    }
                    PatchOperation::Edit(_) => {
                        return Err(BytemateError::InvalidSerial(key.clone()));
                    }
                    _ => {
                        return Err(BytemateError::InvalidSerial(key.clone()));
                    }
                }
            }
        }

        items_to_remove.sort_unstable_by(|a, b| b.cmp(a));
        for &index in &items_to_remove {
            if index < arr.len() {
                arr.remove(index);
            }
        }

        arr.extend(items_to_add);
        Ok(())
    }

    #[inline]
    fn parse_array_index_fast(key: &str) -> Option<usize> {
        let bytes = key.as_bytes();
        if bytes.len() >= 3 && bytes[0] == b'[' && bytes[bytes.len() - 1] == b']' {
            std::str::from_utf8(&bytes[1..bytes.len()-1])
                .ok()?
                .parse()
                .ok()
        } else {
            None
        }
    }

    fn apply_operations_direct(target: &mut Value, operations: &[(String, PatchOperation)]) -> Result<()> {
        match target {
            Value::Object(obj) => {
                for (key, operation) in operations {
                    match operation {
                        PatchOperation::Set(value) => {
                            obj.insert(key.clone(), value.clone());
                        }
                        PatchOperation::Delete => {
                            obj.remove(key);
                        }
                        PatchOperation::Edit(sub_ops) => {
                            if let Some(target_value) = obj.get_mut(key) {
                                Self::apply_operations_direct(target_value, sub_ops)?;
                            }
                        }
                        _ => {}
                    }
                }
            }
            Value::Array(arr) => {
                let serial_index: HashMap<String, usize> = arr
                    .iter()
                    .enumerate()
                    .filter_map(|(i, item)| {
                        item.get("_")?.as_str().map(|serial| (serial.to_string(), i))
                    })
                    .collect();

                let mut items_to_remove = Vec::new();
                let mut items_to_add = Vec::new();

                for (key, operation) in operations {
                    if let Some(&index) = serial_index.get(key) {
                        match operation {
                            PatchOperation::Set(value) => {
                                let mut new_value = value.clone();
                                if let Value::Object(ref mut obj) = new_value {
                                    obj.insert("_".to_string(), Value::String(key.clone()));
                                }
                                arr[index] = new_value;
                            }
                            PatchOperation::Delete => {
                                items_to_remove.push(index);
                            }
                            PatchOperation::Edit(sub_ops) => {
                                Self::apply_operations_direct(&mut arr[index], sub_ops)?;
                            }
                            _ => {}
                        }
                    } else {
                        match operation {
                            PatchOperation::Set(value) => {
                                let mut new_item = value.clone();
                                if let Value::Object(ref mut obj) = new_item {
                                    obj.insert("_".to_string(), Value::String(key.clone()));
                                }
                                items_to_add.push(new_item);
                            }
                            PatchOperation::Edit(_) => {
                                return Err(BytemateError::InvalidSerial(key.clone()));
                            }
                            _ => {}
                        }
                    }
                }

                items_to_remove.sort_unstable_by(|a, b| b.cmp(a));
                for &index in &items_to_remove {
                    if index < arr.len() {
                        arr.remove(index);
                    }
                }

                arr.extend(items_to_add);
            }
            _ => {}
        }
        Ok(())
    }

    pub fn merge(minor_patch: Self, major_patch: Self) -> Self {
        let mut operations = HashMap::with_capacity(
            minor_patch.operations.len() + major_patch.operations.len()
        );

        for (key, op) in minor_patch.operations {
            operations.insert(key, op);
        }

        for (key, major_op) in major_patch.operations {
            match major_op {
                PatchOperation::Edit(ref major_sub_ops) => {
                    if let Some(PatchOperation::Edit(minor_sub_ops)) = operations.get(&key) {
                        let merged = Self::merge_operations_fast(minor_sub_ops, major_sub_ops);
                        operations.insert(key, PatchOperation::Edit(merged));
                    } else {
                        operations.insert(key, major_op);
                    }
                }
                _ => {
                    operations.insert(key, major_op);
                }
            }
        }

        Self { operations }
    }

    fn merge_operations_fast(
        minor_ops: &[(String, PatchOperation)],
        major_ops: &[(String, PatchOperation)]
    ) -> Vec<(String, PatchOperation)> {
        let mut result = Vec::with_capacity(minor_ops.len() + major_ops.len());
        let mut processed = HashSet::with_capacity(major_ops.len());

        for (key, major_op) in major_ops {
            processed.insert(key.as_str());

            if let Some((_, minor_op)) = minor_ops.iter().find(|(k, _)| k == key) {
                match (minor_op, major_op) {
                    (PatchOperation::Edit(minor_sub), PatchOperation::Edit(major_sub)) => {
                        let merged = Self::merge_operations_fast(minor_sub, major_sub);
                        result.push((key.clone(), PatchOperation::Edit(merged)));
                    }
                    _ => {
                        result.push((key.clone(), major_op.clone()));
                    }
                }
            } else {
                result.push((key.clone(), major_op.clone()));
            }
        }

        for (key, minor_op) in minor_ops {
            if !processed.contains(key.as_str()) {
                result.push((key.clone(), minor_op.clone()));
            }
        }

        result
    }

    #[inline]
    pub fn set(mut self, key: impl Into<String>, value: Value) -> Self {
        self.operations.insert(key.into(), PatchOperation::Set(value));
        self
    }

    #[inline]
    pub fn delete(mut self, key: impl Into<String>) -> Self {
        self.operations.insert(key.into(), PatchOperation::Delete);
        self
    }

    #[inline]
    pub fn edit(mut self, key: impl Into<String>, sub_operations: Vec<(String, PatchOperation)>) -> Self {
        self.operations.insert(key.into(), PatchOperation::Edit(sub_operations));
        self
    }

    #[inline]
    pub fn move_key(mut self, from: impl Into<String>, to: impl Into<String>) -> Self {
        self.operations.insert(
            "__move".to_string(),
            PatchOperation::Move {
                from: from.into(),
                to: to.into()
            }
        );
        self
    }

    #[inline]
    pub fn copy_key(mut self, from: impl Into<String>, to: impl Into<String>) -> Self {
        self.operations.insert(
            "__copy".to_string(),
            PatchOperation::Copy {
                from: from.into(),
                to: to.into()
            }
        );
        self
    }

    #[inline]
    pub fn test(mut self, key: impl Into<String>, expected: Value) -> Self {
        self.operations.insert(key.into(), PatchOperation::Test { expected });
        self
    }

    pub fn from_json(patch_json: &Value) -> Result<Self> {
        let mut operations = HashMap::new();

        if let Value::Object(obj) = patch_json {
            operations.reserve(obj.len());

            for (key, value) in obj {
                match value {
                    Value::Object(inner_obj) => {
                        if let Some(star_value) = inner_obj.get("*") {
                            if star_value.is_null() {
                                operations.insert(key.clone(), PatchOperation::Delete);
                            } else {
                                operations.insert(key.clone(), PatchOperation::Set(star_value.clone()));
                            }
                        } else {
                            let mut sub_ops = Vec::with_capacity(inner_obj.len());
                            for (sub_key, sub_value) in inner_obj {
                                Self::parse_nested_operation_fast(sub_key, sub_value, &mut sub_ops)?;
                            }
                            operations.insert(key.clone(), PatchOperation::Edit(sub_ops));
                        }
                    }
                    _ => {
                        operations.insert(key.clone(), PatchOperation::Set(value.clone()));
                    }
                }
            }
        }

        Ok(Self { operations })
    }

    fn parse_nested_operation_fast(key: &str, value: &Value, sub_ops: &mut Vec<(String, PatchOperation)>) -> Result<()> {
        match value {
            Value::Object(inner_obj) => {
                if let Some(star_value) = inner_obj.get("*") {
                    if star_value.is_null() {
                        sub_ops.push((key.to_string(), PatchOperation::Delete));
                    } else {
                        sub_ops.push((key.to_string(), PatchOperation::Set(star_value.clone())));
                    }
                } else {
                    let mut nested_sub_ops = Vec::with_capacity(inner_obj.len());
                    for (nested_key, nested_value) in inner_obj {
                        Self::parse_nested_operation_fast(nested_key, nested_value, &mut nested_sub_ops)?;
                    }
                    sub_ops.push((key.to_string(), PatchOperation::Edit(nested_sub_ops)));
                }
            }
            _ => {
                sub_ops.push((key.to_string(), PatchOperation::Set(value.clone())));
            }
        }
        Ok(())
    }

    pub fn to_json(&self) -> Value {
        let mut result = Map::with_capacity(self.operations.len());

        for (key, operation) in &self.operations {
            match operation {
                PatchOperation::Set(value) => {
                    result.insert(key.clone(), value.clone());
                }
                PatchOperation::Delete => {
                    let mut delete_obj = Map::with_capacity(1);
                    delete_obj.insert("*".to_string(), Value::Null);
                    result.insert(key.clone(), Value::Object(delete_obj));
                }
                PatchOperation::Edit(sub_ops) => {
                    let mut edit_obj = Map::with_capacity(sub_ops.len());
                    for (sub_key, sub_op) in sub_ops {
                        Self::serialize_operation(sub_key, sub_op, &mut edit_obj);
                    }
                    result.insert(key.clone(), Value::Object(edit_obj));
                }
                PatchOperation::Move { from, to } => {
                    let mut move_obj = Map::with_capacity(2);
                    move_obj.insert("from".to_string(), Value::String(from.clone()));
                    move_obj.insert("to".to_string(), Value::String(to.clone()));
                    result.insert(key.clone(), Value::Object(move_obj));
                }
                PatchOperation::Copy { from, to } => {
                    let mut copy_obj = Map::with_capacity(2);
                    copy_obj.insert("from".to_string(), Value::String(from.clone()));
                    copy_obj.insert("to".to_string(), Value::String(to.clone()));
                    result.insert(key.clone(), Value::Object(copy_obj));
                }
                PatchOperation::Test { expected } => {
                    let mut test_obj = Map::with_capacity(1);
                    test_obj.insert("test".to_string(), expected.clone());
                    result.insert(key.clone(), Value::Object(test_obj));
                }
            }
        }

        Value::Object(result)
    }

    fn serialize_operation(key: &str, operation: &PatchOperation, target: &mut Map<String, Value>) {
        match operation {
            PatchOperation::Set(value) => {
                target.insert(key.to_string(), value.clone());
            }
            PatchOperation::Delete => {
                let mut delete_obj = Map::with_capacity(1);
                delete_obj.insert("*".to_string(), Value::Null);
                target.insert(key.to_string(), Value::Object(delete_obj));
            }
            PatchOperation::Edit(sub_ops) => {
                let mut edit_obj = Map::with_capacity(sub_ops.len());
                for (sub_key, sub_op) in sub_ops {
                    Self::serialize_operation(sub_key, sub_op, &mut edit_obj);
                }
                target.insert(key.to_string(), Value::Object(edit_obj));
            }
            PatchOperation::Move { from, to } => {
                let mut move_obj = Map::with_capacity(2);
                move_obj.insert("from".to_string(), Value::String(from.clone()));
                move_obj.insert("to".to_string(), Value::String(to.clone()));
                target.insert(key.to_string(), Value::Object(move_obj));
            }
            PatchOperation::Copy { from, to } => {
                let mut copy_obj = Map::with_capacity(2);
                copy_obj.insert("from".to_string(), Value::String(from.clone()));
                copy_obj.insert("to".to_string(), Value::String(to.clone()));
                target.insert(key.to_string(), Value::Object(copy_obj));
            }
            PatchOperation::Test { expected } => {
                let mut test_obj = Map::with_capacity(1);
                test_obj.insert("test".to_string(), expected.clone());
                target.insert(key.to_string(), Value::Object(test_obj));
            }
        }
    }

    #[inline]
    pub fn len(&self) -> usize {
        self.operations.len()
    }

    #[inline]
    pub fn is_empty(&self) -> bool {
        self.operations.is_empty()
    }
}

impl Default for BytematePatch {
    fn default() -> Self {
        Self::new()
    }
}
