// Copyright 2023 Georges Racinet <georges.racinet@octobus.net>
//
// This software may be used and distributed according to the terms of the
// GNU General Public License version 2 or any later version.
// SPDX-License-Identifier: GPL-2.0-or-later
use tonic::{Request, Response, Status};
use tracing::{info, instrument};

use crate::gitaly::server_service_server::{ServerService, ServerServiceServer};
use crate::gitaly::{ServerInfoRequest, ServerInfoResponse};
use crate::util::tracing_span_id;

build_const!("constants");

#[derive(Debug, Default)]
pub struct ServerServiceImpl {}

#[tonic::async_trait]
impl ServerService for ServerServiceImpl {
    #[instrument(name = "server_info", skip(self, _request))]
    async fn server_info(
        &self,
        _request: Request<ServerInfoRequest>,
    ) -> Result<Response<ServerInfoResponse>, Status> {
        tracing_span_id!();
        info!("Processing");
        Ok(Response::new(ServerInfoResponse {
            server_version: HGITALY_VERSION.into(),
            ..Default::default()
        }))
    }
}

/// Takes care of boilerplate that would instead be in the startup sequence.
pub fn server_server() -> ServerServiceServer<ServerServiceImpl> {
    ServerServiceServer::new(ServerServiceImpl::default())
}
