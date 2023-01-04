use crate::prelude::*;

#[derive(Serialize, Deserialize, Debug, Clone)]
#[serde(tag = "event_name", content = "data")]
pub enum WsDispatch {
    MessageCreate {
        #[serde(flatten)]
        message: models::Message
    },
    RoomJoin {
        #[serde(flatten)]
        room: models::Room
    },
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct WsHello {
    pub heartbeat_interval: u64,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
#[serde(tag = "opcode")]
pub enum WsIncomingMessage {
    #[serde(rename = "0")]
    WsDispatch(WsDispatch),
    #[serde(rename = "2")]
    HeartbeatAck,
    #[serde(rename = "4")]
    Hello {
        data: WsHello
    },
}

#[derive(Serialize, Deserialize, Debug, Clone)]
#[serde(tag = "opcode", content = "data")]
pub enum WsOutgoingMessage {
    #[serde(rename = "1")]
    Heartbeat,
    #[serde(rename = "3")]
    Identify {
        token: String,
    }

}
