use std::fs;
use pyo3::prelude::*;
extern crate glob;
use glob::glob;
extern crate walkdir;
use walkdir::WalkDir;


fn _filesize(path: String) -> usize {
    let x = match fs::read(path) {
        Ok(val) => val,
        Err(err) => return 0,
    };

    return x.len();
}


#[pyfunction]
fn file_get(path: String) -> PyResult<Vec<u8>> {
    let empty: Vec<u8> = Vec::new();
    let x = match fs::read(path) {
        Ok(val) => val,
        Err(err) => return Ok(empty),
    };
    return Ok(x);
}


#[pyfunction]
fn file_search(path: String, pattern: String) -> PyResult<Vec<Vec<usize>>> {
    let empty: Vec<Vec<usize>> = Vec::new();
    let content = match fs::read_to_string(path) {
        Ok(val)  => val,
        Err(err) => return Ok(empty),
    };
    let re = Regex::new(&pattern).unwrap();
    let m = re.find_iter(&content);
    let mut rast: Vec<Vec<usize>> = Vec::new();
    for i in m {
        let mut obj: Vec<usize> = Vec::new();
        obj.push(i.start());
        obj.push(i.end());

        rast.push(obj)
    }

    return Ok(rast);
}

#[pyfunction]
fn rec_ld(path: String) -> PyResult<Vec<String>> {
    let mut ret: Vec<String> = Vec::new();
    for e in WalkDir::new(path).into_iter().filter_map(|e| e.ok()) {
        if e.metadata().unwrap().is_file() {
            ret.push(e.path().to_str().unwrap().to_string());
        }
    }
    return Ok(ret);
}

#[pyclass]
struct rec_path_ret_val {
    #[pyo3(get)]
    name: String,
    #[pyo3(get)]
    amount: usize
}

#[pyfunction]
fn rec_path_search(path: String, pattern: String) -> PyResult<Vec<rec_path_ret_val>> {
    let mut ret: Vec<rec_path_ret_val> = Vec::new();
    let mut single_path: String;
    let mut empty: Vec<rec_path_ret_val> = Vec::new();
    empty.push(rec_path_ret_val {name: "err".to_string(), amount: usize::MAX});
    for e in WalkDir::new(path).into_iter().filter_map(|e| e.ok()) {
        if e.metadata().unwrap().is_file() {
            single_path = e.path().to_str().unwrap().to_string();
            let content = match fs::read_to_string(single_path.clone()) {
                Ok(val)  => val,
                Err(err) => continue,
            };
            let re = Regex::new(&pattern).unwrap();
            let m: usize = re.find_iter(&content).count();
            ret.push(rec_path_ret_val { name: single_path.to_string(), amount: m})
        }
    }
    return Ok(ret)
}

#[pyfunction]
fn rec_size(path: String) -> PyResult<usize> {
    let mut ret: usize = 0;
    for e in WalkDir::new(path).into_iter().filter_map(|e| e.ok()) {
        if e.metadata().unwrap().is_file() {
            ret += _filesize(e.path().to_str().unwrap().to_string());
        }
    }
    return Ok(ret);
}

#[pyfunction]
fn version() -> PyResult<String> {
    Ok("0.2.5".to_string())
}

#[pymodule]
fn ntllib(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(file_search, m)?)?;
    m.add_function(wrap_pyfunction!(version, m)?)?;
    m.add_function(wrap_pyfunction!(rec_ld, m)?)?;
    m.add_function(wrap_pyfunction!(rec_path_search, m)?)?;
    m.add_function(wrap_pyfunction!(file_get, m)?)?;
    m.add_function(wrap_pyfunction!(rec_size, m)?)?;
    Ok(())
}

fn main() {}