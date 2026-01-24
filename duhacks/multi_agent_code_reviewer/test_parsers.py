import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from snippet.parsers.javascript_parser import JavascriptParser
from snippet.parsers.typescript_parser import TypescriptParser

def test_js_parser():
    print("="*60)
    print("TESTING JAVASCRIPT PARSER")
    print("="*60)
    
    code = """
    function explicitFunction() {
        if (true) {
            console.log("Hello");
        }
        return 42;
    }
    
    const arrowFunc = () => {
        eval("alert('hacked')");
        while(true) { break; }
    }
    
    class MyClass {
        myMethod() {
            const query = "SELECT * FROM users";
        }
    }
    """
    
    try:
        parser = JavascriptParser()
        blocks = parser.parse(code)
        
        print(f"Found {len(blocks)} blocks:")
        for b in blocks:
            print(f"- [{b.type}] {b.name} (Lines: {b.start_line}-{b.end_line}, Complexity: {b.complexity})")
            print(f"  Metadata: {b.metadata}")
            
    except Exception as e:
        print(f"JS Parser Failed: {e}")
        import traceback
        traceback.print_exc()

def test_ts_parser():
    print("\n" + "="*60)
    print("TESTING TYPESCRIPT PARSER")
    print("="*60)
    
    code = """
    interface User {
        id: number;
        name: string;
    }
    
    function processUser(user: User): void {
        const x = new Function('return 1');
    }
    """
    
    try:
        parser = TypescriptParser()
        blocks = parser.parse(code)
        
        print(f"Found {len(blocks)} blocks:")
        for b in blocks:
            print(f"- [{b.type}] {b.name} (Lines: {b.start_line}-{b.end_line})")
            
    except Exception as e:
        print(f"TS Parser Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_js_parser()
    test_ts_parser()
