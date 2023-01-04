use crate::prelude::*;

// #[derive(Serialize, Deserialize, Debug, Clone)]
// pub enum RoomType {
//     #[serde(rename = "0")]
//     Group,
//     #[serde(rename = "1")]
//     Direct,
// }

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct RoomMe {
    pub permission_level: u32,  // TODO
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct Room {
    pub id: models::ID,
    pub name: String,
    pub description: String,
    pub owner_id: models::ID,
    #[serde(rename = "type")]
    pub room_type: u8,
    pub me: RoomMe,
    pub last_message: Option<models::Message>,
}
