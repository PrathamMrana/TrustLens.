import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from snippet.parsers.python_parser import PythonParser
from snippet.parsers.javascript_parser import JavascriptParser
from snippet.parsers.typescript_parser import TypescriptParser
from snippet.parsers.java_parser import JavaParser

def print_blocks(language, blocks):
    print(f"\n[{language}] Found {len(blocks)} blocks:")
    for b in blocks:
        print(f"  - [{b.type}] {b.name}")
        print(f"    Lines: {b.start_line}-{b.end_line}")
        print(f"    Complexity: {b.complexity}")
        if b.metadata:
            print(f"    Metadata: {b.metadata}")

def test_python():
    print("="*60)
    print("TESTING PYTHON PARSER")
    print("="*60)
    code = """
def complex_logic(x):
    if x > 10:
        for i in range(x):
            print(i)
    elif x < 0:
        while True:
            break
    else:
        try:
            eval("print('danger')")
        except:
            pass

class SecurityCheck:
    def check_sql(self, query):
        cursor.execute(f"SELECT * FROM {query}")
"""
    parser = PythonParser()
    blocks = parser.parse(code)
    print_blocks("PYTHON", blocks)

def test_javascript():
    print("="*60)
    print("TESTING JAVASCRIPT PARSER")
    print("="*60)
    code = """
function authUser(user) {
    if (user.isAdmin) {
        eval("grantAccess()");
    } else {
        while(true) {
            console.log("waiting...");
        }
    }
}

const db = {
    query: (sql) => {
        if (sql.includes('SELECT')) {
            console.log('Querying...');
        }
    }
}
"""
    parser = JavascriptParser()
    blocks = parser.parse(code)
    print_blocks("JAVASCRIPT", blocks)

def test_typescript():
    print("="*60)
    print("TESTING TYPESCRIPT PARSER")
    print("="*60)
    code = """
interface UserData {
    id: number;
    token: string;
}

class UserManager {
    public validate(data: UserData): boolean {
        if (data.token) {
            const runner = new Function('return 1');
            return true;
        }
        return false;
    }
}
"""
    parser = TypescriptParser()
    blocks = parser.parse(code)
    print_blocks("TYPESCRIPT", blocks)

def test_java():
    print("="*60)
    print("TESTING JAVA PARSER")
    print("="*60)
    code = """
public class PaymentProcessor {
    private String apiKey = "sk_live_12345secret";

    public void processDict(Map<String, String> data) {
        if (data.containsKey("cmd")) {
            try {
                Runtime.getRuntime().exec(data.get("cmd"));
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
        
        for (String key : data.keySet()) {
            System.out.println(key);
        }
    }
    
    public void recursiveLoop() {
        if (true) {
             recursiveLoop();
        }
    }
}
"""
    parser = JavaParser()
    blocks = parser.parse(code)
    print_blocks("JAVA", blocks)

if __name__ == "__main__":
    test_python()
    test_javascript()
    test_typescript()
    test_java()
