# Se ejecuta al cargar el mundo y con /reload
scoreboard objectives add talar_cfg dummy
scoreboard objectives add talar trigger
scoreboard objectives add tc_agach minecraft.custom:minecraft.sneak_time
scoreboard objectives add tc_ant dummy
scoreboard objectives add tc_dif dummy
scoreboard objectives add tc_oak minecraft.mined:minecraft.oak_log
scoreboard objectives add tc_spruce minecraft.mined:minecraft.spruce_log
scoreboard objectives add tc_birch minecraft.mined:minecraft.birch_log
scoreboard objectives add tc_jungle minecraft.mined:minecraft.jungle_log
scoreboard objectives add tc_acacia minecraft.mined:minecraft.acacia_log
scoreboard objectives add tc_dark_oak minecraft.mined:minecraft.dark_oak_log
scoreboard objectives add tc_mangrove minecraft.mined:minecraft.mangrove_log
scoreboard objectives add tc_cherry minecraft.mined:minecraft.cherry_log
scoreboard objectives add tc_pale_oak minecraft.mined:minecraft.pale_oak_log
# Máximo de troncos que se talan de una vez (se cambia con /scoreboard players set #limite talar_cfg 100)
execute unless score #limite talar_cfg matches 1.. run scoreboard players set #limite talar_cfg 200
# 1 = activado, 0 = desactivado para todo el mundo (/scoreboard players set #activado talar_cfg 0)
execute unless score #activado talar_cfg matches 0..1 run scoreboard players set #activado talar_cfg 1
