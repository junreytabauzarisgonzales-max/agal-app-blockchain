import 'dart:convert';
import 'dart:io';
import 'dart:ui' as ui;
import 'package:drift/native.dart';
import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter/services.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get/get.dart';
import 'package:get_storage/get_storage.dart';
import 'package:agal/core/auth/auth_controller.dart';
import 'package:agal/core/auth/session.dart';
import 'package:agal/core/models/enums.dart';
import 'package:agal/core/theme/app_theme.dart';
import 'package:agal/data/local/database.dart';
import 'package:agal/data/remote/agal_api_client.dart';
import 'package:agal/data/sync/sync_scheduler.dart';
import 'package:agal/data/sync/sync_service.dart';
import 'package:agal/features/farmer/farmer_dashboard_screen.dart';
import 'package:agal/features/farmer/farmer_create_batch_screen.dart';
import 'package:agal/features/chat/chat_thread_screen.dart';
import 'package:agal/features/shared/buying_prices_screen.dart';
import 'package:agal/features/shared/batch_history_screen.dart';
import 'package:agal/features/shared/sourcing_screen.dart';
import 'package:agal/features/supplier/supplier_home_screen.dart';
import 'package:agal/features/supplier/shipments_screen.dart';
import 'package:agal/features/supplier/shipment_service.dart';
import 'support/demo_data.dart';

const captureScreenshots = bool.fromEnvironment('CAPTURE_SCREENSHOTS');
final captureKey = GlobalKey();

class DemoSync extends SyncScheduler {
  DemoSync(super.service, super.db, super.auth) {
    online.value = false; pendingHarvests.value = 2; pendingMessages.value = 1;
  }
  @override
  void start() {}
  @override
  Future<void> refreshCounts() async {}
  @override
  Future<void> syncNow() async {}
}

Future<void> showScreen(WidgetTester tester, Widget screen, {bool navigation = true}) async {
  await tester.pumpWidget(const SizedBox.shrink());
  await tester.pumpWidget(GetMaterialApp(debugShowCheckedModeBanner: false, theme: AppTheme.dark,
    home: RepaintBoundary(key: captureKey, child: Scaffold(
      body: Column(children: [Container(height: 28, color: AgalColors.deep, padding: const EdgeInsets.symmetric(horizontal: 22),
        child: const Row(children: [Text('9:41', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600)), Spacer(),
          Icon(Icons.signal_cellular_alt, size: 13), SizedBox(width: 5), Icon(Icons.wifi, size: 13), SizedBox(width: 5), Icon(Icons.battery_full, size: 14)])),
        Expanded(child: screen)]),
      bottomNavigationBar: !navigation ? null : NavigationBar(selectedIndex: 0, destinations: const [
        NavigationDestination(icon: Icon(Icons.home_outlined), label: 'Home'),
        NavigationDestination(icon: Icon(Icons.inventory_2_outlined), label: 'Batches'),
        NavigationDestination(icon: Icon(Icons.chat_bubble_outline), label: 'Messages'),
        NavigationDestination(icon: Icon(Icons.person_outline), label: 'Profile'),
      ]),
    ))));
  await tester.pumpAndSettle();
  await tester.runAsync(() async {
    await precacheImage(const AssetImage('assets/agal_dark.jpg'), captureKey.currentContext!);
  });
  await tester.pumpAndSettle();
  expect(tester.takeException(), isNull);
}

