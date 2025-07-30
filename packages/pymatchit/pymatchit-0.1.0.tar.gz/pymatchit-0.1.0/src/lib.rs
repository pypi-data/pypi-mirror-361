
#![allow(non_local_definitions)]

use std::sync::{Arc, RwLock};

use matchit::Router;
use pyo3::exceptions::{PyValueError};
use pyo3::prelude::*;
use pyo3::types::*;

/// matchit.Router python binding
#[pyclass(generic)]
pub struct PyRouter {
    inner: Arc<RwLock<Router<Py<PyAny>>>>,
}

#[pymethods]
impl PyRouter {

    #[new]
    fn new() -> Self {
        Self {
            inner: Arc::new(RwLock::new(Router::new())),
        }
    }

    /// Insert a new route.
    ///
    /// Wildcard routes are supported via `{*name}` (e.g. `"/static/{*path}"`).
    /// Returns `None` on success; raises `ValueError` on conflict.
    fn insert(&self, _py: Python, path: &str, value: PyObject) -> PyResult<()> {
        let mut router = self.inner.write().expect("router poisoned");
        router
            .insert(path, value)
            .map_err(|err| PyValueError::new_err(format!("unable to add route (error: {err})")))
    }

    /// Match an incoming `path`. Returns `Some((handler, params))` on success;
    /// returns `None` otherwise.
    fn at(&self, py: Python, path: &str) -> PyResult<Option<(PyObject, PyObject)>> {
        let router = self.inner.read().expect("router poisoned");
        let matched = match router.at(path) {
            Ok(m) => m,
            Err(_) => return Ok(None),
        };

        let handler = matched.value.clone_ref(py);
        let params = PyDict::new(py);
        for (k, v) in matched.params.iter() {
            params.set_item(k, v)?;
        }
        Ok(Some((handler.into(), params.into())))
    }

    /// Remove a specific route by path.
    /// Returns `True` if the route was found and removed, `False` otherwise.
    fn remove(&self, path: &str) -> PyResult<bool> {
        let mut router = self.inner.write().expect("router poisoned");
        match router.remove(path) {
            Some(_) => Ok(true),
            None => Ok(false),
        }
    }

    /// Remove all routes.
    fn clear(&self) {
        let mut router = self.inner.write().expect("router poisoned");
        *router = Router::new();
    }

    /// String representation.
    fn __repr__(slf: &Bound<'_, Self>) -> PyResult<String> {
        // This is the equivalent of `self.__class__.__name__` in Python.
        let class_name: Bound<'_, PyString> = slf.get_type().qualname()?;
        Ok(format!("{}()", class_name))
    }
}

#[pymodule]
fn pymatchit(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyRouter>()?;
    Ok(())
}
