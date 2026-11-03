import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:get/get.dart';
import 'package:intl/intl.dart';

import '../../core/theme/app_theme.dart';
import '../../core/auth/auth_controller.dart';
import '../../data/remote/agal_api_client.dart';
import 'agal_widgets.dart';
import 'custody_event_labels.dart';
import 'location_picker.dart';

class BatchHistoryScreen extends StatefulWidget {
  const BatchHistoryScreen({super.key, required this.batchId});
  final String batchId;
  @override
  State<BatchHistoryScreen> createState() => _BatchHistoryScreenState();
}

class _BatchHistoryScreenState extends State<BatchHistoryScreen> {
  late Future<List<dynamic>> _future;
  final Map<String, Future<Map<String, dynamic>>> _verifications = {};
  @override
  void initState() {
    super.initState();
    _future = _load();
  }

  Future<List<dynamic>> _load() {
    final api = Get.find<AgalApiClient>();
    return Future.wait([
      api.getBatch(widget.batchId),
      api.getBatchEvents(widget.batchId),
      api.listDirectory(),
    ]);
  }

  void _verify(String id) => setState(
    () { _verifications[id] = Get.find<AgalApiClient>().verifyCustodyEvent(id); },
  );
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(
      title: const Text('Batch Provenance'),
      actions: [
        IconButton(
          tooltip: 'Refresh history',
          onPressed: () => setState(() {
            _verifications.clear();
            _future = _load();
          }),
          icon: const Icon(Icons.refresh),
        ),
      ],
    ),
    body: FutureBuilder<List<dynamic>>(
      future: _future,
      builder: (context, snapshot) {
        if (snapshot.hasError)
          return const EmptyState(
            icon: Icons.cloud_off_outlined,
            title: 'Could not load provenance',
            message: 'Check your connection and tap refresh.',
          );
        if (!snapshot.hasData)
          return const Center(child: CircularProgressIndicator());
        final batch = snapshot.data![0] as Map<String, dynamic>;
        final events = (snapshot.data![1] as List).cast<Map<String, dynamic>>();
        final people = {
          for (final p in snapshot.data![2] as List) p['id']: p['full_name'],
        };
        final lat = double.tryParse('${batch['harvest_latitude']}');
        final lng = double.tryParse('${batch['harvest_longitude']}');
        return ListView(
          padding: const EdgeInsets.all(18),
          children: [
            Text(
              'Viewing as ${Get.find<AuthController>().session.value!.fullName}',
              style: const TextStyle(fontSize: 11, color: Color(0xFFACC8BD)),
            ),
            const SizedBox(height: 12),
            AgalSurface(
              child: Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          batchLabel(widget.batchId),
                          style: const TextStyle(
                            fontSize: 22,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                        const SizedBox(height: 7),
                        Text(speciesLabel('${batch['species']}')),
                        const SizedBox(height: 4),
                        Text(
                          '${batch['estimated_weight_kg']} ${batch['unit']}',
                        ),
                      ],
                    ),
                  ),
                  const SeaweedArt(size: 66),
                ],
              ),
            ),
            const SizedBox(height: 12),
            Text(
              'Origin: ${people[batch['farmer_id']] ?? 'Farmer'} · Farmer’s harvest record',
              style: const TextStyle(color: AgalColors.mint, fontSize: 12),
            ),
            const SizedBox(height: 24),
            ...events.map((event) {
              final id = '${event['id']}';
              final anchored = event['on_chain_status'] == 'anchored';
              final payload = event['payload'] as Map<String, dynamic>? ?? {};
              return IntrinsicHeight(
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Column(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(6),
                          decoration: const BoxDecoration(
                            color: AgalColors.mint,
                            shape: BoxShape.circle,
                          ),
                          child: Icon(
                            anchored ? Icons.verified_outlined : Icons.schedule,
                            size: 20,
                            color: AgalColors.deep,
                          ),
                        ),
                        Expanded(
                          child: Container(
                            width: 2,
                            color: const Color(0xFF439B7A),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Padding(
                        padding: const EdgeInsets.only(bottom: 22),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              custodyEventLabels[event['event_type']] ??
                                  '${event['event_type']}',
                              style: const TextStyle(
                                fontWeight: FontWeight.w700,
                                fontSize: 16,
                              ),
                            ),
                            const SizedBox(height: 5),
                            Text(
                              'By: ${people[event['actor_id']] ?? 'Agal partner'} (${event['actor_role']})',
                              style: const TextStyle(
                                fontSize: 12,
                                color: Color(0xFFACC8BD),
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              DateFormat('MMM d, yyyy · h:mm a').format(
                                DateTime.parse('${event['occurred_at']}')
                                    .toLocal(),
                              ),
                              style: const TextStyle(
                                fontSize: 12,
                                color: Color(0xFFACC8BD),
                              ),
                            ),
                            if ((payload['notes'] as String? ?? '').isNotEmpty)
                              Padding(padding: const EdgeInsets.only(top: 6), child: Text('${payload['notes']}',
                                style: const TextStyle(fontSize: 12, color: Color(0xFFACC8BD)))),
                            if (payload['quality_grade'] != null)
                              Padding(
                                padding: const EdgeInsets.only(top: 6),
                                child: Text(
                                  'Quality: ${payload['quality_grade']} · Moisture: ${payload['moisture_percent']}%\nVerified weight: ${payload['verified_weight_kg']} kg',
                                  style: const TextStyle(
                                    fontSize: 12,
                                    color: AgalColors.mint,
                                  ),
                                ),
                              ),
                            if ((payload['remarks'] as String? ?? '')
                                .isNotEmpty)
                              Text(
                                '${payload['remarks']}',
                                style: const TextStyle(fontSize: 12),
                              ),
                            const SizedBox(height: 8),
                            if (!anchored)
                              Text(
                                event['on_chain_status'] == 'failed'
                                    ? 'Anchoring failed · Not verified'
                                    : 'Pending blockchain anchoring',
                                style: const TextStyle(
                                  fontSize: 11,
                                  color: Color(0xFFFFBA71),
                                ),
                              )
                            else if (_verifications[id] == null)
                              TextButton.icon(
                                onPressed: () => _verify(id),
                                icon: const Icon(
                                  Icons.verified_user_outlined,
                                  size: 17,
                                ),
                                label: const Text(
                                  'Verify on Sepolia',
                                  style: TextStyle(fontSize: 12),
                                ),
                              )
                            else
                              FutureBuilder<Map<String, dynamic>>(
                                future: _verifications[id],
                                builder: (context, result) {
                                  if (result.connectionState !=
                                      ConnectionState.done)
                                    return const LinearProgressIndicator();
                                  if (result.hasError)
                                    return TextButton(
                                      onPressed: () => _verify(id),
                                      child: const Text(
                                        'Could not reach Sepolia · Retry',
                                      ),
                                    );
                                  final verified =
                                      result.data!['verified'] == true;
                                  return Text(
                                    verified
                                        ? 'Verified · Matches the record on Sepolia'
                                        : 'Warning · Does not match the on-chain record',
                                    style: TextStyle(
                                      color: verified
                                          ? AgalColors.mint
                                          : const Color(0xFFFF7777),
                                      fontSize: 12,
                                      fontWeight: FontWeight.w700,
                                    ),
                                  );
                                },
                              ),
                            if (event['on_chain_tx_hash'] != null)
                              InkWell(
                                onTap: () async {
                                  await Clipboard.setData(
                                    ClipboardData(
                                      text: '${event['on_chain_tx_hash']}',
                                    ),
                                  );
                                  if (context.mounted)
                                    ScaffoldMessenger.of(context).showSnackBar(
                                      const SnackBar(
                                        content: Text(
                                          'Transaction hash copied',
                                        ),
                                      ),
                                    );
                                },
                                child: Row(
                                  children: [
                                    Expanded(
                                      child: Text(
                                        'Tx: ${event['on_chain_tx_hash']}',
                                        maxLines: 1,
                                        overflow: TextOverflow.ellipsis,
                                        style: const TextStyle(
                                          fontSize: 10,
                                          color: Color(0xFFACC8BD),
                                        ),
                                      ),
                                    ),
                                    const Icon(
                                      Icons.copy,
                                      size: 13,
                                      color: AgalColors.mint,
                                    ),
                                  ],
                                ),
                              ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              );
            }),
            if (lat != null && lng != null)
              AgalSurface(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Harvest location',
                      style: TextStyle(fontWeight: FontWeight.w700),
                    ),
                    const SizedBox(height: 10),
                    MapPreview(latitude: lat, longitude: lng),
                  ],
                ),
              ),
            const SizedBox(height: 18),
            const Text(
              'Blockchain verification checks recorded data for changes. It does not independently certify the physical harvest.',
              style: TextStyle(
                fontSize: 11,
                color: Color(0xFFACC8BD),
                height: 1.5,
              ),
            ),
          ],
        );
      },
    ),
  );
}
