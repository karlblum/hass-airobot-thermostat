# Airobot Thermostat Integration for Home Assistant

This custom integration allows you to integrate **Airobot thermostats** with Home Assistant, enabling control and monitoring of your thermostat directly from Home Assistant. You can view and manage the temperature, humidity, CO2 levels, and current mode of your Airobot thermostat, with seamless integration into Home Assistant's climate entities.

## Features

- **Temperature Monitoring**: View and set the current and target temperatures for your Airobot thermostat.
- **Humidity and CO2 Monitoring**: Display current humidity and CO2 levels (if supported by the thermostat).
- **Mode Display**: View the current operating mode (Home or Away).
- **Temperature Control**: Adjust the target temperature directly from Home Assistant.
- **Seamless Integration**: Works with Home Assistant's climate component, allowing automation and control via the Home Assistant UI and automations.

## Requirements

- Airobot thermostat that supports the API.
- Home Assistant 2023.1 or later.

## Installation Instructions (via HACS)

To install this integration via HACS (Home Assistant Community Store), follow these steps:

### Step 1: Install HACS

If you haven't already installed HACS, follow the [HACS installation guide](https://hacs.xyz/docs/setup/download).

### Step 2: Add the Integration Repository to HACS

1. Open Home Assistant and navigate to **HACS** from the sidebar.
2. Click on **Integrations**.
3. Click the three dots menu in the top-right corner and select **Custom repositories**.
4. In the **Repository** field, enter the following URL for this integration's repository:
   https://github.com/karlblum/hass-airobot-thermostat

### Step 3: Install the Integration

1. Once you've added the custom repository, search for **Airobot Thermostat** in the HACS integrations.
2. Click **Download** to install the integration.

### Step 4: Restart Home Assistant

After installing the integration, you must restart Home Assistant for the changes to take effect.

1. Navigate to **Settings** > **System** > **Restart**.
2. Click **Restart** to restart Home Assistant.

### Step 5: Configure the Integration

1. After the restart, go to **Settings** > **Devices & Services**.
2. Click **Add Integration** and search for **Airobot Thermostat**.
3. Follow the on-screen instructions to configure the integration by entering your thermostat's details (e.g., IP address, username, and password).

### Step 6: Enjoy!

Once configured, your Airobot thermostat will be added to Home Assistant. You can now monitor and control the thermostat from the Home Assistant UI, set up automations, and more.

## Troubleshooting

If you encounter any issues with the integration:

1. Check the Home Assistant logs for any errors.
2. Ensure your thermostat is reachable on the network and that the API credentials are correct.

## Support

For issues, feature requests, or contributions, please visit the [GitHub repository](https://github.com/karlblum/hass-airobot-thermostat).

---

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
