# Exercises: ECC, Weak Entropy and Authentication Mechanisms

## Exercise 1: Implement the group law for elliptic curves

## Objective

In this exercise, you will implement the group law for the elliptic curve called Curve25519. For simplicity, we will use the Weierstrass model of the curve.
This will involve defining point addition and doubling for the elliptic curve, which are essential components for any cryptographic algorithm based on elliptic curves.

### The Elliptic Curve
The elliptic curve used is defined by the equation:

$$ y^2 = x^3 + ax + b \pmod{p} $$

Where:
- $a$ and $b$ are constants defining the curve.
- $p$ is a prime number that defines the field over which the curve is defined.

### Group Law

The group law involves two primary operations: point addition and point doubling.

#### Point Addition
Given two distinct points $P = (x_1, y_1)$ and $Q = (x_2, y_2)$ on the curve, the sum $R = P + Q$ is calculated as follows:

1. If $P \neq Q$, the slope $\lambda$ is given by:

$$ \lambda = \frac{y_2 - y_1}{x_2 - x_1} \pmod{p} $$

2. The coordinates of the resulting point $R = (x_3, y_3)$ are then:

$$ x_3 = \lambda^2 - x_1 - x_2 \pmod{p} $$

$$ y_3 = \lambda(x_1 - x_3) - y_1 \pmod{p} $$

#### Point Doubling
For point doubling, i.e., when $P = Q$, the formulas simplify to:

$$ \lambda = \frac{3x_1^2 + a}{2y_1} \pmod{p} $$

And the resulting point $R = 2P = (x_3, y_3)$ is calculated as:

$$ x_3 = \lambda^2 - 2x_1 \pmod{p} $$

$$ y_3 = \lambda(x_1 - x_3) - y_1 \pmod{p} $$

#### Scalar Multiplication
Scalar multiplication involves multiplying a point $P$ by an integer $k$. This can be performed using repeated point doubling and addition. The algorithm for scalar multiplication is:

1. Start with $R = O$ (the point at infinity, which is the identity element).
2. For each bit $b$ of $k$, starting from the most significant bit:
   - Double the point: $R = 2R$
   - If the bit $b$ is 1, add $P$ to $R$: $R = R + P$

### Tasks
1. Implement the point addition operation.
2. Implement the point doubling operation.
3. Make sure that the scalar multiplication, and the Diffie-Hellman protocol works correctly by using the provided tests.
4. BONUS: Implement the Montgomery Ladder algorithm using the group law implemented above, as seen in class.

## Exercise 2: Weak Entropy

I have a big problem: When preparing this exercise last Monday, I encrypted a
very important file.  Unfortunately, I forgot to save the key, and now I cannot
access the data anymore.  Can you help me decrypt it?

This is the command that I used:
```
$ python encrypt.py plain.txt ciphertext.bin
```

## Exercise 3: Authentication Mechanisms

We will strengthen your authentication mechanisms by adopting a password manager and hardening its default configuration.

1. First, find a password manager that is compatible with your personal choices of operating system and mobile device. There are many options here, and some popular suggestions are LastPass, 1Password, Dashlane and BitWarden. An open-source solution with somewhat lower usability is KeePass. You should favor any options that support multi-factor authentication as a free option, not requiring a paid subscription.

**Note**: If you already are a user of a password manager, use this exercise to _harden_ your setup instead.

2. Install and create an account in your password manager software. Pick a long passphrase containing at least 6 words by using the [Diceware](https://diceware.dmuth.org/) (or a similar) method.

3. Use the [have i been pwned](https://haveibeenpwned.com/) service to detect if any of your credentials was observed in a data breach included in their database.

4. Migrate some accounts to your new password manager by resetting their passwords and picking the random replacements suggested by the password manager. We do not suggest migrating your e-mail account, since that will be needed to recover your password manager account itself in case the passphrase is lost.

5. Find what options are supported for multi-factor authentication in your password manager, and pick one to setup.

6. Attempt to harden your password manager configuration by finding out what is the current choice of iterations for the password hashing function -- typically [PBKDF2](https://en.wikipedia.org/wiki/PBKDF2) -- and what the recommended best practices are.

7. Think of other ways to harden your account further, for example using it strictly in offline mode (to reduce attack surface) or a secure backup policy for the unlikely case of losing access to your passphrase.
