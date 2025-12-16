Fix updater installation and NVDA logger compatibility

- Replace unsupported addonHandler.installAddon with os.startfile
- Fix GitHub asset download URL field
- Remove use of excinfo with NVDA logHandler
- Ensure updater uses only supported NVDA APIs
- Improve stability across NVDA 2024+ versions
