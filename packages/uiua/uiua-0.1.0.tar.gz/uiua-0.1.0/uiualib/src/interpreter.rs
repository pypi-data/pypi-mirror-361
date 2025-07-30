use pyo3::prelude::*;
use rayon::prelude::*;
use uiua::{Primitive, Uiua};

#[pyclass]
#[derive(Clone, Debug)]
pub struct UiuaPrimitive {
    #[pyo3(get)]
    glyph: Option<char>,
    #[pyo3(get)]
    name: &'static str,
    #[pyo3(get)]
    num_arguments: Option<usize>,
    #[pyo3(get)]
    num_outputs: Option<usize>,
    #[pyo3(get)]
    aliases: &'static [&'static str],
}

#[pymethods]
impl UiuaPrimitive {
    fn __str__(&self) -> String {
        format!("{self:#?}")
    }
}

#[pyclass]
pub struct UiuaInterpreter {
    #[pyo3(get)]
    primitives: Vec<UiuaPrimitive>,
}

#[pymethods]
impl UiuaInterpreter {
    #[new]
    fn new() -> Self {
        let primitives = Primitive::all()
            .map(|p| UiuaPrimitive {
                glyph: p.glyph(),
                name: p.name(),
                num_arguments: p.args(),
                num_outputs: p.outputs(),
                aliases: p.aliases(),
            })
            .collect::<Vec<_>>();
        Self { primitives }
    }

    fn eval(&self, code: &str) -> PyResult<String> {
        let _ = self;
        let mut uiua = Uiua::with_safe_sys();

        match uiua.run_str(code) {
            Ok(_) => {
                let stack = uiua.take_stack();
                Ok(stack
                    .iter()
                    .rev()
                    .map(uiua::Value::representation)
                    .collect::<Vec<_>>()
                    .join(" "))
            }
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Uiua execution error: {e}"
            ))),
        }
    }

    #[allow(clippy::needless_pass_by_value)]
    fn eval_multi(&self, codes: Vec<String>) -> Vec<Option<String>> {
        codes.par_iter().map(|code| self.eval(code).ok()).collect()
    }
}
