
public class Service {
    public void exec(String cmd) {
        try {
            Runtime.getRuntime().exec(cmd);
        } catch(Exception e) {}
    }
}
