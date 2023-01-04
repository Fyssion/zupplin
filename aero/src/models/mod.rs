use serde::{ Deserialize, Serialize };

pub mod http;
pub mod message;
pub mod room;
pub mod user;
pub mod ws;

pub use http::*;
pub use message::*;
pub use room::*;
pub use ws::*;
pub use user::*;

#[derive(Serialize, Deserialize, Debug, Clone, Eq, Hash, PartialEq)]
pub struct ID(String);

impl std::fmt::Display for ID {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.0)
    }
}
