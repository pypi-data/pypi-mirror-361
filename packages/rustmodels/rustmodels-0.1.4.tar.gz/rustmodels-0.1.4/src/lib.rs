use pyo3::prelude::*;

// Declare the models module
mod models;

/// A Python module implemented in Rust.
#[pymodule]
fn rustmodels(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Register all functions from the models module
    models::register_models(m)?;
    Ok(())
}
