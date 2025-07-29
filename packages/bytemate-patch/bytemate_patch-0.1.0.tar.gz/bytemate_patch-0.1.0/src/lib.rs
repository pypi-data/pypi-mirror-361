//! # BYTEMATE:PATCH
//!
//! The JSON patching library that doesn't suck.

pub mod error;
pub mod patch;
pub mod operations;

#[cfg(feature = "python")]
pub mod python;

#[cfg(feature = "wasm")]
pub mod wasm;

pub use error::{BytemateError, Result};
pub use patch::BytematePatch;
pub use operations::PatchOperation;

#[cfg(feature = "python")]
pub use python::*;

#[cfg(feature = "wasm")]
pub use wasm::*;

pub const VERSION: &str = env!("CARGO_PKG_VERSION");
pub const MEDIA_TYPE: &str = "application/bytemate-patch+json";
