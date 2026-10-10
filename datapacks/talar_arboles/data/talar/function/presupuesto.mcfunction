# Lo ejecuta el jugador: calcula cuántos troncos extra aguanta su hacha y fija el tope de este talado
scoreboard players set #max talar_cfg 250
execute if items entity @s weapon.mainhand minecraft:wooden_axe run scoreboard players set #max talar_cfg 59
execute if items entity @s weapon.mainhand minecraft:stone_axe run scoreboard players set #max talar_cfg 131
execute if items entity @s weapon.mainhand minecraft:copper_axe run scoreboard players set #max talar_cfg 190
execute if items entity @s weapon.mainhand minecraft:iron_axe run scoreboard players set #max talar_cfg 250
execute if items entity @s weapon.mainhand minecraft:golden_axe run scoreboard players set #max talar_cfg 32
execute if items entity @s weapon.mainhand minecraft:diamond_axe run scoreboard players set #max talar_cfg 1561
execute if items entity @s weapon.mainhand minecraft:netherite_axe run scoreboard players set #max talar_cfg 2031
scoreboard players set #dano talar_cfg 0
execute store result score #dano talar_cfg run data get entity @s SelectedItem.components."minecraft:damage"
scoreboard players operation #disp talar_cfg = #max talar_cfg
scoreboard players operation #disp talar_cfg -= #dano talar_cfg
scoreboard players operation #tope talar_cfg = #limite talar_cfg
execute if score #disp talar_cfg < #tope talar_cfg run scoreboard players operation #tope talar_cfg = #disp talar_cfg
