use pyo3::prelude::*;
use pyo3::types::{PyList, PyDict};
use crate::BytematePatch;
use serde_json::Value;

/// Convert Python object to serde_json::Value
fn py_to_json(obj: &Bound<'_, PyAny>) -> PyResult<Value> {
    if obj.is_none() {
        Ok(Value::Null)
    } else if let Ok(b) = obj.extract::<bool>() {
        Ok(Value::Bool(b))
    } else if let Ok(i) = obj.extract::<i64>() {
        Ok(Value::Number(i.into()))
    } else if let Ok(f) = obj.extract::<f64>() {
        Ok(Value::Number(serde_json::Number::from_f64(f).unwrap_or(0.into())))
    } else if let Ok(s) = obj.extract::<String>() {
        Ok(Value::String(s))
    } else if let Ok(list) = obj.downcast::<PyList>() {
        let mut vec = Vec::new();
        for item in list.iter() {
            vec.push(py_to_json(&item)?);
        }
        Ok(Value::Array(vec))
    } else if let Ok(dict) = obj.downcast::<PyDict>() {
        let mut map = serde_json::Map::new();
        for (key, value) in dict.iter() {
            let key_str = key.extract::<String>()?;
            map.insert(key_str, py_to_json(&value)?);
        }
        Ok(Value::Object(map))
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
            "Unsupported type for JSON conversion"
        ))
    }
}

/// Convert serde_json::Value to Python object
fn json_to_py(py: Python, value: &Value) -> PyResult<PyObject> {
    match value {
        Value::Null => Ok(py.None()),
        Value::Bool(b) => Ok((*b).into_pyobject(py)?.as_any().clone().unbind()),
        Value::Number(n) => {
            if let Some(i) = n.as_i64() {
                Ok(i.into_pyobject(py)?.as_any().clone().unbind())
            } else if let Some(f) = n.as_f64() {
                Ok(f.into_pyobject(py)?.as_any().clone().unbind())
            } else {
                Ok(py.None())
            }
        }
        Value::String(s) => Ok(s.into_pyobject(py)?.as_any().clone().unbind()),
        Value::Array(arr) => {
            let py_list = PyList::empty(py);
            for item in arr {
                py_list.append(json_to_py(py, item)?)?;
            }
            Ok(py_list.as_any().clone().unbind())
        }
        Value::Object(obj) => {
            let py_dict = PyDict::new(py);
            for (key, value) in obj {
                py_dict.set_item(key, json_to_py(py, value)?)?;
            }
            Ok(py_dict.as_any().clone().unbind())
        }
    }
}


#[pyclass(name = "BytematePatch")]
pub struct PyBytematePatch {
    inner: BytematePatch,
}

#[pymethods]
impl PyBytematePatch {
    #[new]
    fn new() -> Self {
        Self {
            inner: BytematePatch::new(),
        }
    }

    fn set(&mut self, key: &str, value: Bound<'_, PyAny>) -> PyResult<()> {
        let json_value = py_to_json(&value)?;
        self.inner = self.inner.clone().set(key, json_value);
        Ok(())
    }

    fn delete(&mut self, key: &str) -> PyResult<()> {
        self.inner = self.inner.clone().delete(key);
        Ok(())
    }

    fn apply(&self, data: Bound<'_, PyAny>) -> PyResult<PyObject> {
        let json_data = py_to_json(&data)?;

        match self.inner.apply(&json_data) {
            Ok(result) => {
                Python::with_gil(|py| json_to_py(py, &result))
            }
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                format!("Patch error: {}", e)
            ))
        }
    }

    fn apply_inplace(&self, data: Bound<'_, PyAny>) -> PyResult<()> {
        let mut json_data = py_to_json(&data)?;

        match self.inner.apply_inplace(&mut json_data) {
            Ok(()) => Ok(()),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                format!("Patch error: {}", e)
            ))
        }
    }

    #[staticmethod]
    fn from_json(data: Bound<'_, PyAny>) -> PyResult<Self> {
        let json_data = py_to_json(&data)?;

        match BytematePatch::from_json(&json_data) {
            Ok(patch) => Ok(Self { inner: patch }),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                format!("Parse error: {}", e)
            ))
        }
    }

    fn to_json(&self) -> PyResult<PyObject> {
        let json_result = self.inner.to_json();
        Python::with_gil(|py| json_to_py(py, &json_result))
    }

    #[staticmethod]
    fn merge(minor: &PyBytematePatch, major: &PyBytematePatch) -> Self {
        let merged = BytematePatch::merge(minor.inner.clone(), major.inner.clone());
        Self { inner: merged }
    }
    
    fn __len__(&self) -> usize {
        self.inner.len()
    }

    fn __bool__(&self) -> bool {
        !self.inner.is_empty()
    }
}

#[pymodule]
fn bytemate_patch(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyBytematePatch>()?;
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    Ok(())
}
