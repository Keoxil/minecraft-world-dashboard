# Macro ($(d) = daño total): fija la durabilidad gastada del hacha
$item modify entity @s weapon.mainhand {"type":"minecraft:set_components","components":{"minecraft:damage":$(d)}}
