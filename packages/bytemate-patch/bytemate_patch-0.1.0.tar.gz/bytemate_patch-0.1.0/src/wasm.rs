use wasm_bindgen::prelude::*;
use crate::BytematePatch;
use serde_json::Value;

#[wasm_bindgen]
extern "C" {
    #[wasm_bindgen(js_namespace = console)]
    fn log(s: &str);
}

macro_rules! console_log {
    ($($t:tt)*) => (log(&format_args!($($t)*).to_string()))
}

#[wasm_bindgen]
pub struct JsBytematePatch {
    inner: BytematePatch,
}

#[wasm_bindgen]
impl JsBytematePatch {
    #[wasm_bindgen(constructor)]
    pub fn new() -> JsBytematePatch {
        JsBytematePatch {
            inner: BytematePatch::new(),
        }
    }

    #[wasm_bindgen]
    pub fn set(&mut self, key: &str, value: &JsValue) -> Result<(), JsValue> {
        let json_value: Value = serde_wasm_bindgen::from_value(value.clone())
            .map_err(|e| JsValue::from_str(&format!("Failed to convert value: {}", e)))?;

        self.inner = self.inner.clone().set(key, json_value);
        Ok(())
    }
    
    #[wasm_bindgen]
    pub fn delete(&mut self, key: &str) {
        self.inner = self.inner.clone().delete(key);
    }

    #[wasm_bindgen]
    pub fn apply(&self, data: &JsValue) -> Result<JsValue, JsValue> {
        let json_data: Value = serde_wasm_bindgen::from_value(data.clone())
            .map_err(|e| JsValue::from_str(&format!("Failed to parse input: {}", e)))?;

        let result = self.inner.apply(&json_data)
            .map_err(|e| JsValue::from_str(&format!("Patch error: {}", e)))?;

        let json_string = result.to_string();
        js_sys::JSON::parse(&json_string)
            .map_err(|e| JsValue::from_str("Failed to parse result as JSON"))
    }

    #[wasm_bindgen(js_name = fromJson)]
    pub fn from_json(data: &JsValue) -> Result<JsBytematePatch, JsValue> {
        let json_data: Value = serde_wasm_bindgen::from_value(data.clone())
            .map_err(|e| JsValue::from_str(&format!("Failed to parse JSON: {}", e)))?;

        let patch = BytematePatch::from_json(&json_data)
            .map_err(|e| JsValue::from_str(&format!("Parse error: {}", e)))?;

        Ok(JsBytematePatch { inner: patch })
    }

    #[wasm_bindgen(js_name = toJson)]
    pub fn to_json(&self) -> Result<JsValue, JsValue> {
        let json_result = self.inner.to_json();
        serde_wasm_bindgen::to_value(&json_result)
            .map_err(|e| JsValue::from_str(&format!("Failed to convert to JSON: {}", e)))
    }

    #[wasm_bindgen]
    pub fn merge(minor: &JsBytematePatch, major: &JsBytematePatch) -> JsBytematePatch {
        let merged = BytematePatch::merge(minor.inner.clone(), major.inner.clone());
        JsBytematePatch { inner: merged }
    }

    #[wasm_bindgen(getter)]
    pub fn length(&self) -> usize {
        self.inner.len()
    }

    #[wasm_bindgen(js_name = isEmpty)]
    pub fn is_empty(&self) -> bool {
        self.inner.is_empty()
    }
}

// Export version
#[wasm_bindgen]
pub fn version() -> String {
    env!("CARGO_PKG_VERSION").to_string()
}
