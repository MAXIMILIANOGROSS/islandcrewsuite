// Island Crew · ventana nativa de macOS (sin Chrome ni barra de direcciones).
// Modo programa:  ventana "Título" icono.icns -- python3 script.py args…   (arranca el programa y muestra su pantalla)
// Modo directo:   ventana --url http://127.0.0.1:1234/ "Título" icono.icns
import Cocoa
import WebKit

let args = Array(CommandLine.arguments.dropFirst())
var titulo = "Island Crew"
var icono = ""
var cmd: [String] = []
var urlDirecta: String? = nil
if args.first == "--url" && args.count >= 2 {
    urlDirecta = args[1]
    if args.count > 2 { titulo = args[2] }
    if args.count > 3 { icono = args[3] }
} else {
    if args.count > 0 { titulo = args[0] }
    if args.count > 1 { icono = args[1] }
    if let i = args.firstIndex(of: "--") { cmd = Array(args[(i + 1)...]) }
}
ProcessInfo.processInfo.processName = titulo

final class Delegado: NSObject, NSApplicationDelegate, NSWindowDelegate, WKUIDelegate, WKNavigationDelegate {
    var ventana: NSWindow!
    var web: WKWebView!
    var hijo: Process?
    let fifo = NSTemporaryDirectory() + "ic-url-\(getpid()).txt"
    var intentos = 0

