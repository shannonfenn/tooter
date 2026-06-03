use aata_judson::ch02::extended_gcd;

fn main() {
    let examples = [(252, 198), (101, 23), (-84, 30)];

    for (a, b) in examples {
        let (g, x, y) = extended_gcd(a, b);
        println!("gcd({a}, {b}) = {g}; Bezout coefficients: x={x}, y={y}");
        println!("  check: {a}*{x} + {b}*{y} = {}", a * x + b * y);
    }
}
