import Cocoa
import WebKit
let casa = FileManager.default.homeDirectoryForCurrentUser.path
let raiz = ProcessInfo.processInfo.environment["CB_RAIZ"] ?? "\(casa)/Downloads/island-crew-web"
let py = "python3 '\(raiz)/scripts/carta-viva/carta-viva-app.py'"
func sh(_ cmd: String, espera: Bool = false) {
    let p = Process(); p.executableURL = URL(fileURLWithPath: "/bin/bash"); p.arguments = ["-lc", cmd]
    try? p.run(); if espera { p.waitUntilExit() }
}
func puerto() -> Int? {
    guard let d = FileManager.default.contents(atPath: "\(casa)/IslandCrewAI/carta-viva-app.json"),
          let j = try? JSONSerialization.jsonObject(with: d) as? [String: Any], let p = j["port"] as? Int else { return nil }
    return p
}
class App: NSObject, NSApplicationDelegate, NSWindowDelegate, WKUIDelegate {
    var win: NSWindow!; var web: WKWebView!; var cerrando = false
    func applicationDidFinishLaunching(_ n: Notification) {
        NSApp.setActivationPolicy(.regular)
        web = WKWebView(frame: .zero, configuration: WKWebViewConfiguration()); web.uiDelegate = self
        win = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 1100, height: 860), styleMask: [.titled, .closable, .miniaturizable, .resizable], backing: .buffered, defer: false)
        win.title = "Carta Viva"; win.contentView = web; win.delegate = self; win.center(); win.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
        web.loadHTMLString("<body style='background:#0e1116;color:#eef2f7;font:18px system-ui;display:flex;align-items:center;justify-content:center;height:100vh'>Arrancando Carta Viva…</body>", baseURL: nil)
        sh("\(py) >> '\(casa)/IslandCrewAI/carta-viva-app.log' 2>&1")
        var n = 0
        Timer.scheduledTimer(withTimeInterval: 0.5, repeats: true) { t in
            n += 1
            if let p = puerto(), let u = URL(string: "http://127.0.0.1:\(p)/"), (try? Data(contentsOf: u)) != nil { t.invalidate(); self.web.load(URLRequest(url: u)) }
            else if n > 60 { t.invalidate(); self.web.loadHTMLString("<body style='background:#0e1116;color:#ff6b6b;font:16px system-ui;padding:40px'>No arrancó. Mira ~/IslandCrewAI/carta-viva-app.log</body>", baseURL: nil) }
        }
    }
    func webView(_ w: WKWebView, runJavaScriptConfirmPanelWithMessage m: String, initiatedByFrame f: WKFrameInfo, completionHandler c: @escaping (Bool) -> Void) {
        let a = NSAlert(); a.messageText = m; a.addButton(withTitle: "Aceptar"); a.addButton(withTitle: "Cancelar"); c(a.runModal() == .alertFirstButtonReturn)
    }
    func webView(_ w: WKWebView, runJavaScriptTextInputPanelWithPrompt p: String, defaultText: String?, initiatedByFrame f: WKFrameInfo, completionHandler c: @escaping (String?) -> Void) {
        let a = NSAlert(); a.messageText = p; let t = NSTextField(frame: NSRect(x: 0, y: 0, width: 300, height: 24)); t.stringValue = defaultText ?? ""; a.accessoryView = t
        a.addButton(withTitle: "Aceptar"); a.addButton(withTitle: "Cancelar"); c(a.runModal() == .alertFirstButtonReturn ? t.stringValue : nil)
    }
    func webView(_ w: WKWebView, runOpenPanelWith p: WKOpenPanelParameters, initiatedByFrame f: WKFrameInfo, completionHandler c: @escaping ([URL]?) -> Void) {
        let o = NSOpenPanel(); o.allowsMultipleSelection = p.allowsMultipleSelection; c(o.runModal() == .OK ? o.urls : nil)
    }
    func finalizar() { if cerrando { return }; cerrando = true; sh("\(py) --parar", espera: true) }
    func windowWillClose(_ n: Notification) { finalizar(); NSApp.terminate(nil) }
    func applicationShouldTerminate(_ s: NSApplication) -> NSApplication.TerminateReply { finalizar(); return .terminateNow }
}
let app = NSApplication.shared; let del = App(); app.delegate = del; app.run()