    func applicationDidFinishLaunching(_ n: Notification) {
        let cfg = WKWebViewConfiguration()
        cfg.mediaTypesRequiringUserActionForPlayback = []
        web = WKWebView(frame: .zero, configuration: cfg)
        web.uiDelegate = self
        web.navigationDelegate = self
        ventana = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 1280, height: 860), styleMask: [.titled, .closable, .miniaturizable, .resizable], backing: .buffered, defer: false)
        ventana.title = titulo
        ventana.contentView = web
        ventana.minSize = NSSize(width: 760, height: 520)
        ventana.backgroundColor = NSColor(calibratedRed: 0.05, green: 0.06, blue: 0.08, alpha: 1)
        ventana.center()
        ventana.setFrameAutosaveName("ic-" + titulo)
        ventana.delegate = self
        montarMenu()
        if icono != "", let im = NSImage(contentsOfFile: icono) { NSApp.applicationIconImage = im }
        NSApp.activate(ignoringOtherApps: true)
        ventana.makeKeyAndOrderFront(nil)
        web.loadHTMLString("<body style='margin:0;background:#0d0f14;color:#aab4c4;font:18px Georgia,serif;display:flex;align-items:center;justify-content:center;height:100vh'>Island Crew · Abriendo…</body>", baseURL: nil)
        if let u = urlDirecta, let url = URL(string: u) { web.load(URLRequest(url: url)) } else { arrancar() }
    }

    func arrancar() {
        guard !cmd.isEmpty else { NSApp.terminate(nil); return }
        try? FileManager.default.removeItem(atPath: fifo)
        let p = Process()
        p.executableURL = URL(fileURLWithPath: cmd[0])
        p.arguments = Array(cmd.dropFirst())
        var env = ProcessInfo.processInfo.environment
        env["IC_FIFO"] = fifo
        p.environment = env
        do { try p.run() } catch { NSApp.terminate(nil); return }
        hijo = p
        Timer.scheduledTimer(withTimeInterval: 0.2, repeats: true) { t in
            if let s = try? String(contentsOfFile: self.fifo, encoding: .utf8) {
                let u = s.trimmingCharacters(in: .whitespacesAndNewlines)
                if !u.isEmpty, let url = URL(string: u) {
                    t.invalidate()
                    try? FileManager.default.removeItem(atPath: self.fifo)
                    self.web.load(URLRequest(url: url))
                    return
                }
            }
            self.intentos += 1
            if self.intentos > 400 || (self.hijo?.isRunning == false && self.intentos > 5) { t.invalidate(); NSApp.terminate(nil) }
        }
    }

    func applicationShouldTerminateAfterLastWindowClosed(_ s: NSApplication) -> Bool { true }
    func windowWillClose(_ n: Notification) { NSApp.terminate(nil) }
    func applicationWillTerminate(_ n: Notification) { if let h = hijo, h.isRunning { h.terminate() } }
    @objc func recargar() { web.reload() }

    func montarMenu() {
        let m = NSMenu(); NSApp.mainMenu = m
        let a = NSMenuItem(); m.addItem(a); let am = NSMenu(); a.submenu = am
        am.addItem(withTitle: "Ocultar " + titulo, action: #selector(NSApplication.hide(_:)), keyEquivalent: "h")
        am.addItem(withTitle: "Salir de " + titulo, action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q")
        let e = NSMenuItem(); m.addItem(e); let em = NSMenu(title: "Edición"); e.submenu = em
        em.addItem(withTitle: "Deshacer", action: Selector(("undo:")), keyEquivalent: "z")
        em.addItem(withTitle: "Rehacer", action: Selector(("redo:")), keyEquivalent: "Z")
        em.addItem(NSMenuItem.separator())
        em.addItem(withTitle: "Cortar", action: #selector(NSText.cut(_:)), keyEquivalent: "x")
        em.addItem(withTitle: "Copiar", action: #selector(NSText.copy(_:)), keyEquivalent: "c")
        em.addItem(withTitle: "Pegar", action: #selector(NSText.paste(_:)), keyEquivalent: "v")
        em.addItem(withTitle: "Seleccionar todo", action: #selector(NSText.selectAll(_:)), keyEquivalent: "a")
        let v = NSMenuItem(); m.addItem(v); let vm = NSMenu(title: "Ver"); v.submenu = vm
        let r = vm.addItem(withTitle: "Recargar", action: #selector(recargar), keyEquivalent: "r"); r.target = self
        let w = NSMenuItem(); m.addItem(w); let wm = NSMenu(title: "Ventana"); w.submenu = wm
        wm.addItem(withTitle: "Minimizar", action: #selector(NSWindow.performMiniaturize(_:)), keyEquivalent: "m")
        wm.addItem(withTitle: "Cerrar", action: #selector(NSWindow.performClose(_:)), keyEquivalent: "w")
    }

    // avisos, confirmaciones y cuadros de texto de la pantalla
    func webView(_ w: WKWebView, runJavaScriptAlertPanelWithMessage message: String, initiatedByFrame frame: WKFrameInfo, completionHandler: @escaping () -> Void) {
        let a = NSAlert(); a.messageText = titulo; a.informativeText = message; a.addButton(withTitle: "OK"); a.runModal(); completionHandler()
    }
    func webView(_ w: WKWebView, runJavaScriptConfirmPanelWithMessage message: String, initiatedByFrame frame: WKFrameInfo, completionHandler: @escaping (Bool) -> Void) {
        let a = NSAlert(); a.messageText = titulo; a.informativeText = message; a.addButton(withTitle: "OK"); a.addButton(withTitle: "Cancelar")
        completionHandler(a.runModal() == .alertFirstButtonReturn)
    }
    func webView(_ w: WKWebView, runJavaScriptTextInputPanelWithPrompt prompt: String, defaultText: String?, initiatedByFrame frame: WKFrameInfo, completionHandler: @escaping (String?) -> Void) {
        let a = NSAlert(); a.messageText = titulo; a.informativeText = prompt; a.addButton(withTitle: "OK"); a.addButton(withTitle: "Cancelar")
        let t = NSTextField(frame: NSRect(x: 0, y: 0, width: 320, height: 24)); t.stringValue = defaultText ?? ""; a.accessoryView = t
        completionHandler(a.runModal() == .alertFirstButtonReturn ? t.stringValue : nil)
    }
    // elegir archivos (logo, fondo, fotos…)
    func webView(_ w: WKWebView, runOpenPanelWith parameters: WKOpenPanelParameters, initiatedByFrame frame: WKFrameInfo, completionHandler: @escaping ([URL]?) -> Void) {
        let o = NSOpenPanel()
        o.allowsMultipleSelection = parameters.allowsMultipleSelection
        o.canChooseDirectories = parameters.allowsDirectories
        o.canChooseFiles = true
        o.beginSheetModal(for: ventana) { r in completionHandler(r == .OK ? o.urls : nil) }
    }
    // enlaces de fuera → navegador normal; los del propio programa se quedan aquí
    func webView(_ w: WKWebView, decidePolicyFor a: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        if let u = a.request.url, let s = u.scheme, s == "http" || s == "https", let h = u.host, h != "127.0.0.1", h != "localhost" {
            NSWorkspace.shared.open(u); decisionHandler(.cancel); return
        }
        decisionHandler(.allow)
    }
    func webView(_ w: WKWebView, createWebViewWith c: WKWebViewConfiguration, for a: WKNavigationAction, windowFeatures: WKWindowFeatures) -> WKWebView? {
        if let u = a.request.url {
            if u.host == "127.0.0.1" || u.host == "localhost" { w.load(a.request) } else { NSWorkspace.shared.open(u) }
        }
        return nil
    }
}

let app = NSApplication.shared
let del = Delegado()
app.delegate = del
app.setActivationPolicy(.regular)
app.run()
