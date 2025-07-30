use std::time::Duration;

use binary_options_tools_core_pre::error::CoreError;
use uuid::Uuid;

use crate::pocketoption_pre::modules::subscriptions::SubscriptionError;

#[derive(thiserror::Error, Debug)]
pub enum PocketError {
    #[error("Failed to join task: {0}")]
    Core(#[from] Box<CoreError>),
    #[error("State builder error, {0}")]
    StateBuilder(String),
    #[error("Invalid asset: {0}")]
    InvalidAsset(String),

    /// Error opening order.
    #[error("Failed to open order: {error}, amount: {amount}, asset: {asset}")]
    FailOpenOrder {
        error: String,
        amount: f64,
        asset: String,
    },

    /// Error finding deal.
    #[error("Failed to find deal: {0}")]
    DealNotFound(Uuid),

    /// Timeout error.
    #[error("Timeout error: {task} in {context} after {duration:?}")]
    Timeout {
        task: String, // The task that timed out, eg "check-results",
        context: String,
        duration: Duration,
    },

    #[error("General error: {0}")]
    General(String),

    #[error("Subscription error: {0}")]
    Subscription(#[from] SubscriptionError),
}

pub type PocketResult<T> = Result<T, PocketError>;

impl From<CoreError> for PocketError {
    fn from(err: CoreError) -> Self {
        PocketError::Core(Box::new(err))
    }
}
