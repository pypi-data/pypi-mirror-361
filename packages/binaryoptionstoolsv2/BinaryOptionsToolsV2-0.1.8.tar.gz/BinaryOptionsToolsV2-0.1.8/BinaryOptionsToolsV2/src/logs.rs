use std::{fs::OpenOptions, io::Write, sync::Arc};

use binary_options_tools::{
    error::BinaryOptionsResult,
    stream::{stream_logs_layer, RecieverStream},
};
use chrono::Duration;
use futures_util::{
    stream::{BoxStream, Fuse},
    StreamExt,
};
use pyo3::{pyclass, pyfunction, pymethods, Bound, Py, PyAny, PyResult, Python};
use pyo3_async_runtimes::tokio::future_into_py;
use tokio::sync::Mutex;
use tracing::{debug, instrument, level_filters::LevelFilter, warn, Level};
use tracing_subscriber::{
    fmt::{self, MakeWriter},
    layer::SubscriberExt,
    util::SubscriberInitExt,
    Layer, Registry,
};

use crate::{error::BinaryErrorPy, runtime::get_runtime, stream::next_stream};

const TARGET: &str = "Python";

#[pyfunction]
pub fn start_tracing(
    path: String,
    level: String,
    terminal: bool,
    layers: Vec<StreamLogsLayer>,
) -> PyResult<()> {
    let level: LevelFilter = level.parse().unwrap_or(Level::DEBUG.into());
    let error_logs = OpenOptions::new()
        .append(true)
        .create(true)
        .open(format!("{}/error.log", &path))?;
    let logs = OpenOptions::new()
        .append(true)
        .create(true)
        .open(format!("{}/logs.log", &path))?;
    let default = fmt::Layer::default().with_writer(NoneWriter).boxed();
    let mut layers = layers
        .into_iter()
        .flat_map(|l| Arc::try_unwrap(l.layer))
        .collect::<Vec<Box<dyn Layer<Registry> + Send + Sync>>>();
    layers.push(default);
    println!("Length of layers: {}", layers.len());
    let subscriber = tracing_subscriber::registry()
        // .with(filtered_layer)
        .with(layers)
        .with(
            // log-error file, to log the errors that arise
            fmt::layer()
                .with_ansi(false)
                .with_writer(error_logs)
                .with_filter(LevelFilter::WARN),
        )
        .with(
            // log-debug file, to log the debug
            fmt::layer()
                .with_ansi(false)
                .with_writer(logs)
                .with_filter(level),
        );

    if terminal {
        subscriber
            .with(fmt::Layer::default().with_filter(level))
            .init();
    } else {
        subscriber.init()
    }

    Ok(())
}

#[pyclass]
#[derive(Clone)]
pub struct StreamLogsLayer {
    layer: Arc<Box<dyn Layer<Registry> + Send + Sync>>,
}

struct NoneWriter;

impl Write for NoneWriter {
    fn write(&mut self, buf: &[u8]) -> std::io::Result<usize> {
        Ok(buf.len())
    }

    fn flush(&mut self) -> std::io::Result<()> {
        Ok(())
    }
}

impl<'a> MakeWriter<'a> for NoneWriter {
    type Writer = NoneWriter;
    fn make_writer(&'a self) -> Self::Writer {
        NoneWriter
    }
}

type LogStream = Fuse<BoxStream<'static, BinaryOptionsResult<String>>>;

#[pyclass]
pub struct StreamLogsIterator {
    stream: Arc<Mutex<LogStream>>,
}

#[pymethods]
impl StreamLogsIterator {
    fn __aiter__(slf: Py<Self>) -> Py<Self> {
        slf
    }

    fn __iter__(slf: Py<Self>) -> Py<Self> {
        slf
    }

    fn __anext__<'py>(&'py mut self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let stream = self.stream.clone();
        future_into_py(py, next_stream(stream, false))
    }

    fn __next__<'py>(&'py self, py: Python<'py>) -> PyResult<String> {
        let runtime = get_runtime(py)?;
        let stream = self.stream.clone();
        runtime.block_on(next_stream(stream, true))
    }
}

#[pyclass]
#[derive(Default)]
pub struct LogBuilder {
    layers: Vec<Box<dyn Layer<Registry> + Send + Sync>>,
    build: bool,
}

#[pymethods]
impl LogBuilder {
    #[new]
    pub fn new() -> Self {
        Self::default()
    }

