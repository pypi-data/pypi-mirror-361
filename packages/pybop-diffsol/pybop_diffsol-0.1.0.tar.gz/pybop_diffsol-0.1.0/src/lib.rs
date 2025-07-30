pub(crate) mod error;
pub(crate) mod config;
pub(crate) mod problem;

pub(crate) use config::Config;
pub(crate) use error::PyDiffsolError;
pub(crate) use problem::Diffsol;

use numpy::{PyArray2, PyReadonlyArray1};
use pyo3::prelude::*;

macro_rules! create_diffsol_class {
    ($name:ident, $matrix:ty, $linear_solver:ty) => {
        #[pyclass]
        pub(crate) struct $name(Diffsol<$matrix>);

        #[pymethods]
        impl $name {
            #[new]
            fn new(code: &str, config: &Config) -> Result<Self, PyDiffsolError> {
                let inner = Diffsol::new(code, config)?;
                Ok(Self(inner))
            }

            #[pyo3(signature = (params))]
            fn set_params<'py>(&mut self, params: PyReadonlyArray1<'py, f64>) -> Result<(), PyDiffsolError> {
                self.0.set_params(params)
            }

            #[pyo3(signature = (times))]
            fn solve<'py>(&mut self, py: Python<'py>, times: PyReadonlyArray1<'py, f64>) -> Result<Bound<'py, PyArray2<f64>>, PyDiffsolError> {
                Diffsol::solve::<$linear_solver>(&mut self.0, py, times)
            }
        }
        
    };
}

create_diffsol_class!(DiffsolDense, diffsol::NalgebraMat<f64>, diffsol::NalgebraLU<f64>);
create_diffsol_class!(DiffsolSparse, diffsol::FaerSparseMat<f64>, diffsol::FaerSparseLU<f64>);


#[pymodule]
fn pybop_diffsol(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<DiffsolDense>()?;
    m.add_class::<DiffsolSparse>()?;
    m.add_class::<Config>()?;
    Ok(())
}
