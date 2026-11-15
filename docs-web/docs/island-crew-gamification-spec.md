# Island Crew — Especificación de gamificación

Estado: **diseño**. Lo marcado ✅ ya existe en producción; lo marcado ⏳ es propuesta pendiente de aprobación.

## 1. Jerarquía oficial
```
ISLAND CREW ID (user_id)
   ↓
ACTIVIDAD REAL (hechos verificables)
   ├─ XP ─────────→ NIVEL ─→ BADGES ─→ GOALS ─→ JOURNEYS ─→ ESPECIALIZACIONES
   ├─ REPUTACIÓN ─→ CONFIANZA
   └─ ISLAND POINTS → BENEFICIOS
```
Match score queda **fuera** de la cadena: mide compatibilidad con una oportunidad concreta.

## 2. Definiciones (una pregunta por concepto)
| Concepto | Pregunta que responde | Se gana por | Puede bajar |
|---|---|---|---|
| XP | ¿Cuánto he avanzado en Island Crew? | Hechos reales | No |
| Nivel | ¿Cuál es mi trayectoria? | XP acumulado | No |
| Reputación | ¿Puede fiarse la gente de mí? | Señales verificadas, reseñas, referencias | Sí (con motivo y derecho de réplica) |
| Match score | ¿Qué tan compatible soy con *esta* oferta? | Cálculo explicable | Sí (por oferta) |
| Island Points | ¿Qué puedo canjear? | Hechos reales | Sí (se gastan; caducidad: revisión legal) |
| Badge | ¿Qué logro concreto tengo? | Criterio explícito | No |
| Goal | ¿Qué hago ahora? | — | — |
| Journey | ¿En qué fase de mi vida en la isla estoy? | — | — |

## 3. Niveles
✅ Hoy: 7 niveles persona (0/100/400/1.000/2.000/4.000/8.000 XP), 6 empresa. **Constantes en SQL.**
⏳ Propuesta: pasar a **10 niveles** en tabla editable `levels`: New Goat, Island Starter, Island Member, Island Worker, Crew Member, Island Pro, Island Expert, Island Master, Island Legend, Island GOAT. Umbrales iniciales (a calibrar con datos reales, **estimados, no verificados**): 0, 100, 250, 500, 900, 1.500, 2.500, 4.000, 6.000, 9.000. Migrar sin bajar a nadie: el nivel nuevo se calcula del XP existente y, si saliera menor, se mantiene el mayor ya alcanzado.

## 4. Economía de XP (reglas en tabla `xp_rules`, no en código)
✅ En producción: perfil +100, email +50, isla +100, teléfono +100, identidad +200, Crew +50, operación Market +100, primer empleo +150, 1/3/6/12 meses +250/+500/+1.000/+2.000, contrato finalizado +300, empresa verificada +300, contratación +200, bonus de objetivos hasta +500.
⏳ Nuevos eventos: vivienda conseguida, Crew con acuerdo firmado, referencia recibida (solo con empleo confirmado), primera venta/alquiler. Valores a decidir tras ver datos.
Reglas fijas: sin XP por clics, refrescos, mensajes ni aperturas; un evento = una fila idempotente; empresas no compran XP.

## 5. Arquitectura del motor
```
Acción → Evento de dominio → Motor → Regla de XP → Ledger → Nivel → Badges → Elegibilidad de recompensa → Analítica
```
✅ Ledger (`xp_events`, `points_ledger`), idempotencia, servidor como autoridad.
⏳ `domain_events` + `xp_rules` + `levels` + función única `gamification_apply`. Los dos "sync" actuales leen la misma tabla de reglas.

## 6. Reputación (⏳ P1)
Señales, no nota global: empleo verificado (meses), identidad, operaciones completadas, reseñas con moderación y derecho de réplica, referencias. Se muestran como hechos ("14 meses verificados"), nunca como puntuación secreta. Para profesionales y empresas se usan **solo** hechos; el pago nunca entra. Ranking profesional → posible alto riesgo en el Reglamento europeo de IA y art. 22 RGPD: **revisión legal obligatoria** antes de activar.

## 7. Match score (⏳ P1)
Separar **restricciones duras** (disponibilidad, salario mínimo, zona máxima, fechas, habitaciones) de **preferencias blandas**. Salida: porcentaje + lista "por qué" (✓ 4/5 habilidades, ✓ disponibilidad…). Prohibido usar rasgos protegidos. Siempre explicable.

