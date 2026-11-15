import re, sys
P = "src/components/RealTownWorld.tsx"
s = open(P, encoding="utf-8").read()
if "AvatarInteractionSystem" in s: print("ya parcheado"); sys.exit(0)
def rep(old, new, cnt=1):
    global s
    if s.count(old) < 1: print("NO ENCONTRADO:", old[:70]); sys.exit(1)
    s = s.replace(old, new, cnt)

# 1 imports
rep('import NpcChat from "@/components/NpcChat";',
 'import { AvatarRenderer } from "@/lib/avatar/render"; import { loadAvatarLocal, loadAvatarRemote, type AvatarConfig } from "@/lib/avatar/config"; import { AvatarInteractionSystem, INTERACTIVE_OBJECTS } from "@/lib/avatar/interaction"; import { ScooterController, AnimationController } from "@/lib/avatar/motion"; import { createScooter, targetFor, applyScooter, setScooterDebug } from "@/lib/avatar/scooterModel"; import { solveGripPlacement, smooth } from "@/lib/avatar/ik"; import AvatarEditor from "@/components/AvatarEditor";\nimport NpcChat from "@/components/NpcChat";')

# 2 estado del editor
rep('  useEffect(() => { let off = false; const code =',
 '  const [editor, setEditor] = useState(false); const edR = useRef(false); const avR = useRef<((c: AvatarConfig) => void) | null>(null); useEffect(() => { edR.current = editor; }, [editor]);\n  useEffect(() => { let off = false; const code =')

# 3 modelo del patinete
a = s.index('const scooterMesh = (col = "#1f2933") => {'); b = s.index('return g; };', a) + len('return g; };')
s = s[:a] + 'const scooterMesh = (col = "#1f2933") => createScooter(col);' + s[b:]

# 4 sistema de avatar tras rd
RD = 'const rd: { i: number; batt: number } = { i: -1, batt: 0 };'
SETUP = r'''
      /* AVATAR + interaccion (patinete con IK en las manos). Todo el calculo vive en src/lib/avatar; aqui solo se conecta al mundo. */
      const SDEF = INTERACTIVE_OBJECTS.scooter; const avatar = new AvatarRenderer(loadAvatarLocal()); avatar.root.visible = false; scene.add(avatar.root); avR.current = (c) => avatar.setConfig(c);
      supabase.auth.getUser().then(({ data }) => { if (data.user) loadAvatarRemote(supabase as never, data.user.id).then((c) => { if (c) avatar.setConfig(c); }); }).catch(() => { /* sin sesion */ });
      const inter = new AvatarInteractionSystem(), sctl = new ScooterController(), anim = new AnimationController(); const cm = { third: false, prev: false, dist: 3.1, blend: 0 };
      let mountI = -1, dbgOn = false, lastX = pos.x, lastZ = pos.z, lastYaw = yaw, spd = 0, yrate = 0, plM: unknown = null, plV: ReturnType<typeof solveGripPlacement> | null = null, sideX = 0, sideZ = 0;
      const sw = (o: THREE.Object3D, lx: number, lz: number): [number, number] => { const th = o.rotation.y; return [o.position.x + Math.cos(th) * lx + Math.sin(th) * lz, o.position.z - Math.sin(th) * lx + Math.cos(th) * lz]; };
      inter.onPhase = (p) => { if (mountI < 0) return; const sc = scoots[mountI]; const R = SDEF.rig;
        if (p === "APPROACH") { cm.prev = cm.third; cm.third = true; }
        if (p === "MOUNT") { avatar.hands.setLeftHandTarget(targetFor(sc.g as never, SDEF.leftHandTarget)); avatar.hands.setRightHandTarget(targetFor(sc.g as never, SDEF.rightHandTarget)); avatar.feet.setLeftFootTarget(targetFor(sc.g as never, SDEF.leftFootTarget)); avatar.feet.setRightFootTarget(targetFor(sc.g as never, SDEF.rightFootTarget)); }
        if (p === "ACTIVE") { pos.x = sc.x; pos.z = sc.z; lastX = pos.x; lastZ = pos.z; rd.i = mountI; rd.batt = sc.batt; setRide(Math.round(rd.batt)); }
        if (p === "DISMOUNT") { sc.batt = rd.batt; rd.i = -1; setRide(null); sc.x = pos.x; sc.z = pos.z; sc.g.position.y = 0; let [qx, qz] = sw(sc.g, R.mountSide[0], R.mountSide[2]); if (blocked(qx, qz)) [qx, qz] = sw(sc.g, -R.mountSide[0], R.mountSide[2]); if (blocked(qx, qz)) { qx = pos.x; qz = pos.z; } sideX = qx; sideZ = qz; }
        if (p === "NONE") { pos.x = sideX; pos.z = sideZ; lastX = pos.x; lastZ = pos.z; avatar.hands.releaseHands(0.05); avatar.feet.release(0.05); sc.on = false; mountI = -1; cm.third = cm.prev; } };'''
