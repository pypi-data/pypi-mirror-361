use std::sync::Arc;

use futures_util::{
    stream::{BoxStream, Fuse},
    StreamExt,
};
use pyo3::{
    exceptions::{PyStopAsyncIteration, PyStopIteration},
    PyResult,
};
use tokio::sync::Mutex;

pub type PyStream<T, E> = Fuse<BoxStream<'static, Result<T, E>>>;

pub async fn next_stream<T, E>(stream: Arc<Mutex<PyStream<T, E>>>, sync: bool) -> PyResult<T>
where
    E: std::error::Error,
{
    let mut stream = stream.lock().await;
    match stream.next().await {
        Some(item) => match item {
            Ok(itm) => Ok(itm),
            Err(e) => {
                println!("Error: {:?}", e);
                match sync {
                    true => Err(PyStopIteration::new_err(e.to_string())),
                    false => Err(PyStopAsyncIteration::new_err(e.to_string())),
                }
            }
        },
        None => match sync {
            true => Err(PyStopIteration::new_err("Stream exhausted")),
            false => Err(PyStopAsyncIteration::new_err("Stream exhausted")),
        },
    }
}
