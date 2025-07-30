import streamlit as st

from mlox.configs_old import Milvus, get_server_connections, update_service
from mlox.remote import fs_read_file


st.set_page_config(page_title="Milvus Install Page", page_icon="🌍")
st.markdown("# Milvus Install")

servers = get_server_connections()
target_ip = st.selectbox("Choose Server", list(servers.keys()))
server = servers[target_ip]

target_path = st.text_input("Install Path", f"/home/{server.user}/my_milvus")

service = Milvus(server, target_path)
update_service(service)
c1, c2, c3, c4 = st.columns([15, 15, 15, 55])
if c1.button("Setup"):
    service.setup()
if c2.button("Start"):
    service.spin_up()
if c3.button("Stop"):
    service.spin_down()

with st.expander("Details"):
    st.write(service)

files = [
    "docker-compose.yaml",
    "service.env",
    # "cert.pem",
    # "htpasswd",
]
tabs = st.tabs(files)
for i in range(len(files)):
    with tabs[i]:
        with service.server as conn:
            res = fs_read_file(
                conn,
                f"{service.target_path}/{files[i]}",
                format="yaml" if files[i][-4:] == "yaml" else None,
            )
            if isinstance(res, str):
                st.text(res)
            else:
                st.write(res, unsafe_allow_html=True)
            print(res)

st.sidebar.header("Links")
st.sidebar.page_link(service.get_service_url(), label="Milvus")
