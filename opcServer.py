import asyncio
import logging

from asyncua import Server, ua
from asyncua.common.methods import uamethod


@uamethod
def func(parent, value):
    return value * 2



async def main():
    _logger = logging.getLogger(__name__)
    # Server setup
    server = Server()
    await server.init()

    #url = "opc.tcp://192.168.1.14:4840"
    url = "opc.tcp://0.0.0.0:4080/freeopcus/server/"
    server.set_endpoint(url)


    # Set up namespace
    uri = "MY_OPCUA_SIMULATION_SERVER"
    idx = await server.register_namespace(uri)

    # Populate address space
    # Server.nodes, contains linkst to common nodes like objects and root.
    myObj = await server.nodes.objects.add_object(idx, "MyObject")
    myVar = await myObj.add_variable(idx, "MyVariable", 6.7)
    
    # Set myVar to be writable by clients.
    await myVar.set_writable()
    await server.nodes.objects.add_method(
        ua.NodeId("ServerMethod", idx),
        ua.QualifiedName("ServerMethod", idx),
        func,
        [ua.VariantType.Int64],
        [ua.VariantType.Int64],
    )
    _logger.info("Starting server")
    async with server:
        # Testing access to address space.
        _logger.info("\n\n\n")
        db_root = server.get_root_node()
        db_kids = await db_root.get_children()
        _logger.info(db_root)
        _logger.info("\n\n")
        _logger.info(db_kids)
        while True:
            await asyncio.sleep(1)
            new_val = await myVar.get_value() + 0.1
            _logger.info("Set value of %s to %.1f", myVar, new_val)
            await myVar.write_value(new_val)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main(), debug=True)
