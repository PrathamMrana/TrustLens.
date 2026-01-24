
import os
import sys
from snippet.parsers.typescript_parser import TypescriptParser

def debug_ts_parsing():
    content = """
type User = {
    id: number;
    role?: string;
};

function isAuthorized(user: User): boolean {
    // ❌ LOGIC: role can be undefined
    if (user.role!.toLowerCase() === "admin") {
        return true;
    }
    return false;
}

function parseInput(input: any): number {
    // ❌ SECURITY / LOGIC: unsafe any usage
    return input.value * 10;
}

function complexFunction(a: number, b: number, c: number) {
    // ❌ QUALITY: High complexity
    if (a > 0) {
        if (b > 0) {
            if (c > 0) {
                if (a + b > c) {
                    if (a * b > c) {
                        console.log("Too complex");
                    }
                }
            }
        }
    }
}
"""
    parser = TypescriptParser()
    blocks = parser.parse(content)
    print(f"Total blocks found: {len(blocks)}")
    for i, b in enumerate(blocks):
        print(f"Block {i}: {b.type} {b.name} (complexity: {b.complexity})")
        print(f"  Metadata: {b.metadata}")

if __name__ == "__main__":
    debug_ts_parsing()
