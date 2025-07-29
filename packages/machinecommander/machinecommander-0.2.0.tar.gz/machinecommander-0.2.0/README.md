# machine-commander
MachineCommander is an IoT system to manage all the construction machines working on construction projects.

## MCP server config
```json
{
    "mcpServers": {
        "MachineCommander": {
            "command": "uvx",
            "args": [ "MachineCommander" ],
            "env": {
                "APP_KEY": "Your zhgcloud App Key",
                "APP_SECRET": "Your App Secret"
            }
        }
    }
}
```

## Tools
* _get_construction_machines_data_: Use this tool to extract the data of construction machines and projects, and to answer construction related questions. The returned value includes a "result" field, which can be a table (a list of rows) or an answer (a string).