    #[pyo3(signature = (level = "DEBUG".to_string(), timeout = None))]
    pub fn create_logs_iterator(
        &mut self,
        level: String,
        timeout: Option<Duration>,
    ) -> StreamLogsIterator {
        let timeout = match timeout {
            Some(timeout) => match timeout.to_std() {
                Ok(timeout) => Some(timeout),
                Err(e) => {
                    warn!("Error converting duration to std, {e}");
                    None
                }
            },
            None => None,
        };
        let (layer, inner_iter) =
            stream_logs_layer(level.parse().unwrap_or(Level::DEBUG.into()), timeout);
        let stream = RecieverStream::to_stream_static(Arc::new(inner_iter))
            .boxed()
            .fuse();
        let iter = StreamLogsIterator {
            stream: Arc::new(Mutex::new(stream)),
        };
        self.layers.push(layer);
        iter
    }

    #[pyo3(signature = (path = "logs.log".to_string(), level = "DEBUG".to_string()))]
    pub fn log_file(&mut self, path: String, level: String) -> PyResult<()> {
        let logs = OpenOptions::new().append(true).create(true).open(path)?;
        let layer = fmt::layer()
            .with_ansi(false)
            .with_writer(logs)
            .with_filter(level.parse().unwrap_or(LevelFilter::DEBUG))
            .boxed();
        self.layers.push(layer);
        Ok(())
    }

    #[pyo3(signature = (level = "DEBUG".to_string()))]
    pub fn terminal(&mut self, level: String) {
        let layer = fmt::Layer::default()
            .with_filter(level.parse().unwrap_or(LevelFilter::DEBUG))
            .boxed();
        self.layers.push(layer);
    }

    pub fn build(&mut self) -> PyResult<()> {
        if self.build {
            return Err(BinaryErrorPy::NotAllowed(
                "Builder has already been built, cannot be called again".to_string(),
            )
            .into());
        }
        self.build = true;
        let default = fmt::Layer::default().with_writer(NoneWriter).boxed();
        self.layers.push(default);
        let layers = self
            .layers
            .drain(..)
            .collect::<Vec<Box<dyn Layer<Registry> + Send + Sync>>>();
        tracing_subscriber::registry().with(layers).init();
        Ok(())
    }
}

#[pyclass]
#[derive(Default)]
pub struct Logger;

#[pymethods]
impl Logger {
    #[new]
    pub fn new() -> Self {
        Self
    }

    #[instrument(target = TARGET, skip(self, message))] // Use instrument for better tracing
    pub fn debug(&self, message: String) {
        debug!(message);
    }

    #[instrument(target = TARGET, skip(self, message))]
    pub fn info(&self, message: String) {
        tracing::info!(message);
    }

    #[instrument(target = TARGET, skip(self, message))]
    pub fn warn(&self, message: String) {
        tracing::warn!(message);
    }

    #[instrument(target = TARGET, skip(self, message))]
    pub fn error(&self, message: String) {
        tracing::error!(message);
    }
}

#[cfg(test)]
mod tests {
    use std::time::Duration;

    use futures_util::future::join;
    use serde_json::Value;
    use tracing::{error, info, trace, warn};

    use super::*;

    #[test]
    fn test_start_tracing() {
        start_tracing(".".to_string(), "DEBUG".to_string(), true, vec![]).unwrap();

        info!("Test")
    }

    fn create_logs_iterator_test(level: String) -> (StreamLogsLayer, StreamLogsIterator) {
        let (inner_layer, inner_iter) =
            stream_logs_layer(level.parse().unwrap_or(Level::DEBUG.into()), None);
        let layer = StreamLogsLayer {
            layer: Arc::new(inner_layer),
        };
        let stream = RecieverStream::to_stream_static(Arc::new(inner_iter))
            .boxed()
            .fuse();
        let iter = StreamLogsIterator {
            stream: Arc::new(Mutex::new(stream)),
        };
        (layer, iter)
    }

    #[tokio::test]
    async fn test_start_tracing_stream() {
        let (layer, receiver) = create_logs_iterator_test("ERROR".to_string());
        start_tracing(".".to_string(), "DEBUG".to_string(), false, vec![layer]).unwrap();

        async fn log() {
            let mut num = 0;
            loop {
                tokio::time::sleep(Duration::from_secs(1)).await;
                num += 1;
                trace!(num, "Test trace");
                debug!(num, "Test debug");
                info!(num, "Test info");
                warn!(num, "Test warning");
                error!(num, "Test error");
            }
        }

        async fn reciever_fn(reciever: StreamLogsIterator) {
            let mut stream = reciever.stream.lock().await;

            // stream.next().await;
            while let Some(Ok(value)) = stream.next().await {
                let value: Value = serde_json::from_str(&format!("{:?}", value)).unwrap();
                println!("{}", value);
            }
        }

        join(log(), reciever_fn(receiver)).await;
    }
}
