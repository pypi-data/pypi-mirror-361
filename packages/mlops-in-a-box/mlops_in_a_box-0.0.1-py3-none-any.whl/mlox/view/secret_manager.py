import pandas as pd

import streamlit as st

from typing import cast

from mlox.infra import Infrastructure
from mlox.secret_manager import AbstractSecretManagerService, AbstractSecretManager


def save_infra():
    with st.spinner("Saving infrastructure..."):
        st.session_state.mlox.save_infrastructure()


def secrets():
    st.markdown("""
    # Secret Manager
    - Keys and secrets
    - Configurations
    """)

    infra = cast(Infrastructure, st.session_state.mlox.infra)

    secret_manager_service_list = []
    for sms in infra.filter_by_group("secret-manager"):
        bundle = infra.get_bundle_by_service(sms)
        if not bundle:
            continue
        secret_manager_service_list.append(
            {
                "ip": bundle.server.ip,
                "server": bundle.name,
                "name": sms.name,
                "path": sms.target_path,
                "service": sms,
                "bundle": bundle,
            }
        )

    df = pd.DataFrame(
        secret_manager_service_list,
        columns=["ip", "server", "name", "path", "service", "bundle"],
    )
    selection = st.dataframe(
        df[["server", "name", "path"]],
        hide_index=True,
        selection_mode="single-row",
        use_container_width=True,
        on_select="rerun",
    )
    if len(selection["selection"]["rows"]) > 0:
        idx = selection["selection"]["rows"][0]
        name = secret_manager_service_list[idx]["name"]
        bundle = secret_manager_service_list[idx]["bundle"]
        secret_manager_service = secret_manager_service_list[idx]["service"]

        # if st.button("Delete"):
        #     with st.spinner(f"Deleting {name}..."):
        #         infra.teardown_service(secret_manager_service)
        #     save_infra()
        #     st.rerun()

        config = infra.get_service_config(secret_manager_service)
        callable_settings_func = config.instantiate_ui("settings")
        if callable_settings_func and secret_manager_service.state == "running":
            callable_settings_func(infra, bundle, secret_manager_service)


secrets()
