use futures::{StreamExt};
use futures::{join, SinkExt};
use std::{rc::Rc, time::Duration};
use async_std::sync::RwLock;
use async_std::task::sleep;
use ws_stream_wasm::{WsMeta, WsMessage};

use crate::prelude::*;

pub async fn websocket(
    token: String,
    me: Option<models::User>,
    set_me: Rc<dyn Fn(Option<models::User>)>,
    mut rooms: RoomsState,
    set_rooms: Rc<dyn Fn(RoomsState)>,
    mut messages: MessagesState,
    set_messages: Rc<dyn Fn(MessagesState)>,
) {
    log::info!("Connecting to WS");
    let (_ws_meta, ws) = WsMeta::connect("ws://localhost:4000/websocket/connect", None).await.unwrap();

    let ws = Rc::new(RwLock::new(ws));
    let heartbeat_ws = ws.clone();

    let heartbeat_task = async move {
        loop {
            log::info!("Sending heartbeat");
            let heartbeat_message= WsMessage::Text(serde_json::to_string(&models::WsOutgoingMessage::Heartbeat).unwrap());
            let mut actual_ws = heartbeat_ws.write().await;
            actual_ws.send(heartbeat_message).await.unwrap();
            sleep(Duration::from_millis(60000)).await;
        }
    };

    let polling_task = async move {
        let identify_message = serde_json::to_string(&models::WsOutgoingMessage::Identify { token: (token.clone()) }).unwrap();
        log::info!("Sending IDENTIFY: {}", identify_message);
        ws.write().await.send(WsMessage::Text(identify_message)).await.unwrap();

        log::info!("Starting to poll WS");

        while let Some(WsMessage::Text(raw_message)) = ws.write().await.next().await {
            log::info!("Got msg {}", raw_message);
            match serde_json::from_str::<models::WsIncomingMessage>(&raw_message).unwrap() {
                // WsIncomingMessage::Hello { data } => {
                //     log::info!("Got heartbeat {}", data.heartbeat_interval);
                //     // heartbeat_tx.send(data.heartbeat_interval).unwrap();
                // }
                models::WsIncomingMessage::HeartbeatAck => {}
                models::WsIncomingMessage::WsDispatch(event) => {
                    match event {
                        models::WsDispatch::MessageCreate { message } => {
                            log::info!("Received MessageCreate");
                            messages.entry(message.clone().id).or_default().insert(message.clone().id, message.clone());
                            set_messages(messages.clone());
                        }
                        models::WsDispatch::RoomJoin { room } => {
                            log::info!("Received RoomJoin");
                            rooms.insert(room.clone().id, room.clone());
                            set_rooms(rooms.clone());
                        }
                    }
                }
                _ => unreachable!()
            }
        }

        log::info!("Done with WS");
    };

    join!(heartbeat_task, polling_task);
}
