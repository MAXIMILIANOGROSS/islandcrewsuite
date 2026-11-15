# Inventario de formularios e interfaces con campos de entrada

Generado automáticamente por búsqueda en el código (`<form|<input|<textarea|<select`). **Es un inventario de archivos, no una validación funcional.** Columna «Destino» = tablas/RPC/API que el archivo usa. «Clase» es una heurística por nombre de ruta; hay que revisar a mano antes de migrar.

Total de archivos con campos: **113** · páginas en src/app: **145**

| Clase | Archivo | Ruta | Campos | Destino de datos | PDF |
|---|---|---|---|---|---|
| admin | app/admin/agentes/page.tsx | /admin/agentes | 6 | rpc:aos_agents, rpc:aos_cycle_preview, rpc:aos_overview, rpc:aos_runs, rpc:aos_task_drafts, rpc:aos_tasks, /api/agentes-borrador, /api/agentes-ejecutar, /api/ia-estado | — |
| admin | app/admin/cabra/page.tsx | /admin/cabra | 1 | rpc:aos_task_create, /api/cabra | — |
| admin | app/admin/denuncias/page.tsx | /admin/denuncias | 2 | content_reports, privacy_requests, rpc:net_report_attachment, rpc:net_report_resolve, rpc:net_reports_admin, rpc:net_room_report_resolve, rpc:net_room_reports_admin, /api/legal-resolve | — |
| admin | app/admin/gamification/page.tsx | /admin/gamification | 11 | gamification_flags, goals_catalog, launch_gate, levels, xp_rules, rpc:gam_admin_stats, rpc:gam_explain_user, rpc:gam_flag_set, rpc:gam_goal_save, rpc:gam_level_save, rpc:gam_rule_save, rpc:gate_set | — |
| admin | app/admin/housing/page.tsx | /admin/housing | 2 | housing_cases, housing_reports, rpc:housing_demand, rpc:housing_funnel, rpc:housing_stats | — |
| admin | app/admin/housing/properties/page.tsx | /admin/housing/properties | 9 | housing_audit, properties, property_interests, property_private, rpc:property_interests_admin, rpc:property_moderate | — |
| admin | app/admin/identidad/page.tsx | /admin/identidad | 1 | business_accounts, rpc:admin_find_user, rpc:business_verify, rpc:trust_set, rpc:trust_summary | — |
| admin | app/admin/incidencias/page.tsx | /admin/incidencias | 1 | moderation_cases, rpc:moderation_resolve | — |
| admin | app/admin/leads/page.tsx | /admin/leads | 1 | leads | — |
| admin | app/admin/limpieza/page.tsx | /admin/limpieza | 1 | rpc:net_orphan_photos, rpc:net_retention_preview, rpc:net_retention_run | — |
| admin | app/admin/marketplace/page.tsx | /admin/marketplace | 4 | market_demand, market_disputes, market_items, market_reports, rpc:market_admin_stats, rpc:market_moderate | — |
| admin | app/admin/negocio/page.tsx | /admin/negocio | 3 | rpc:biz_dashboard, rpc:plan_set | — |
| admin | app/admin/npcs/page.tsx | /admin/npcs | 3 | /api/npc | — |
| admin | app/admin/world/page.tsx | /admin/world | 18 | destinations, hotspots, world_content_sources, zones | — |
| chat/IA | components/AiFaqChat.tsx |  | 1 | /api/goat-chat | — |
| chat/IA | components/ConversationScreen.tsx |  | 1 | /api/npc-group | — |
| chat/IA | components/NpcChat.tsx |  | 1 | cvs, /api/npc | — |
| chat/IA | components/VenueChat.tsx |  | 1 | rpc:venue_chat_send, rpc:venue_chat_thread, /api/venue-borrador | — |
| chat/IA | components/chat/ChatView.tsx |  | 1 | — | — |
| chat/IA | components/life/CompanionChat.tsx |  | 16 | /api/life-listen | — |
| chat/IA | components/life/SoulGuideChat.tsx |  | 1 | /api/soul-chat | — |
| formulario | app/asistente/page.tsx | /asistente | 1 | /api/assistant | — |
| formulario | app/crearcurriculum/page.tsx | /crearcurriculum | 28 | cvs, profiles, terms_acceptances, worker_profiles | sí |
| formulario | app/cuenta/page.tsx | /cuenta | 1 | cvs, interviews, matches, offers, profiles, rpc:delete_my_account | sí |
| formulario | app/denunciar/page.tsx | /denunciar | 7 | rpc:report_content, /api/legal-notify | — |
| formulario | app/editar-perfil/page.tsx | /editar-perfil | 11 | profiles, restaurant_profiles, terms_acceptances, worker_profiles, rpc:set_employer_visibility | — |
| formulario | app/empresa/[id]/candidaturas/page.tsx | /empresa/[id]/candidaturas | 1 | job_vacancies, rpc:jobs_applications_for, rpc:jobs_mark_reviewed, rpc:jobs_set_status | — |
| formulario | app/empresa/[id]/page.tsx | /empresa/[id] | 4 | business_accounts, business_audit, business_members, employment_records, market_items, profiles_public, rpc:business_member_add, rpc:business_member_remove, rpc:employment_act, rpc:employment_create | — |
| formulario | app/empresa/[id]/vacantes/page.tsx | /empresa/[id]/vacantes | 5 | job_vacancies | — |
| formulario | app/empresa/mensajes/page.tsx | /empresa/mensajes | 1 | rpc:my_claimed_venues, rpc:venue_chat_close, rpc:venue_chat_inbox | — |
| formulario | app/empresa/mi-local/page.tsx | /empresa/mi-local | 5 | rpc:my_claimed_venues, rpc:my_venue_claims, rpc:set_venue_hiring, rpc:venue_claim_request | — |
| formulario | app/empresa/nueva/page.tsx | /empresa/nueva | 2 | restaurant_profiles, rpc:business_claim_legacy, rpc:business_create | — |
| formulario | app/empresa/panel/page.tsx | /empresa/panel | 12 | rpc:my_claimed_venues, rpc:venue_hub_admin, rpc:venue_offer_delete, rpc:venue_offer_save, rpc:venue_profile_save, rpc:venue_request_answer, rpc:venue_requests_for, rpc:venue_stats | — |
| formulario | app/empresa/reclamar/page.tsx | /empresa/reclamar | 2 | business_members, rpc:business_claim_request | — |
| formulario | app/empresas/talento/page.tsx | /empresas/talento | 2 | profiles, terms_acceptances, rpc:company_ranking, rpc:employer_talent | — |
| formulario | app/housing/alerts/page.tsx | /housing/alerts | 3 | housing_alerts, housing_waitlist | — |
| formulario | app/housing/companeros/page.tsx | /housing/companeros | 2 | housing_blocks, housing_reports, rpc:housing_candidates, rpc:housing_request | — |
| formulario | app/housing/grupo/[id]/page.tsx | /housing/grupo/[id] | 15 | housing_agreement_acceptances, housing_agreements, housing_group_messages, housing_groups, housing_listings, housing_poll_votes, housing_polls, rpc:housing_group_invite, rpc:housing_group_leave, rpc:housing_group_people, rpc:housing_my_connections, rpc:housing_new_agreement | — |
| formulario | app/housing/grupo/page.tsx | /housing/grupo | 3 | rpc:housing_create_group, rpc:housing_group_invite, rpc:housing_group_respond, rpc:housing_my_groups | — |
| formulario | app/housing/perfil/page.tsx | /housing/perfil | 6 | housing_profiles, terms_acceptances, worker_profiles | — |
| formulario | app/housing/property/[id]/page.tsx | /housing/property/[id] | 2 | housing_group_members, housing_listings, housing_profiles, properties, properties_public, property_favorites, property_interests, property_reports | — |
| formulario | app/housing/seguridad/page.tsx | /housing/seguridad | 1 | housing_reports | — |
| formulario | app/housing/viviendas/nueva/page.tsx | /housing/viviendas/nueva | 8 | properties, property_favorites, rpc:property_owner_publish | — |
| formulario | app/housing/viviendas/page.tsx | /housing/viviendas | 6 | properties_public, property_favorites | — |
| formulario | app/login/page.tsx | /login | 6 | terms_acceptances | — |
| formulario | app/marketplace/[id]/page.tsx | /marketplace/[id] | 5 | market_favorites, market_items, market_items_public, market_reports, rpc:market_contact, rpc:market_order_create, rpc:market_rental_request | — |
| formulario | app/marketplace/mine/page.tsx | /marketplace/mine | 6 | market_handovers, market_items, market_orders, market_rentals, market_reviews, rpc:market_dispute_open, rpc:market_handover_add, rpc:market_publish, rpc:market_review_add | — |
| formulario | app/marketplace/page.tsx | /marketplace | 8 | market_categories, market_favorites, market_items_public | — |
| formulario | app/marketplace/sell/page.tsx | /marketplace/sell | 8 | business_members, market_categories, market_items, profiles, rpc:market_publish | — |
| formulario | app/marketplace/wanted/page.tsx | /marketplace/wanted | 6 | market_categories, market_wanted, market_wanted_public | — |
| formulario | app/matches/[id]/page.tsx | /matches/[id] | 1 | — | — |
| formulario | app/mundo/jugar/page.tsx | /mundo/jugar | 1 | market_items_public, rpc:housing_is_admin, rpc:ic_game_load, rpc:ic_game_save, rpc:world_destinations, rpc:world_discover, rpc:world_discovery_stats, rpc:world_hotspots, rpc:world_vacancies | — |
| formulario | app/mundo/page.tsx | /mundo | 3 | rpc:world_destinations, rpc:world_hotspots, rpc:world_vacancies | — |
| formulario | app/mundo/real/page.tsx | /mundo/real | 1 | market_items_public, rpc:ic_game_load, rpc:ic_game_save, rpc:world_destinations, rpc:world_vacancies | — |
| formulario | app/npc-factory/page.tsx | /npc-factory | 6 | npc_custom, rpc:npc_custom_delete, rpc:npc_custom_save, /api/npc-crear | — |
| formulario | app/onboarding/page.tsx | /onboarding | 4 | profiles, restaurant_profiles, worker_profiles | — |
| formulario | app/recuperar-contrasena/page.tsx | /recuperar-contrasena | 1 | — | — |
| formulario | app/restablecer-contrasena/page.tsx | /restablecer-contrasena | 2 | — | — |
| formulario | app/valorar/page.tsx | /valorar | 1 | rpc:my_rateable_restaurants, rpc:rate_restaurant | — |
| formulario | app/verificar/page.tsx | /verificar | 2 | — | — |
| formulario | app/vida/page.tsx | /vida | 6 | — | — |
| formulario | components/AccountGate.tsx |  | 2 | terms_acceptances, rpc:delete_my_account | — |
| formulario | components/Bienvenida.tsx |  | 1 | terms_acceptances | — |
| formulario | components/CabraMaestraHero.tsx |  | 1 | profiles, /api/goat-chat | — |
| formulario | components/CabraVida.tsx |  | 1 | profiles, rpc:cabra_mem_forget, /api/goat-chat | — |
| formulario | components/CareerLayer.tsx |  | 5 | — | — |
| formulario | components/ChoiceSelect.tsx |  | 1 | — | — |
| formulario | components/CrewTab.tsx |  | 2 | — | — |
| formulario | components/DealPanel.tsx |  | 8 | — | — |
| formulario | components/FomoGlobe.tsx |  | 1 | /api/fires, /api/flights, /api/ships | — |
| formulario | components/GameLayer.tsx |  | 3 | rpc:game_award, rpc:ic_friend_request, rpc:ic_friends, rpc:ic_me | — |
| formulario | components/GameRanking.tsx |  | 2 | rpc:game_my_player, rpc:game_my_stats, rpc:game_set_player | — |
| formulario | components/LeadForm.tsx |  | 4 | — | — |
| formulario | components/LivePanel.tsx |  | 4 | rpc:net_connect, rpc:net_my_profile, rpc:ps_delete | — |
| formulario | components/MiMemoria.tsx |  | 2 | rpc:cabra_mem_forget, rpc:cabra_mem_get | — |
| formulario | components/NavSelect.tsx |  | 1 | — | — |
| formulario | components/PrivacyRequestForm.tsx |  | 3 | rpc:request_privacy_right, /api/legal-notify | — |
| formulario | components/RadioPanel.tsx |  | 1 | — | — |
| formulario | components/RealTownWorld.tsx |  | 1 | claimed_venues, player_crew, rpc:attest_adult, rpc:drop_cv, rpc:game_complete_mission, rpc:game_my_progress, rpc:ps_save, rpc:set_pvp_enabled, rpc:venues_hiring | — |
| formulario | components/SocialPanel.tsx |  | 5 | — | — |
| formulario | components/VenueHR.tsx |  | 2 | cvs, rpc:drop_cv, /api/cv-send | — |
| formulario | components/VenueOffers.tsx |  | 4 | rpc:venue_hub_public, rpc:venue_request_create, rpc:venue_track | — |
| formulario | components/WorldCall.tsx |  | 1 | — | — |
| formulario | components/WorldNetwork.tsx |  | 2 | rpc:jobs_list, rpc:net_create_post, rpc:net_feed | — |
| formulario | components/ZonePresence.tsx |  | 1 | rpc:net_connect, rpc:net_my_profile | — |
| formulario | components/housing/CrewExtras.tsx |  | 4 | housing_visits, rpc:housing_group_decide, rpc:housing_group_requests, rpc:housing_invite_create | — |
| formulario | components/housing/PhotoUploader.tsx |  | 2 | property_photos, rpc:property_set_cover | — |
| formulario | components/life/LifeArquetipos.tsx |  | 2 | — | — |
| formulario | components/life/LifeCouncil.tsx |  | 3 | /api/life-council | — |
| formulario | components/life/LifeExplore.tsx |  | 1 | — | — |
| formulario | components/life/LifeHabits.tsx |  | 2 | — | — |
| formulario | components/life/LifeJournal.tsx |  | 10 | — | — |
| formulario | components/life/LifeKnow.tsx |  | 10 | — | — |
| formulario | components/life/LifeNutrition.tsx |  | 6 | — | — |
| formulario | components/life/LifePurpose.tsx |  | 8 | — | — |
| formulario | components/life/LifeTools.tsx |  | 2 | — | — |
| formulario | components/life/LifeVault.tsx |  | 2 | — | — |
| formulario | components/life/LocalAiCard.tsx |  | 1 | — | — |
| formulario | components/life/ReflectUI.tsx |  | 4 | — | — |
| formulario | components/life/SearchPanel.tsx |  | 1 | — | — |
| formulario | components/life/SoulCouncil.tsx |  | 2 | /api/soul-council | — |
| formulario | components/life/SoulEngine.tsx |  | 12 | — | sí |
| formulario | components/life/SoulLab.tsx |  | 3 | — | — |
| formulario | components/life/SoulMap.tsx |  | 5 | — | sí |
| formulario | components/life/SoulMe.tsx |  | 2 | — | — |
| formulario | components/life/SoulMeditate.tsx |  | 5 | — | — |
| formulario | components/market/MarketPhotoUploader.tsx |  | 2 | market_item_photos, rpc:market_set_cover | — |
| formulario | components/market/ShareToCrew.tsx |  | 2 | crew_market_items, housing_group_members | — |
| formulario | components/network/CrewPlusInterest.tsx |  | 4 | rpc:plus_my_interest, rpc:plus_register_interest | — |
| formulario | components/network/JobsBoard.tsx |  | 6 | rpc:jobs_apply, rpc:jobs_list, rpc:jobs_my_applications, rpc:jobs_report, rpc:jobs_withdraw | — |
| formulario | components/network/NetworkApp.tsx |  | 20 | rpc:net_attach_media, rpc:net_comment, rpc:net_comments_of, rpc:net_create_post, rpc:net_delete_message, rpc:net_feed, rpc:net_inbox, rpc:net_my_hidden, rpc:net_my_network, rpc:net_my_profile, rpc:net_notifications_list, rpc:net_notifications_read, rpc:net_notifications_unread, rpc:net_post_extra, rpc:net_post_media_of, rpc:net_react_message, rpc:net_report_message, rpc:net_save_profile, rpc:net_search_people | — |
| formulario | components/network/ProfileItems.tsx |  | 6 | rpc:net_item_delete, rpc:net_item_save, rpc:net_items_of | — |
| formulario | components/network/Rooms.tsx |  | 6 | rpc:net_room_delete_message, rpc:net_room_invite_answer, rpc:net_room_invites_mine, rpc:net_room_join, rpc:net_room_leave, rpc:net_room_report, rpc:net_room_send, rpc:net_room_thread, rpc:net_rooms_list | — |
