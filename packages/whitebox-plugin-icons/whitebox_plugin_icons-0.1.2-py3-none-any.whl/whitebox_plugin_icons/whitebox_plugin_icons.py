import whitebox


class WhiteboxPluginIcons(whitebox.Plugin):
    name = "Icons"

    provides_capabilities = ["icons"]
    exposed_component_map = {
        "icons": {
            # Logos
            "logo": "Logo",
            "logo-white-on-black": "generated/logos/WhiteOnBlack",
            # Icons
            "eye": "generated/icons/Eye",
            "info": "generated/icons/Info",
            "link": "generated/icons/Link",
            "close": "generated/icons/Close",
            "search": "generated/icons/Search",
            "cancel": "generated/icons/Cancel",
            "eclipse": "generated/icons/Eclipse",
            "spinner": "generated/icons/Spinner",
            "arrow-back": "generated/icons/ArrowBack",
            "camera-device": "generated/icons/CameraDevice",
            "check-circle": "generated/icons/CheckCircle",
            "chevron-right": "generated/icons/ChevronRight",
            "import-export": "generated/icons/ImportExport",
        },
    }


plugin_class = WhiteboxPluginIcons
