use crate::prelude::*;

#[derive(Serialize, Deserialize, Debug, Clone)]
pub enum MessageType {
    #[serde(rename = "0")]
    Standard
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct Message {
    pub id: models::ID,
    pub content: String,
    pub room_id: models::ID,
    pub author: models::User,
    #[serde(rename = "type")]
    pub message_type: MessageType,
}
