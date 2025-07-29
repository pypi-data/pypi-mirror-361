from whitebox import Plugin


class WhiteboxPluginDeviceManager(Plugin):
    name = "Device Manager"

    provides_capabilities = ["device-wizard"]
    slot_component_map = {
        "device-wizard.screen": "Wizard",
    }
    exposed_component_map = {
        "device-wizard": {
            "device-connection": "common/DeviceConnection",
        }
    }


plugin_class = WhiteboxPluginDeviceManager
