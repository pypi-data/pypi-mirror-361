use thiserror::Error;

#[derive(Error, Debug)]
pub enum BytemateError {
    #[error("Invalid patch operation: {0}")]
    InvalidOperation(String),

    #[error("Type mismatch: expected {expected}, found {found}")]
    TypeMismatch { expected: String, found: String },

    #[error("Key '{0}' not found")]
    KeyNotFound(String),

    #[error("Invalid serial key: {0}")]
    InvalidSerial(String),

    #[error("JSON error: {0}")]
    JsonError(#[from] serde_json::Error),

    #[error("Invalid array index: {0}")]
    InvalidIndex(String),

    #[error("Recursion depth limit exceeded")]
    RecursionLimit,
}

pub type Result<T> = std::result::Result<T, BytemateError>;
