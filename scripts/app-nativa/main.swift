import Cocoa
import WebKit

let casa = FileManager.default.homeDirectoryForCurrentUser.path
let raiz = ProcessInfo.processInfo.environment["CB_RAIZ"] ?? "\(casa)/Downloads/island-crew-web"

func sh(_ cmd: String, espera: Bool = false) {
    let p = Process(); p.executableURL = URL(fileURLWithPath: "/bin/bash"); p.arguments = ["-lc", cmd]
    p.environment = ProcessInfo.processInfo.environment.merging(["CB_NO_VENTANA": "1"]) { $1 }
    try? p.run(); if espera { p.waitUntilExit() }
}
func puerto() -> Int? {
    guard let d = FileManager.default.contents(atPath: "\(casa)/IslandCrewAI/cabra-beats-app.json"),
          let j = try? JSONSerialization.jsonObject(with: d) as? [String: Any], let p = j["port"] as? Int else { return nil }
    return p
}

class App: NSObject, NSApplicationDelegate, NSWindowDelegate, WKUIDelegate, WKNavigationDelegate {
    var win: NSWindow!; var web: WKWebView!
    func applicationDidFinishLaunching(_ n: Notification) {
        NSApp.setActivationPolicy(.regular)
        let cfg = WKWebViewConfiguration(); cfg.mediaTypesRequiringUserActionForPlayback = []
        web = WKWebView(frame: .zero, configuration: cfg); web.uiDelegate = self; web.navigationDelegate = self
        win = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 1180, height: 860), styleMask: [.titled, .closable, .miniaturizable, .resizable], backing: .buffered, defer: false)
        win.title = "Cabra Beats"; win.contentView = web; win.delegate = self; win.center(); win.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
        web.loadHTMLString("<body style='background:#0e1116;color:#eef2f7;font:18px system-ui;display:flex;align-items:center;justify-content:center;height:100vh'>Arrancando Cabra Beats…</body>", baseURL: nil)
        sh("python3 '\(raiz)/scripts/cabra-beats-app.py' >> '\(casa)/IslandCrewAI/cabra-beats-app.log' 2>&1")
        var intentos = 0
        Timer.scheduledTimer(withTimeInterval: 0.5, repeats: true) { t in
            intentos += 1
            if let p = puerto(), let u = URL(string: "http://127.0.0.1:\(p)/"), (try? Data(contentsOf: u)) != nil {
                t.invalidate(); self.web.load(URLRequest(url: u))
            } else if intentos > 60 {
                t.invalidate(); self.web.loadHTMLString("<body style='background:#0e1116;color:#ff6b6b;font:16px system-ui;padding:40px'>No arrancó. Mira ~/IslandCrewAI/cabra-beats-app.log</body>", baseURL: nil)
            }
        }
    }
    func webView(_ w: WKWebView, runJavaScriptConfirmPanelWithMessage m: String, initiatedByFrame f: WKFrameInfo, completionHandler c: @escaping (Bool) -> Void) {
        let a = NSAlert(); a.messageText = m; a.addButton(withTitle: "Aceptar"); a.addButton(withTitle: "Cancelar"); c(a.runModal() == .alertFirstButtonReturn)
    }
    func webView(_ w: WKWebView, runJavaScriptAlertPanelWithMessage m: String, initiatedByFrame f: WKFrameInfo, completionHandler c: @escaping () -> Void) {
        let a = NSAlert(); a.messageText = m; a.runModal(); c()
    }
    func webView(_ w: WKWebView, runOpenPanelWith parameters: WKOpenPanelParameters, initiatedByFrame frame: WKFrameInfo, completionHandler: @escaping ([URL]?) -> Void) {
        let panel = NSOpenPanel(); panel.canChooseFiles = true; panel.canChooseDirectories = false; panel.allowsMultipleSelection = parameters.allowsMultipleSelection
        panel.message = "Elige tu foto"; panel.prompt = "Elegir"
        panel.beginSheetModal(for: win) { r in completionHandler(r == .OK ? panel.urls : nil) }
    }
    @available(macOS 12.0, *)
    func webView(_ w: WKWebView, requestMediaCapturePermissionFor origin: WKSecurityOrigin, initiatedByFrame frame: WKFrameInfo, type: WKMediaCaptureType, decisionHandler: @escaping (WKPermissionDecision) -> Void) {
        decisionHandler(origin.host == "127.0.0.1" ? .grant : .deny)
    }
    // Los enlaces externos (YouTube, etc.) se abren en tu navegador, no dentro de la ventana
    func webView(_ w: WKWebView, createWebViewWith c: WKWebViewConfiguration, for a: WKNavigationAction, windowFeatures: WKWindowFeatures) -> WKWebView? {
        if let u = a.request.url { NSWorkspace.shared.open(u) }
        return nil
    }
    func webView(_ w: WKWebView, decidePolicyFor a: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        if let u = a.request.url, a.navigationType == .linkActivated, let h = u.host, h != "127.0.0.1" { NSWorkspace.shared.open(u); decisionHandler(.cancel); return }
        decisionHandler(.allow)
    }
    var cerrando = false, limpiarAlCerrar = false
    // Pregunta al programa si está creando algo; nil = no responde (se deja cerrar)
    func trabajando() -> [String]? {
        guard let p = puerto(), let u = URL(string: "http://127.0.0.1:\(p)/api/ocupado") else { return nil }
        var r = URLRequest(url: u); r.timeoutInterval = 2; var out: [String]? = nil; let sem = DispatchSemaphore(value: 0)
        URLSession.shared.dataTask(with: r) { d, _, _ in
            if let d = d, let j = try? JSONSerialization.jsonObject(with: d) as? [String: Any] { out = (j["activo"] as? [String]) ?? [] }
            sem.signal()
        }.resume()
        _ = sem.wait(timeout: .now() + 3); return out
    }
    func confirmarCierre() -> Bool {
        guard let l = trabajando(), !l.isEmpty else { return true }
        let a = NSAlert(); a.alertStyle = .warning; a.messageText = "Cabra Beats está trabajando"
        a.informativeText = "Ahora mismo está haciendo: " + l.joined(separator: ", ") + ".\n\nSi cierras ahora, lo que se esté creando se queda a medias y ocupa espacio en el disco.\n\n• Esperar: sigue trabajando y cierras cuando termine.\n• Cerrar y borrar lo parcial: cancela el trabajo y elimina los restos del disco."
        a.addButton(withTitle: "Esperar"); a.addButton(withTitle: "Cerrar y borrar lo parcial")
        if a.runModal() == .alertFirstButtonReturn { return false }
        limpiarAlCerrar = true; return true
    }
    func finalizar() {
        if cerrando { return }; cerrando = true
        sh("python3 '\(raiz)/scripts/cabra-beats-app.py' --parar", espera: true)
        if limpiarAlCerrar {
            sh("pkill -f acestep-api; pkill -f start_api_server_macos; sleep 2; python3 '\(raiz)/scripts/cabra-beats-app.py' --limpiar >> '\(casa)/IslandCrewAI/cabra-beats-app.log' 2>&1", espera: true)
        }
    }
    func windowShouldClose(_ s: NSWindow) -> Bool { return cerrando || confirmarCierre() }
    func applicationShouldTerminate(_ s: NSApplication) -> NSApplication.TerminateReply {
        if cerrando { return .terminateNow }
        if !confirmarCierre() { return .terminateCancel }
        finalizar(); return .terminateNow
    }
    func windowWillClose(_ n: Notification) { finalizar(); NSApp.terminate(nil) }
}
let app = NSApplication.shared; let del = App(); app.delegate = del; app.run()
