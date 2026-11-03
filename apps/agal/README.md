# Agal

Single Flutter app for all three Agal roles -- Farmer, Supplier/Aggregator,
Buyer/Exporter. After login, the backend-assigned `role` on the user decides
which navigation shell the app shows (see `lib/core/routes/`).

## Architecture

- **State management & DI**: GetX (`get`). Core singletons (`AppDatabase`, `Dio`, `AgalApiClient`, `AuthController`, `SyncService`, `SyncScheduler`, `ThemeController`) are registered once via `Get.put(..., permanent: true)` in `main()`, before `runApp` -- see `lib/main.dart`. Screens read them with `Get.find<T>()`.
- **Routing**: GetX's own router (`GetMaterialApp` + `GetPage`), defined in `lib/core/routes/app_pages.dart`. `AuthMiddleware` (`lib/core/routes/auth_middleware.dart`) is a defense-in-depth guard against direct navigation to the wrong route, but the actual login/logout transitions are driven explicitly by `AuthController.login()`/`logout()` calling `Get.offAllNamed(...)` -- GetX middleware only re-evaluates on navigation, not reactively when `session` changes on its own, so relying on it alone would leave you on a blank screen after logout, or with a previous role's screens still sitting in the stack after logging in as someone else.
- **Networking**: `dio`, wrapped in `lib/data/remote/agal_api_client.dart`. The auth token is attached per-request by an interceptor (`lib/core/network/dio_client.dart`) that reads the *current* session fresh on each call.
- **Session**: JWT + user info persisted via `flutter_secure_storage`, loaded once at startup by `AuthController` (`lib/core/auth/auth_controller.dart`) -- awaited in `main()` *before* `runApp`, so there's no splash screen needed to hide the gap.
- **Theme**: Material 3, seeded from the same teal accent as the marketing site (`lib/core/theme/app_theme.dart`). Light/dark/system is user-selectable in Settings and persisted via `get_storage` (`lib/core/theme/theme_controller.dart`).

### Farmer role: offline-first

Only the Farmer role uses a local database -- Supplier and Buyer assume
normal connectivity and call the REST API directly (see
`lib/features/supplier/`, `lib/features/buyer/`).