Future<void> capture(WidgetTester tester, String name) async {
  if (!captureScreenshots) return;
  await tester.pump();
  await tester.runAsync(() async {
    final boundary = captureKey.currentContext!.findRenderObject()! as RenderRepaintBoundary;
    final image = await boundary.toImage(pixelRatio: 3);
    final bytes = await image.toByteData(format: ui.ImageByteFormat.png);
    final directory = Directory('../../screenshots/raw');
    await directory.create(recursive: true);
    await File('${directory.path}/$name.png').writeAsBytes(bytes!.buffer.asUint8List());
    image.dispose();
  });
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  late AppDatabase db;
  late DemoApi api;
  late AuthController auth;
  setUpAll(() async {
    final folder = await Directory(r'C:\Users\ADMIN\AppData\Local\Temp\opencode').create(recursive: true);
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger.setMockMethodCallHandler(
      const MethodChannel('plugins.flutter.io/path_provider'), (_) async => folder.path);
    await GetStorage('GetStorage', folder.path).initStorage;
    if (Platform.isWindows) {
      final loader = FontLoader('Roboto');
      for (final name in ['segoeui.ttf', 'segoeuib.ttf']) {
        loader.addFont(Future.value(ByteData.sublistView(await File('C:/Windows/Fonts/$name').readAsBytes())));
      }
      await loader.load();
      await (FontLoader('MaterialIcons')..addFont(rootBundle.load('fonts/MaterialIcons-Regular.otf'))).load();
    }
  });
  setUp(() async {
    Get.testMode = true;
    db = AppDatabase.forTesting(NativeDatabase.memory());
    api = DemoApi();
    auth = AuthController(const FlutterSecureStorage());
    Get.put<AuthController>(auth);
    Get.put<AppDatabase>(db);
    Get.put<AgalApiClient>(api);
    Get.put<SyncScheduler>(DemoSync(SyncService(db, api), db, auth));
    Get.put<ShipmentService>(ShipmentService(api));
    auth.session.value = const Session(userId: farmerId, email: 'junrey@example.test', fullName: 'Junrey Gonzales', role: UserRole.farmer,
      municipality: 'Bongao, Tawi-Tawi', accessToken: 'mock-token');
  });
  tearDown(() async { await db.close(); Get.reset(); });

  testWidgets('farmer offline harvest, prices and SMS screenshots', (tester) async {
    tester.view.physicalSize = const Size(828, 1792); tester.view.devicePixelRatio = 2;
    addTearDown(tester.view.resetPhysicalSize); addTearDown(tester.view.resetDevicePixelRatio);
    await tester.runAsync(() => db.insertBatchCreated(id: batchId, farmerId: farmerId, species: 'Eucheuma Cottonii (Sakol)',
      estimatedWeightKg: 180, unit: 'kg', harvestedAt: DateTime(2026, 11, 3, 8, 21), payloadJson: jsonEncode({'species': 'Eucheuma Cottonii (Sakol)', 'estimated_weight_kg': 180, 'unit': 'kg'})));
    await showScreen(tester, const FarmerDashboardScreen());
    expect(find.text('Junrey Gonzales'), findsOneWidget);
    expect(find.textContaining('Offline mode'), findsOneWidget);
    await capture(tester, 'farmer_dashboard');
    await showScreen(tester, const FarmerCreateBatchScreen(), navigation: false);
    await tester.enterText(find.byType(TextFormField), '180');
    FocusManager.instance.primaryFocus?.unfocus(); await tester.pumpAndSettle();
    await capture(tester, 'farmer_log_harvest_offline');
    await showScreen(tester, const BuyingPricesScreen());
    expect(find.textContaining('55.00'), findsOneWidget);
    await capture(tester, 'farmer_buying_prices');
    await showScreen(tester, const ChatThreadScreen(counterpartId: traderId), navigation: false);
    await tester.enterText(find.byType(TextField), 'Bongao Port. I am offline — I will send the location by SMS.');
    FocusManager.instance.primaryFocus?.unfocus(); await tester.pumpAndSettle();
    expect(find.text('Send via SMS'), findsOneWidget);
    await capture(tester, 'farmer_sms_chat');
    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pumpAndSettle();
  });

  testWidgets('trader sales, inventory and shipment screenshots', (tester) async {
    tester.view.physicalSize = const Size(828, 1792); tester.view.devicePixelRatio = 2;
    addTearDown(tester.view.resetPhysicalSize); addTearDown(tester.view.resetDevicePixelRatio);
    auth.session.value = const Session(userId: traderId, email: 'hamsya@example.test', fullName: 'Hamsya Igasan', role: UserRole.supplier, accessToken: 'mock-token');
    await showScreen(tester, const SupplierHomeScreen());
    expect(find.text('Hamsya Igasan'), findsOneWidget);
    await capture(tester, 'supplier_dashboard');
    await showScreen(tester, const ShipmentsScreen(), navigation: false);
    await tester.enterText(find.byType(TextField), 'Krishane Ann Remonde · Zamboanga warehouse');
    await tester.tap(find.byType(CheckboxListTile).at(0));
    await tester.tap(find.byType(CheckboxListTile).at(1));
    FocusManager.instance.primaryFocus?.unfocus(); await tester.pumpAndSettle();
    expect(find.text('400 kg'), findsOneWidget);
    await capture(tester, 'supplier_bundle_shipment');
    await tester.tap(find.text('Create Shipment'));
    await tester.pumpAndSettle();
    expect(api.writes.length, 2);
    expect(api.writes.every((e) => e['event_type'] == 'note_added'), isTrue);
    expect(find.text('Recorded'), findsOneWidget);
    await capture(tester, 'supplier_shipment_recorded');
    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pumpAndSettle();
  });

  testWidgets('exporter origin and handling history screenshots', (tester) async {
    tester.view.physicalSize = const Size(828, 1792); tester.view.devicePixelRatio = 2;
    addTearDown(tester.view.resetPhysicalSize); addTearDown(tester.view.resetDevicePixelRatio);
    auth.session.value = const Session(userId: exporterId, email: 'krishane@example.test', fullName: 'Krishane Ann Remonde', role: UserRole.buyer, accessToken: 'mock-token');
    await showScreen(tester, const SourcingScreen(supplier: false));
    await capture(tester, 'exporter_marketplace');
    await showScreen(tester, const BatchHistoryScreen(batchId: batchId), navigation: false);
    expect(find.textContaining('Krishane Ann Remonde'), findsOneWidget);
    expect(find.textContaining('Origin: Junrey Gonzales'), findsOneWidget);
    await tester.tap(find.text('Verify on Sepolia').first); await tester.pumpAndSettle();
    await capture(tester, 'batch_verification_origin');
    await tester.drag(find.byType(ListView).first, const Offset(0, -750)); await tester.pumpAndSettle();
    await capture(tester, 'batch_verification_full_history');
    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pumpAndSettle();
  });
}
