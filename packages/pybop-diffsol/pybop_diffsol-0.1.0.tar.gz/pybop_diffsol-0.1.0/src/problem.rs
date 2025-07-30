use std::sync::{Arc, Mutex};

use diffsol::{error::DiffsolError, matrix::MatrixRef, DefaultDenseMatrix, DiffSl, LinearSolver, Matrix, OdeBuilder, OdeEquations, OdeSolverProblem, Vector, VectorHost, VectorRef, Op, OdeSolverMethod, NonLinearOp};
use numpy::{ndarray::{s, Array2}, PyArray2, PyReadonlyArray1, IntoPyArray};
use pyo3::{Bound, Python};
use crate::{Config, PyDiffsolError};
#[cfg(feature = "diffsol-cranelift")]
type CG = diffsol::CraneliftJitModule;
#[cfg(feature = "diffsol-llvm")]
type CG = diffsol::LlvmModule;


pub(crate) struct Diffsol<M> 
where 
    M: Matrix<T=f64>,
    M::V: VectorHost
{
    problem: Arc<Mutex<OdeSolverProblem<DiffSl<M, CG>>>>,
}

impl<M> Diffsol<M> 
where
    M: Matrix<T=f64>,
    M::V: VectorHost + DefaultDenseMatrix,
    for<'b> &'b M::V: VectorRef<M::V>,
    for<'b> &'b M: MatrixRef<M>,
{
    pub(crate) fn new(code: &str, config: &Config) -> Result<Self, PyDiffsolError> {
        let problem = OdeBuilder::<M>::new()
            .rtol(config.rtol)
            .atol([config.atol])
            .build_from_diffsl(code)?;
        Ok(Self { problem: Arc::new(Mutex::new(problem)) })
    }

    pub(crate) fn set_params<'py>(&mut self, params: PyReadonlyArray1<'py, f64>) -> Result<(), PyDiffsolError> {
        let mut problem = self.problem.lock().map_err(|e| PyDiffsolError::new(DiffsolError::Other(e.to_string())))?;
        let params = params.as_array();
        let fparams = M::V::from_slice(params.as_slice().unwrap(), problem.context().clone());
        problem.eqn.set_params(&fparams);
        Ok(())
    }

    pub(crate) fn solve<'py, LS: LinearSolver<M>>(&mut self, py: Python<'py>, times: PyReadonlyArray1<'py, f64>) -> Result<Bound<'py, PyArray2<f64>>, PyDiffsolError> {
        let problem = self.problem.lock().map_err(|e| PyDiffsolError::new(DiffsolError::Other(e.to_string())))?;
        let times = times.as_array();
        let mut solver = problem.bdf::<LS>()?;
        let nout = if let Some(_out) = problem.eqn.out() {
            problem.eqn.nout()
        } else {
            problem.eqn.nstates()
        };
        let mut sol = Array2::zeros((nout, times.len())); 
        for (i, &t) in times.iter().enumerate() {
            while solver.state().t < t {
                solver.step()?;
            }
            let y = solver.interpolate(t)?;
            let out = if let Some(out) = problem.eqn.out() {
                out.call(&y, t)
            } else {
                y
            };
            sol.slice_mut(s![.., i]).iter_mut().zip(out.as_slice().iter()).for_each(|(a, b)| *a = *b);
        }
        Ok(sol.into_pyarray(py))
    }
}