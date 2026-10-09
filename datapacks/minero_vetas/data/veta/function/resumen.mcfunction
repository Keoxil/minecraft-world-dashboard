scoreboard players operation #rotos veta_cfg = #limite veta_cfg
scoreboard players operation #rotos veta_cfg -= #cuenta veta_cfg
execute if score #rotos veta_cfg matches 2.. run title @s actionbar [{"text":"⛏ Veta extraída: ","color":"aqua"},{"score":{"name":"#rotos","objective":"veta_cfg"},"color":"white"},{"text":" bloques","color":"gray"}]
