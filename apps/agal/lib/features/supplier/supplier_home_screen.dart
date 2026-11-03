import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:intl/intl.dart';

import '../../core/auth/auth_controller.dart';
import '../../core/routes/app_routes.dart';
import '../../core/theme/app_theme.dart';
import '../../data/remote/agal_api_client.dart';
import '../shared/agal_widgets.dart';
import '../shared/app_logo.dart';

class SupplierHomeScreen extends StatefulWidget {
  const SupplierHomeScreen({super.key});
  @override
  State<SupplierHomeScreen> createState() => _SupplierHomeScreenState();
}

class _SupplierHomeScreenState extends State<SupplierHomeScreen> {
  late Future<List<dynamic>> _future;
  @override
  void initState() {
    super.initState();
    _future = _load();
  }

  Future<List<dynamic>> _load() async {
    final api = Get.find<AgalApiClient>();
    final myId = Get.find<AuthController>().session.value!.userId;
    final batches = await api.listBatches(
      holderId: myId,
      status: 'with_supplier',
    );
    final all = await api.listBatches();
    final histories = await Future.wait(
      all.map((b) => api.getBatchEvents('${b['id']}')),
    );
    final sales = histories
        .expand((h) => h)
        .where(
          (e) => e['event_type'] == 'payment_recorded' && e['actor_id'] == myId,
        )
        .toList();
    return [batches, sales, all.where((b) => b['status'] == 'dried').length];
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(
      centerTitle: false,
      title: const Row(
        children: [
          AppLogo(size: 32),
          SizedBox(width: 10),
          Text('Supplier Dashboard'),
        ],
      ),
    ),
    body: RefreshIndicator(
      onRefresh: () async {
        setState(() { _future = _load(); });
        await _future;
      },
      child: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          const Text(
            'Your trade, at a glance.',
            style: TextStyle(color: Color(0xFFACC8BD), fontSize: 14),
          ),
          const SizedBox(height: 6),
          Text(
            Get.find<AuthController>().session.value!.fullName,
            style: const TextStyle(fontSize: 27, fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 22),
          FutureBuilder<List<dynamic>>(
            future: _future,
            builder: (context, snapshot) {
              if (snapshot.hasError)
                return const EmptyState(
                  icon: Icons.cloud_off,
                  title: 'Connect to load your dashboard',
                  message: 'Pull down to try again.',
                );
              if (!snapshot.hasData)
                return const Center(child: CircularProgressIndicator());
              final batches = (snapshot.data![0] as List)
                  .cast<Map<String, dynamic>>();
              final sales = (snapshot.data![1] as List)
                  .cast<Map<String, dynamic>>();
              final amount = sales.fold<double>(0, (s, e) {
                final p = e['payload'] as Map;
                return s +
                    (double.tryParse(
                          '${p['amount_php'] ?? p['amount'] ?? 0}',
                        ) ??
                        0);
              });
              final weight = batches.fold<double>(
                0,
                (s, b) =>
                    s + (double.tryParse('${b['estimated_weight_kg']}') ?? 0),
              );
              return Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  AgalSurface(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Row(
                          children: [
                            Icon(Icons.payments_outlined, size: 20),
                            SizedBox(width: 8),
                            Text(
                              'RECORDED SALES',
                              style: TextStyle(
                                fontSize: 11,
                                letterSpacing: 1.4,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 14),
                        Text(
                          '₱${NumberFormat('#,##0').format(amount)}',
                          style: const TextStyle(
                            fontSize: 40,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          '${sales.length} payment records · PHP',
                          style: const TextStyle(
                            color: AgalColors.muted,
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 14),
                  Row(
                    children: [
                      Expanded(
                        child: _stat('${batches.length}', 'Inventory batches'),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: _stat(
                          '${weight.toStringAsFixed(0)} kg',
                          'Ready to bundle',
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 18),
                  FilledButton.icon(
                    onPressed: () => Get.toNamed(Routes.shipments),
                    icon: const Icon(Icons.local_shipping_outlined),
                    label: const Text('Bundle Batches into Shipment'),
                  ),
                  const SizedBox(height: 10),
                  OutlinedButton.icon(
                    onPressed: () => Get.toNamed(Routes.pickups),
                    icon: const Icon(Icons.grass_outlined),
                    label: Text(
                      'Pickup Dashboard · ${snapshot.data![2]} ready',
                    ),
                  ),
                  const SectionLabel('Batches in your inventory'),
                  ...batches
                      .take(4)
                      .map(
                        (b) => Padding(
                          padding: const EdgeInsets.only(bottom: 12),
                          child: AgalSurface(
                            padding: const EdgeInsets.all(14),
                            child: InkWell(
                              onTap: () => Get.toNamed(
                                Routes.batchHistoryPath('${b['id']}'),
                              ),
                              child: Row(
                                children: [
                                  SeaweedArt(
                                    size: 58,
                                    tambalang:
                                        speciesLabel('${b['species']}') ==
                                        'Tambalang',
                                  ),
                                  const SizedBox(width: 12),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          batchLabel('${b['id']}'),
                                          style: const TextStyle(
                                            fontWeight: FontWeight.w700,
                                          ),
                                        ),
                                        const SizedBox(height: 5),
                                        Text(
                                          '${speciesLabel('${b['species']}')} · ${b['estimated_weight_kg']} kg',
                                          style: const TextStyle(
                                            color: AgalColors.muted,
                                            fontSize: 12,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                  const Icon(Icons.chevron_right),
                                ],
                              ),
                            ),
                          ),
                        ),
                      ),
                ],
              );
            },
          ),
        ],
      ),
    ),
  );
  Widget _stat(String value, String label) => AgalSurface(
    child: Column(
      children: [
        Text(
          value,
          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 25),
        ),
        const SizedBox(height: 5),
        Text(
          label,
          style: const TextStyle(color: AgalColors.muted, fontSize: 11),
        ),
      ],
    ),
  );
}
