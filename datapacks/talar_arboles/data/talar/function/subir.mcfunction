# Macro ($(b) = tronco): sube por el tronco hasta su último tronco; ahí es donde están las hojas de un árbol de verdad
$execute if block ~ ~1 ~ $(b) positioned ~ ~1 ~ run function talar:subir with storage talar:tmp
$execute unless block ~ ~1 ~ $(b) run function talar:hojas
