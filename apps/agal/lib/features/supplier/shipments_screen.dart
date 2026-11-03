import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../core/auth/auth_controller.dart';
import '../../core/theme/app_theme.dart';
import '../../data/remote/agal_api_client.dart';
import '../shared/agal_widgets.dart';
import 'shipment_service.dart';

class ShipmentsScreen extends StatefulWidget {
  const ShipmentsScreen({super.key});
  @override
  State<ShipmentsScreen> createState() => _ShipmentsScreenState();
}

class _ShipmentsScreenState extends State<ShipmentsScreen> {
  final _destination = TextEditingController();
  final _selected = <String>{};
  late final Future<List<Map<String, dynamic>>> _future;
  bool _saving = false;
  String? _error;
  Map<String, dynamic>? _draft;
  @override
  void initState() {
    super.initState();
    _future = Get.find<AgalApiClient>().listBatches(
      holderId: Get.find<AuthController>().session.value!.userId,
      status: 'with_supplier',
    );
  }

  @override
  void dispose() {
    _destination.dispose();
    super.dispose();
  }

  Future<void> _save(List<Map<String, dynamic>> batches) async {
    if (_selected.isEmpty || _destination.text.trim().isEmpty) {
      setState(
        () => _error = 'Choose at least one batch and enter a destination.',
      );
      return;
    }
    setState(() {
      _saving = true;
      _error = null;
    });
    final userId = Get.find<AuthController>().session.value!.userId;
    try {
      final service = Get.find<ShipmentService>();
      _draft ??= await service.draft(
        userId,
        _destination.text.trim(),
        batches.where((b) => _selected.contains(b['id'])).toList(),
      );
      await service.publish(userId, _draft!);
      if (mounted)
        setState(() {
          _selected.clear();
          _destination.clear();
          _draft = null;
        });
    } catch (_) {
      if (mounted)
        setState(
          () => _error = 'Manifest saved on this device. Reconnect and retry to record the batch links.',
        );
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  Future<void> _retry(Map<String, dynamic> manifest) async {
    setState(() => _saving = true);
    try {
      await Get.find<ShipmentService>().publish(
        Get.find<AuthController>().session.value!.userId,
        manifest,
      );
    } catch (_) {
      if (mounted)
        setState(
          () => _error =
              'Could not record the shipment. Try again when connected.',
        );
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final shipments = Get.find<ShipmentService>().list(
      Get.find<AuthController>().session.value!.userId,
    );
    return Scaffold(
      appBar: AppBar(title: const Text('Bundle a Shipment')),
      body: FutureBuilder<List<Map<String, dynamic>>>(
        future: _future,
        builder: (context, snapshot) {
          if (snapshot.hasError)
            return const EmptyState(
              icon: Icons.cloud_off_outlined,
              title: 'Connect to load inventory',
              message: 'Your saved manifests will remain on this device.',
            );
          if (!snapshot.hasData)
            return const Center(child: CircularProgressIndicator());
          final batches = snapshot.data!;
          final total = batches
              .where((b) => _selected.contains(b['id']))
              .fold<double>(
                0,
                (s, b) =>
                    s + (double.tryParse('${b['estimated_weight_kg']}') ?? 0),
              );
          return ListView(
            padding: const EdgeInsets.all(18),
            children: [
              const Text(
                'From batches to one shipment.',
                style: TextStyle(fontSize: 23, fontWeight: FontWeight.w700),
              ),
              const SizedBox(height: 8),
              const Text(
                'Select inventory batches and record a shared shipment reference in each batch’s handling history.',
                style: TextStyle(
                  color: Color(0xFFACC8BD),
                  fontSize: 13,
                  height: 1.5,
                ),
              ),
              const SizedBox(height: 20),
              AgalSurface(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Destination',
                      style: TextStyle(fontWeight: FontWeight.w600),
                    ),
                    const SizedBox(height: 10),
                    TextField(
                      controller: _destination,
                      minLines: 2,
                      maxLines: 2,
                      enabled: !_saving && _draft == null,
                      decoration: const InputDecoration(
                        hintText: 'Exporter or warehouse',
                        prefixIcon: Icon(Icons.local_shipping_outlined),
                      ),
                    ),
                    const SectionLabel('Select batches'),
                    if (batches.isEmpty)
                      const Text(
                        'Confirm receipt of a batch to add it to your inventory.',
                      ),
                    ...batches.map(
                      (b) => CheckboxListTile(
                        contentPadding: EdgeInsets.zero,
                        value: _selected.contains(b['id']),
                        controlAffinity: ListTileControlAffinity.leading,
                        title: Text(
                          batchLabel('${b['id']}'),
                          style: const TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        subtitle: Text(
                          '${speciesLabel('${b['species']}')} · ${b['estimated_weight_kg']} kg',
                          style: const TextStyle(fontSize: 12),
                        ),
                        onChanged: _saving || _draft != null
                            ? null
                            : (v) => setState(() {
                                if (v == true) {
                                  _selected.add('${b['id']}');
                                } else {
                                  _selected.remove(b['id']);
                                }
                              }),
                      ),
                    ),
                    const Divider(),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Expanded(child: Text('${_selected.length} batches selected')),
                        Text(
                          '${total.toStringAsFixed(0)} kg',
                          style: const TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                      ],
                    ),
                    if (_error != null)
                      Padding(
                        padding: const EdgeInsets.only(top: 12),
                        child: Text(
                          _error!,
                          style: const TextStyle(
                            color: Colors.red,
                            fontSize: 12,
                          ),
                        ),
                      ),
                    const SizedBox(height: 18),
                    SizedBox(
                      width: double.infinity,
                      child: FilledButton.icon(
                        onPressed: _saving ? null : () => _save(batches),
                        icon: const Icon(Icons.inventory_2_outlined, size: 18),
                        label: Text(
                          _saving
                              ? 'Recording…'
                              : _draft == null
                              ? 'Create Shipment'
                              : 'Retry Recording Shipment',
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SectionLabel('Shipment manifests'),
              if (shipments.isEmpty)
                const Text(
                  'Your bundled shipments will appear here.',
                  style: TextStyle(color: Color(0xFFACC8BD), fontSize: 13),
                ),
              ...shipments.map(
                (s) => Padding(
                  padding: const EdgeInsets.only(bottom: 12),
                  child: AgalSurface(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            const Icon(
                              Icons.local_shipping_outlined,
                              color: AgalColors.forest,
                            ),
                            const SizedBox(width: 10),
                            Expanded(
                              child: Text(
                                '${s['destination']}',
                                style: const TextStyle(
                                  fontWeight: FontWeight.w700,
                                ),
                              ),
                            ),
                            Text(
                              s['status'] == 'recorded' ? 'Recorded' : 'Draft',
                              style: const TextStyle(
                                color: AgalColors.muted,
                                fontSize: 12,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 10),
                        Text(
                          '${(s['batch_ids'] as List).length} batches · ${s['total_weight_kg']} kg',
                        ),
                        const SizedBox(height: 7),
                        Text(
                          'Reference: ${s['id']}',
                          style: const TextStyle(
                            color: AgalColors.muted,
                            fontSize: 10,
                          ),
                        ),
                        if (s['status'] != 'recorded')
                          TextButton(
                            onPressed: _saving ? null : () => _retry(s),
                            child: const Text('Retry recording batch links'),
                          ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}