- **Local DB**: Drift (`lib/data/local/`), three tables:
  - `LocalBatches` -- read-model projection of a batch's current state (mirrors the backend's `harvest_batches`).
  - `LocalCustodyEvents` -- immutable, append-only log of everything that happens to a batch (mirrors the backend's `custody_events`).
  - `LocalMessages` -- outgoing chat messages composed while offline (see Chat below).
  - `LocalCustodyEvents` and `LocalMessages` together **are** the offline sync queue: any row with `synced = false` is waiting to be pushed.
- **Why event-sourced, not "edit a row and resolve conflicts on sync"**: see `backend/README.md`'s "Why event-sourced" section -- the same reasoning applies on-device. Every farmer action (harvest, drying started/completed, handoff, message, note) is a new event with a client-generated UUID; nothing is ever mutated in place, so replaying a sync is naturally idempotent and there's no conflict to resolve.
- **Sync**: `lib/data/sync/sync_service.dart` posts unsynced events and messages together in one `POST /sync` call, and marks them synced once the server acknowledges (`"created"` or `"duplicate"` both count). `lib/data/sync/sync_scheduler.dart` triggers this on a timer, whenever connectivity is regained, and on demand (a "Sync now" button in Settings), for as long as the app process is alive. This is **not** OS-level background execution (no WorkManager/BGTaskScheduler) -- a deliberate scope cut for the scaffold; add `workmanager` later if syncing while the app is fully killed turns out to matter.

## Bottom navigation (`lib/features/shared/role_shell.dart`)

Each role lands on a persistent bottom-nav shell after login, with
different tabs reflecting what that role actually does -- not the same
layout with relabeled buttons:

- **Farmer**: Home (a quick-glance dashboard: sync status, batch counts, a "log new harvest" shortcut), Messages, Harvest (the working batch list -- what used to be the sole home screen), Settings.
- **Supplier**: Home (the incoming-inventory dashboard: ready-for-pickup / my-inventory), Messages, Verification, Settings.
- **Buyer**: Home (the marketplace: available / my-purchases), Messages, Verification, Settings.

`RoleShell` hosts the tabs in an `IndexedStack` (so switching tabs doesn't
lose scroll position or re-fetch data) under a `NavigationBar`; each tab
widget keeps its own `Scaffold`/`AppBar`. Detail screens (a batch, a chat
thread, a settings sub-page) are still pushed full-screen on top of the
shell via `Get.toNamed`, which hides the bottom nav until you go back --
there's no nested per-tab navigation stack.

## Settings (`lib/features/settings/`)

A tab in every role's shell: account details (edit name/phone/municipality
via `PATCH /users/me`), theme mode, offline sync status (Farmer only),
About (app info + version via `package_info_plus`), Terms of Use, Privacy
Policy, and open-source licenses (Flutter's built-in `showLicensePage`).
Logging out lives here too, behind a confirmation dialog.

## Verification (`lib/features/shared/verification_screen.dart`)

A Supplier/Buyer-only tab: paste any batch ID to jump straight to its
chain-of-custody history, or pick one from "your batches" (whatever you
currently hold). The history screen itself
(`lib/features/shared/batch_history_screen.dart`) is where the actual
on-chain check happens -- a "Verify on Sepolia" action per anchored event
calls `GET /custody-events/{id}/verify`, which independently recomputes
the event's hash and compares it against what the live `HarvestLedger`
contract on Sepolia actually reports, not just the backend's own cached
`on_chain_status` column. A mismatch is surfaced as a hard warning
("this history may have been altered"), not just a quiet failure.

## Chat (`lib/features/chat/`)

Direct messaging between any two accounts, regardless of role --
`lib/features/chat/chat_list_screen.dart` (inbox), `contact_picker_screen.dart`
(start a new conversation from the user directory), and
`chat_thread_screen.dart` (the conversation itself). Backed by the same
append-only, client-generated-id pattern as custody events (see
`backend/README.md`): a Farmer's outgoing messages queue in `LocalMessages`
and sync like everything else; Supplier/Buyer send directly online.

Each thread also has a **"send via SMS" fallback**: a button that opens the
device's own SMS app with the recipient's number and the typed message
pre-filled (`url_launcher`'s `sms:` scheme), for reaching someone over the
phone network when only cell signal -- not data -- is available. This is
deliberately *not* silent/automatic SMS sending: Android's SEND_SMS/RECEIVE_SMS
permissions are Play Store Restricted Permissions generally reserved for
default SMS apps, and iOS has no API for a third-party app to send texts at
all. Launching the system SMS composer needs no special permission on either
platform (Android does need the `<queries>` entry for the `sms:` scheme
declared in `android/app/src/main/AndroidManifest.xml`, for package-visibility
reasons on Android 11+).

## Location & maps

Logging a harvest no longer takes a typed address -- `LocationPicker`
(`lib/features/shared/location_picker.dart`) captures the device's current
GPS position automatically (via `geolocator`) and shows it on a small,
draggable-pin Google Map (`google_maps_flutter`), so a farmer can nudge the
pin if the fix is slightly off. The batch detail screen shows the same
location as a small static map. Coordinates are stored as
`harvest_latitude`/`harvest_longitude` (see `backend/README.md`), not a
free-text field.

Requires a Google Maps API key:

- **Android**: put `MAPS_API_KEY=<your key>` in `android/local.properties` (gitignored, never committed). `app/build.gradle.kts` reads it and injects it into `AndroidManifest.xml`'s `com.google.android.geo.API_KEY` meta-data via a manifest placeholder.
- **iOS**: not wired yet -- iOS is a later platform target (see `apps/agal`'s role in the overall roadmap). When it becomes active, add `GMSServices.provideAPIKey(...)` in `ios/Runner/AppDelegate.swift`; `NSLocationWhenInUseUsageDescription` is already set in `Info.plist`.

## Logo & app icon

`assets/agal_light.jpg` / `assets/agal_dark.jpg` are the two logo variants.
`AppLogo` (`lib/features/shared/app_logo.dart`) picks whichever matches the
current theme brightness wherever the logo appears in-app (Login, About).
The app's *launcher icon* always uses the dark variant regardless of theme,
since home-screen icons don't follow in-app theming -- configured via
`flutter_launcher_icons` in `pubspec.yaml`. After swapping either source
image, regenerate with:

```bash
dart run flutter_launcher_icons
```

## Running

```bash
flutter pub get
dart run build_runner build --delete-conflicting-outputs   # regenerate lib/data/local/database.g.dart after touching tables.dart
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000  # 10.0.2.2 = Android emulator's host loopback
```

For a physical device, point `API_BASE_URL` at your machine's LAN IP instead.

## Testing note

`flutter test` on this machine hangs on any widget tree that reaches
`AuthController`'s startup read from `flutter_secure_storage` -- the plugin's
real platform channel has no implementation under `flutter_tester` and, on
Linux, ends up blocking rather than throwing. `test/widget_test.dart` avoids
this by rendering `LoginScreen` directly (it only touches GetX-registered
singletons inside `_submit()`, never during `build()`), rather than booting
the full `AgalApp`.
