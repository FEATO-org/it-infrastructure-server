#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <player-group> <admin-group>" >&2
  exit 2
fi

player_group=$1
admin_group=$2
mapfile -t containers < <(docker ps -q --filter label=com.docker.swarm.service.name=app_minecraft-server)
if [ "${#containers[@]}" -ne 1 ]; then
  echo "Run on the minecraft-data node; expected exactly one app_minecraft-server task, found ${#containers[@]}." >&2
  exit 1
fi
container_id=${containers[0]}

set_permission() {
  docker exec "$container_id" rcon-cli "lp group $1 permission set $2 $3"
}

player_allow=(
  essentials.balance
  essentials.pay
  essentials.kit
  ei.item.emergency_return
  ei.item.mayor_flag
  ei.item.guard_captain_flag
  EconomyShopGUI.shop
  EconomyShopGUI.shop.feato_shop
  deadchest.generate
  deadchest.get
)
player_deny=(
  essentials.spawn
  essentials.kits.return_ticket
  EconomyShopGUI.shop.all
  EconomyShopGUI.sellall
  EconomyShopGUI.sellallitem
  EconomyShopGUI.sellallhand
  EconomyShopGUI.sellgui
  EconomyShopGUI.sellall.all
  EconomyShopGUI.sellallitem.all
  EconomyShopGUI.sellallhand.all
  EconomyShopGUI.sellgui.all
)
admin_allow=(
  essentials.balance.others
  essentials.eco
  essentials.setspawn
  essentials.createkit
  essentials.showkit
  EconomyShopGUI.reload
  EconomyShopGUI.itemindexes
  EconomyShopGUI.eshop.additem
  EconomyShopGUI.eshop.edititem
  EconomyShopGUI.eshop.deleteitem
  EconomyShopGUI.eshop.addhanditem
  EconomyShopGUI.eshop.addsection
  EconomyShopGUI.eshop.editsection
  EconomyShopGUI.eshop.deletesection
  fancynpcs.command.npc.create
  fancynpcs.command.npc.remove
  fancynpcs.command.npc.list
  fancynpcs.command.npc.info
  fancynpcs.command.npc.displayname
  fancynpcs.command.npc.skin
  fancynpcs.command.npc.move_to
  fancynpcs.command.npc.interaction_cooldown
  fancynpcs.command.npc.action.add
  fancynpcs.command.npc.action.add.need_permission
  fancynpcs.command.npc.action.add.message
  fancynpcs.command.npc.action.add.player_command
  fancynpcs.command.npc.action.add.console_command
  fancynpcs.command.npc.action.remove
  fancynpcs.command.npc.action.clear
  fancynpcs.command.npc.action.list
  fancynpcs.command.fancynpcs.reload
  fancynpcs.command.fancynpcs.save
)

for permission in "${player_allow[@]}"; do set_permission "$player_group" "$permission" true; done
for permission in "${player_deny[@]}"; do set_permission "$player_group" "$permission" false; done
for permission in "${admin_allow[@]}"; do set_permission "$admin_group" "$permission" true; done

for role_group in mayor guard_captain; do
  docker exec "$container_id" rcon-cli "lp creategroup $role_group"
done
set_permission mayor feato.mayor true
set_permission guard_captain feato.guard_captain true

echo "Permissions applied to player group '$player_group' and admin group '$admin_group'."
