use crate::prelude::*;

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct User {
    id: models::ID,
    username: Option<String>,
    name: String,
}
