# Macro: $(id) = tronco, $(o) = nombre corto del marcador, $(s) = brote que se replanta
$scoreboard players set @s tc_$(o) 0
execute if entity @s[tag=talar_off] run return 0
execute if score @s tc_dif matches 1.. run return 0
execute unless items entity @s weapon.mainhand #minecraft:axes run return 0
function talar:presupuesto
execute if score #disp talar_cfg matches ..7 run function talar:sin_durabilidad
execute if score #disp talar_cfg matches ..7 run return 0
$data modify storage talar:tmp b set value "$(id)"
$data modify storage talar:tmp s set value "$(s)"
scoreboard players set #hallado talar_cfg 0
$execute at @s as @e[type=item,distance=..8,limit=1,sort=nearest,nbt={Age:0s,Item:{id:"$(id)"}}] at @s run function talar:iniciar
$execute if score #hallado talar_cfg matches 0 at @s as @e[type=item,distance=..8,limit=1,sort=nearest,nbt={Age:1s,Item:{id:"$(id)"}}] at @s run function talar:iniciar
execute if score #hallado talar_cfg matches 1 run function talar:desgastar
execute if score #hallado talar_cfg matches 1 run function talar:resumen
