# Macro: $(o) marcador, $(b) mena picada, $(c) su variante (piedra/pizarra), $(d) lo que suelta, $(x) experiencia por bloque
$scoreboard players set @s tv_$(o) 0
execute if entity @s[tag=veta_off] run return 0
execute if score @s tv_dif matches 1.. run return 0
execute unless items entity @s weapon.mainhand #minecraft:pickaxes run return 0
$data modify storage veta:tmp b set value "$(b)"
$data modify storage veta:tmp c set value "$(c)"
$data modify storage veta:tmp x set value $(x)
scoreboard players set #hallado veta_cfg 0
$execute at @s positioned as @e[type=item,distance=..8,limit=1,sort=nearest,nbt={Age:0s,Item:{id:"$(d)"}}] run function veta:iniciar
$execute if score #hallado veta_cfg matches 0 at @s positioned as @e[type=item,distance=..8,limit=1,sort=nearest,nbt={Age:0s,Item:{id:"$(b)"}}] run function veta:iniciar
$execute if score #hallado veta_cfg matches 0 at @s positioned as @e[type=item,distance=..8,limit=1,sort=nearest,nbt={Age:1s,Item:{id:"$(d)"}}] run function veta:iniciar
$execute if score #hallado veta_cfg matches 0 at @s positioned as @e[type=item,distance=..8,limit=1,sort=nearest,nbt={Age:1s,Item:{id:"$(b)"}}] run function veta:iniciar
execute if score #hallado veta_cfg matches 1 run function veta:resumen
