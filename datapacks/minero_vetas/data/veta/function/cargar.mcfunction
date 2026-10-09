scoreboard objectives add veta_cfg dummy
scoreboard objectives add veta trigger
scoreboard objectives add tv_agach minecraft.custom:minecraft.sneak_time
scoreboard objectives add tv_ant dummy
scoreboard objectives add tv_dif dummy
scoreboard objectives add tv_coal minecraft.mined:minecraft.coal_ore
scoreboard objectives add tv_coald minecraft.mined:minecraft.deepslate_coal_ore
scoreboard objectives add tv_iron minecraft.mined:minecraft.iron_ore
scoreboard objectives add tv_irond minecraft.mined:minecraft.deepslate_iron_ore
scoreboard objectives add tv_cop minecraft.mined:minecraft.copper_ore
scoreboard objectives add tv_copd minecraft.mined:minecraft.deepslate_copper_ore
scoreboard objectives add tv_gold minecraft.mined:minecraft.gold_ore
scoreboard objectives add tv_goldd minecraft.mined:minecraft.deepslate_gold_ore
scoreboard objectives add tv_red minecraft.mined:minecraft.redstone_ore
scoreboard objectives add tv_redd minecraft.mined:minecraft.deepslate_redstone_ore
scoreboard objectives add tv_lap minecraft.mined:minecraft.lapis_ore
scoreboard objectives add tv_lapd minecraft.mined:minecraft.deepslate_lapis_ore
scoreboard objectives add tv_dia minecraft.mined:minecraft.diamond_ore
scoreboard objectives add tv_diad minecraft.mined:minecraft.deepslate_diamond_ore
scoreboard objectives add tv_eme minecraft.mined:minecraft.emerald_ore
scoreboard objectives add tv_emed minecraft.mined:minecraft.deepslate_emerald_ore
scoreboard objectives add tv_ngold minecraft.mined:minecraft.nether_gold_ore
scoreboard objectives add tv_nquar minecraft.mined:minecraft.nether_quartz_ore
# Máximo de bloques por veta (se cambia con /scoreboard players set #limite veta_cfg 32)
execute unless score #limite veta_cfg matches 1.. run scoreboard players set #limite veta_cfg 64
execute unless score #activado veta_cfg matches 0..1 run scoreboard players set #activado veta_cfg 1