rep(RD, RD + SETUP)

# 5 teclas: bajar / subir por el sistema de interaccion
a = s.index('if (e.code === "KeyE" && rd.i >= 0) {'); endm = 'rd.i = -1; setRide(null); }'; b = s.index(endm, a) + len(endm)
s = s[:a] + 'if (e.code === "KeyE" && rd.i >= 0) { inter.requestEnd(); }' + s[b:]
rep('{ const sc = scoots[nearScootI.v]; sc.on = true; sc.g.visible = false; rd.i = nearScootI.v; rd.batt = sc.batt; setRide(Math.round(rd.batt)); }',
    '{ const ii = nearScootI.v; const sc = scoots[ii]; if (inter.begin(SDEF, Math.hypot(sc.x - pos.x, sc.z - pos.z))) { mountI = ii; sc.on = true; } }')
rep('nearScootI.v < 0 && rd.i < 0 &&', 'nearScootI.v < 0 && rd.i < 0 && !inter.active &&')
rep('const kd = (e: KeyboardEvent) => { if (typing(e)) return;', 'const kd = (e: KeyboardEvent) => { if (typing(e) || edR.current) return;')
rep('if (e.code === "KeyP") { setInfoOpen', 'if (e.code === "KeyV") cm.third = !cm.third; if (e.code === "KeyG") { dbgOn = !dbgOn; avatar.setDebug(dbgOn); for (const q of scoots) setScooterDebug(q.g as never, dbgOn, SDEF); } if (e.code === "KeyU") { try { document.exitPointerLock?.(); } catch { /* sin bloqueo */ } for (const k2 of Object.keys(keys)) keys[k2] = false; setEditor(true); }\n if (e.code === "KeyP") { setInfoOpen')

# 6 movimiento bloqueado
OLDFX = 'const fx = (keys.KeyW || keys.ArrowUp ? 1 : 0) - (keys.KeyS || keys.ArrowDown ? 1 : 0), sxk = (keys.KeyD || keys.ArrowRight ? 1 : 0) - (keys.KeyA || keys.ArrowLeft ? 1 : 0);'
rep(OLDFX, 'const lk = inter.locked || edR.current ? 0 : 1; const fx = lk * ((keys.KeyW || keys.ArrowUp ? 1 : 0) - (keys.KeyS || keys.ArrowDown ? 1 : 0)), sxk = lk * ((keys.KeyD || keys.ArrowRight ? 1 : 0) - (keys.KeyA || keys.ArrowLeft ? 1 : 0));')
rep('let bi = -1, bd = 3; if (rd.i < 0) for', 'let bi = -1, bd = 3; if (rd.i < 0 && !inter.active) for')

