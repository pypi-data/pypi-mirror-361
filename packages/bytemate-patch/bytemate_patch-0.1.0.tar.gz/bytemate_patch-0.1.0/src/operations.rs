use serde_json::Value;

#[derive(Debug, Clone, PartialEq)]
pub enum PatchOperation {
    /// Set a value (overwrite)
    Set(Value),
    /// Delete a key
    Delete,
    /// Edit nested structure
    Edit(Vec<(String, PatchOperation)>),
    /// Move value from one key to another
    Move { from: String, to: String },
    /// Copy value from one key to another
    Copy { from: String, to: String },
    /// Test if value matches expected
    Test { expected: Value },
}

impl PatchOperation {
    pub fn is_delete(&self) -> bool {
        matches!(self, PatchOperation::Delete)
    }

    pub fn is_edit(&self) -> bool {
        matches!(self, PatchOperation::Edit(_))
    }
}
