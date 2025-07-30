use pyo3::prelude::*;

// Declare submodules for different linear regression models
// pub mod linear;
// pub mod ridge;

// Example function that would be in this module
#[pyfunction]
pub fn linear_regression_fit(a: usize, b: usize) -> PyResult<String> {
    // Placeholder implementation
    Ok((a + b).to_string())
}

// Register all linear regression related functions
pub fn register_linreg(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(linear_regression_fit, m)?)?;
    
    // Register functions from submodules
    // linear::register_linear(m)?;
    // ridge::register_ridge(m)?;
    
    Ok(())
}