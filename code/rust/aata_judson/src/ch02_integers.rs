pub fn gcd(a: i64, b: i64) -> i64 {
    let mut x = a.abs();
    let mut y = b.abs();

    while y != 0 {
        let remainder = x % y;
        x = y;
        y = remainder;
    }

    x
}

pub fn extended_gcd(a: i64, b: i64) -> (i64, i64, i64) {
    let mut old_r = a.abs();
    let mut r = b.abs();
    let mut old_s = 1;
    let mut s = 0;
    let mut old_t = 0;
    let mut t = 1;

    while r != 0 {
        let quotient = old_r / r;

        let next_r = old_r - quotient * r;
        old_r = r;
        r = next_r;

        let next_s = old_s - quotient * s;
        old_s = s;
        s = next_s;

        let next_t = old_t - quotient * t;
        old_t = t;
        t = next_t;
    }

    let x = if a >= 0 { old_s } else { -old_s };
    let y = if b >= 0 { old_t } else { -old_t };
    (old_r, x, y)
}

#[cfg(test)]
mod tests {
    use super::{extended_gcd, gcd};

    #[test]
    fn gcd_is_nonnegative_and_divides_inputs() {
        for a in -25..=25 {
            for b in -25..=25 {
                let result = gcd(a, b);
                assert!(result >= 0);

                if result == 0 {
                    assert_eq!((a, b), (0, 0));
                } else {
                    assert_eq!(a % result, 0);
                    assert_eq!(b % result, 0);
                }
            }
        }
    }

    #[test]
    fn extended_gcd_satisfies_bezout_identity() {
        for a in -25..=25 {
            for b in -25..=25 {
                let (g, x, y) = extended_gcd(a, b);
                assert_eq!(g, gcd(a, b));
                assert_eq!(a * x + b * y, g);
            }
        }
    }
}

