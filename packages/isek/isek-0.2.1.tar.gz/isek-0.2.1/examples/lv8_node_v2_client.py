import time
from isek.utils.log import log
from isek.node.node_v2 import Node
from isek.node.etcd_registry import EtcdRegistry
from isek.utils.print_utils import print_send_message_result, print_panel

def main():
    """
    This script acts as a client to send a message to the server node.
    Run this script in a separate terminal after starting the server.
    """
    # Logging is now automatically configured.
    # You can set the log level via the LOG_LEVEL environment variable.
    # e.g., export LOG_LEVEL=DEBUG

    # Define the server's details so the client knows where to send the message.
    server_node_id = "server_node_1"
    server_host = "localhost"
    server_port = 9000

    # Create the client node. Its own ID and port are not critical for sending a single message.
    client_node = Node(node_id="client_node")
    
    # The client needs to know about the server. Since we are using DefaultRegistry,
    # discovery is not automatic. We manually add the server's information
    # to the client's local node cache.
    client_node.all_nodes[server_node_id] = {
        "host": server_host,
        "port": server_port,
        "metadata": {"url": f"http://{server_host}:{server_port}"}
    }
    
    print_panel(title="ISEK Node Send Message Demo",
                content=f"Client node is ready. Sending a message to '{server_node_id}'...",
                color="bright_yellow")
    print_send_message_result(
        lambda msg: client_node.send_message(server_node_id, msg),
        source_node_id=client_node.node_id,
        target_node_id=server_node_id,
        message="Hello from the client!"
    )

if __name__ == "__main__":
    main() 