use im_rc::HashMap;

use crate::prelude::*;

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct MeResponse {
    #[serde(flatten)]
    pub user: models::User,
    pub rooms: HashMap<models::ID, models::Room>,
}