# 7 bloque por fotograma + camara
OLDCAM = 'cam.position.set(pos.x, (rd.i >= 0 ? 1.75 : 1.65) + jy + gy, pos.z); cam.rotation.set(pitch, yaw, 0);'
FRAME = r'''{ const fr = inter.update(dt); const sc = mountI >= 0 ? scoots[mountI] : null; const m = avatar.metrics; const rid = rd.i >= 0 && !!sc;
          { let dyw = yaw - lastYaw; dyw = Math.atan2(Math.sin(dyw), Math.cos(dyw)); const k = Math.min(1, dt * 10), idt = 1 / Math.max(dt, 1e-3); spd += (Math.min(Math.hypot(pos.x - lastX, pos.z - lastZ) * idt, 30) - spd) * k; yrate += (dyw * idt - yrate) * k; lastX = pos.x; lastZ = pos.z; lastYaw = yaw; }
          if (sc && (fr.phase === "APPROACH" || fr.phase === "MOUNT")) { let d = sc.g.rotation.y - Math.PI - yaw; d = Math.atan2(Math.sin(d), Math.cos(d)); yaw += d * Math.min(1, dt * 6); }
          if (plM !== m) { plM = m; plV = solveGripPlacement({ armLen: m.armLen, shoulderY: m.shoulderY, shoulderHalf: m.shoulderHalf, bar: SDEF.rig.bar, deckTopY: SDEF.rig.deckTopY, zMin: SDEF.rig.zMin, zMax: SDEF.rig.zMax, pitchMax: SDEF.rig.pitchMax, crouchMax: 0.2, torsoLen: m.torsoLen }); } const pl = plV as NonNullable<typeof plV>;
          const th = yaw + Math.PI; let ax = pos.x, az = pos.z;
          if (sc && fr.phase !== "NONE") {
            if (fr.phase === "ACTIVE") { sc.g.position.set(pos.x, jy + gy, pos.z); sc.g.rotation.y = th; sc.x = pos.x; sc.z = pos.z; }
            sc.g.updateMatrixWorld(true); const [dkx, dkz] = sw(sc.g, 0, pl.rootZ);
            if (fr.phase === "MOUNT") { const t = smooth(fr.progress); ax = pos.x + (dkx - pos.x) * t; az = pos.z + (dkz - pos.z) * t; } else if (fr.phase === "ACTIVE") { ax = dkx; az = dkz; } else if (fr.phase === "DISMOUNT") { const t = smooth(fr.progress); ax = dkx + (sideX - dkx) * t; az = dkz + (sideZ - dkz) * t; }
          }
          sctl.update(dt, { speed: rid ? spd : 0, yawRate: rid ? yrate : 0, braking: rid && !!(keys.KeyS || keys.ArrowDown), throttle: 0 }); if (sc && fr.phase !== "NONE") applyScooter(sc.g as never, sctl);
          const pose0 = anim.update(dt, { state: inter.state, movement: spd > 0.15 ? "moving" : "idle", speed: spd, turn: sctl.steerNorm, brake: sctl.brake, object: fr.objectId, poseBlend: fr.poseBlend, airborne: jy > 0.02, rideTorsoPitch: pl.torsoPitch, lean: SDEF.lean, profile: SDEF.animationProfile } as never);
          const pose = { ...pose0, hipsDrop: pose0.hipsDrop + pl.crouch * fr.poseBlend };
          if (fr.phase !== "NONE") { avatar.hands.driveWeight(fr.ikWeight, 8, dt); avatar.feet.driveWeight(fr.ikWeight, 8, dt); }
          avatar.root.position.set(ax, jy + gy, az); avatar.root.rotation.y = th;
          /* camara: primera persona <-> tercera persona (V, o automatica al subir). Se acorta si choca con edificios y se suaviza. */
          cm.blend += ((cm.third ? 1 : 0) - cm.blend) * Math.min(1, dt * 7); const bl = smooth(cm.blend);
          const bx = Math.sin(yaw) * Math.cos(pitch), bz = Math.cos(yaw) * Math.cos(pitch), by = -Math.sin(pitch); const want = rid ? 3.6 : 3.1; let allowed = want;
          for (let q = 0.4; q <= want; q += 0.4) { if (blocked(ax + bx * q, az + bz * q)) { allowed = Math.max(0.6, q - 0.5); break; } }
          cm.dist = allowed < cm.dist ? allowed : cm.dist + (allowed - cm.dist) * Math.min(1, dt * 3);
          const fy = (rid ? 1.75 : 1.65) + jy + gy, tx = ax + bx * cm.dist, tz = az + bz * cm.dist, tyy = Math.max(0.35, 1.5 + jy + gy + by * cm.dist + 0.25);
          cam.position.set(pos.x + (tx - pos.x) * bl, fy + (tyy - fy) * bl, pos.z + (tz - pos.z) * bl); cam.rotation.set(pitch, yaw, 0);
          avatar.root.visible = bl > 0.04; hands.visible = bl < 0.3; if (sc) sc.g.visible = !(fr.phase === "ACTIVE" && bl < 0.3);
          if (avatar.root.visible) avatar.update(dt, pose); }'''
rep(OLDCAM, FRAME)

# 8 HUD + editor
rep('Coger patinete eléctrico (ficticio)', 'CONDUCIR · patinete eléctrico')
rep('{ride === null && nearScoot !== null &&', '{editor && <div style={{ position: "fixed", inset: 0, zIndex: 80, background: "#0b1220" }}><AvatarEditor initial={loadAvatarLocal()} onSave={(c: AvatarConfig) => avR.current?.(c)} onClose={() => setEditor(false)} /></div>}\n      {ride === null && nearScoot !== null &&')
open(P, "w", encoding="utf-8").write(s); print("OK")