## 8. Goals y siguiente mejor acción
✅ 13 objetivos, `goals_sync`, tarjeta "siguiente paso" (primer objetivo pendiente por orden de catálogo).
⏳ `next_best_action` en servidor con contexto: perfil incompleto → completar; con trabajo sin vivienda → buscar vivienda; con Crew → revisar encajes; con vivienda → explorar Market. Una sola.

## 9. Journeys (⏳ P1)
Cuatro journeys con máquina de estados única cada uno:
- Trabajo: Perfil → Match → Candidatura → Entrevista → Empleo → 1/3/6/12 meses.
- Vivienda: Perfil → Búsqueda → Crew → Propiedad → Contacto → Visita → Solicitud → Vivienda. Estados: Saved, Contacted, Interested, Visit scheduled, Visited, Negotiating, Application, Approved/Rejected, Rented.
- Crew: Crear → Invitar → Compatibilidad → Acuerdo → Búsqueda → Casa.
- Market: Publicar → Interés → Chat → Transacción → Entrega → Completar → Reseña.
Journey = vista de hechos existentes; no concede XP por sí mismo.

## 10. Especializaciones
✅ Barras por área (Trabajo, Vivienda, Crew, Market, Comunidad) = objetivos cumplidos / totales. Sin áreas inventadas.

## 11. Badges
✅ 10 badges con criterio, descripción y fecha. ⏳ Añadir `rarity` solo si es real (porcentaje de usuarios que lo tiene, calculado), nunca decorativa.

## 12. Island Points y partners (⏳ P2)
Moneda de fidelización, no dinero, no transferible, sin conversión. Beneficios apagados hasta tener partners reales verificados. Pendiente legal: condiciones del programa, caducidad, fiscalidad, consentimiento de marketing (LSSI/ePrivacy), protección del consumidor.

## 13. Empresas
Nivel de empleador + reputación de empleador (hechos: contrataciones confirmadas, verificación) + badges. Se puede comprar visibilidad, herramientas y analítica **etiquetada como pagada**; nunca reputación.

## 14. El Goat
Narrador de progreso, no chatbot obligatorio. Estados: idle, happy, encouraging, thinking, celebrating, level-up, success, warning. Un solo componente con estado; hoy existen tres implementaciones que hay que unificar. Rive/Lottie solo si una medición justifica el coste. Animación de subida de nivel ≤ 2 s, saltable, sin movimiento con `prefers-reduced-motion`.

## 15. Anti-abuso
Idempotencia por clave única (✅), límites diarios (✅ en eventos), XP solo desde empleo con empresa verificada y confirmado por ambas partes (✅), logs de auditoría (⏳), correcciones manuales con motivo (⏳), detección de anomalías (⏳), reseñas solo con operación completada (⏳ comprobar).

## 16. Feature flags (⏳ completar)
✅ `goals`, `next_action`, `benefits`. ⏳ `gamification_enabled`, `points_enabled`, `badges_enabled`, `goat_enabled`, `level_up_animation_enabled`, `marketplace_rewards_enabled`, `partner_rewards_enabled`.

## 17. Analítica
✅ 4 eventos (`goals_view`, `goal_click`, `nba_click`, `level_view`). ⏳ Eventos de resultado: `job_hired`, `employment_month_N`, `housing_success`, `crew_agreement_completed`, `marketplace_transaction_completed`, `xp_earned`, `level_up`, `badge_earned`. Métrica de éxito = empleo y vivienda conseguidos, no clics.

## 18. Admin (⏳ ampliar `/admin/gamification`)
✅ Flags, edición de objetivos, resumen. ⏳ Reglas de XP, niveles, badges, ledger por usuario con "¿por qué tiene este nivel?", actividad sospechosa, correcciones con auditoría.

## 19. Legal y privacidad (a revisar por abogado)
RGPD (perfilado, art. 22, datos de empleo), reglamento de IA (clasificación de herramientas de selección), programa de puntos, reseñas y derecho de réplica, seguros (Island Crew no es aseguradora: solo vía corredor/MGA autorizados), pagos y depósitos, comisiones.

## 20. Qué NO construir
Leaderboard global, rachas punitivas, XP por actividad, pérdida de nivel, puntos canjeables sin partners reales, reputación de pago, sonido por defecto, 3D decorativo, confeti generalizado.
