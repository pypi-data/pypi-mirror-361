use pyo3::prelude::*;
mod interpreter;
use interpreter::UiuaInterpreter;

#[pymodule]
fn lib(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<UiuaInterpreter>()?;
    Ok(())
}
