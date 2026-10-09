scoreboard players set @s mc_muerte 0
execute unless data entity @s LastDeathLocation run return 0
data modify storage muerte_coords:tmp x set from entity @s LastDeathLocation.pos[0]
data modify storage muerte_coords:tmp y set from entity @s LastDeathLocation.pos[1]
data modify storage muerte_coords:tmp z set from entity @s LastDeathLocation.pos[2]
data modify storage muerte_coords:tmp dim set from entity @s LastDeathLocation.dimension
data modify storage muerte_coords:tmp nombre set value "Overworld"
execute if data storage muerte_coords:tmp {dim:"minecraft:the_nether"} run data modify storage muerte_coords:tmp nombre set value "Nether"
execute if data storage muerte_coords:tmp {dim:"minecraft:the_end"} run data modify storage muerte_coords:tmp nombre set value "End"
function muerte_coords:mostrar with storage muerte_coords:tmp
