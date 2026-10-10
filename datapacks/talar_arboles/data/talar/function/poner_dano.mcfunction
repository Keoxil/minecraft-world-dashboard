# Macro ($(d) = daño total): fija la durabilidad gastada del hacha
$item modify entity @s weapon.mainhand {"function":"minecraft:set_components","components":{"minecraft:damage":$(d)}}
