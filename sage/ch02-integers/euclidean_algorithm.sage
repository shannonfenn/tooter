# Chapter 2: Euclidean algorithm checks in Sage

a = 252
b = 198

g, x, y = xgcd(a, b)
print((g, x, y))
print(a * x + b * y)

