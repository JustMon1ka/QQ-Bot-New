from Plugins import Plugins


class TestPlugins(Plugins):
    def __init__(self, server_address):
        super().__init__(server_address)
        self.name = "TestPlugins"
        self.type = "Group"

    async def main(self, event, debug, config):
        return
