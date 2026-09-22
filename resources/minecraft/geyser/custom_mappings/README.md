# Geyser custom mappings

Place Geyser custom mapping `.json` files directly in this directory. They are copied to the deployment node by `script/copy_plugins_to_remote.sh` and mounted read-only at `/plugins/Geyser-Velocity/custom_mappings`.

The current [ValhallaMMO Geyser Resource Pack Wiki](https://github.com/Athlaeos/ValhallaMMO/wiki/Geyser-Resource-Pack-%F0%9F%8E%A8) names its mapping `ValhallaMMOmappings.json`, but labels the distribution as unofficial and unmaintained and gives no compatible ValhallaMMO or Minecraft version. Its mapping uses deprecated Geyser custom-item format v1. Verify compatibility with ValhallaMMO 1.10.3 and Minecraft 26.2 before placing the unmodified file here.
