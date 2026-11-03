import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:intl/intl.dart';
import 'package:uuid/uuid.dart';

import '../../core/auth/auth_controller.dart';
import '../../core/models/enums.dart';
import '../../core/theme/app_theme.dart';
import '../../data/local/database.dart';
import '../../data/sync/sync_scheduler.dart';
import '../shared/agal_widgets.dart';
import '../shared/custody_event_labels.dart';

class FarmerBatchDetailScreen extends StatefulWidget {
  const FarmerBatchDetailScreen({super.key, required this.batchId});
  final String batchId;
  @override
  State<FarmerBatchDetailScreen> createState() =>
      _FarmerBatchDetailScreenState();
}

class _FarmerBatchDetailScreenState extends State<FarmerBatchDetailScreen> {
  bool _saving = false;
  Future<void> _add(CustodyEventType type) async {
    setState(() => _saving = true);
    try {
      final session = Get.find<AuthController>().session.value!;
      await Get.find<AppDatabase>().insertCustodyEvent(
        id: const Uuid().v4(),
        batchId: widget.batchId,
        eventType: type,
        actorId: session.userId,
        actorRole: session.role,
        occurredAt: DateTime.now(),
        payloadJson: jsonEncode({}),
      );
      await Get.find<SyncScheduler>().refreshCounts();
    } catch (_) {
      if (mounted)
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Could not save the update. Try again.'),
          ),
        );
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: Text(batchLabel(widget.batchId))),
    body: StreamBuilder<LocalBatch?>(
      stream: Get.find<AppDatabase>().watchBatch(widget.batchId),
      builder: (context, snapshot) {
        final batch = snapshot.data;
        if (batch == null)
          return const Center(child: Text('Batch not found on this device.'));
        final next = switch (batch.status) {
          'harvested' => CustodyEventType.dryingStarted,
          'drying' => CustodyEventType.dryingCompleted,
          _ => null,
        };
        return ListView(
          padding: const EdgeInsets.all(18),
          children: [
            AgalSurface(
              child: Column(
                children: [
                  Row(
                    children: [
                      const Icon(Icons.inventory_2_outlined),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              speciesLabel(batch.species),
                              style: const TextStyle(
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                            const SizedBox(height: 5),
                            Text('${batch.estimatedWeightKg} kg'),
                            const SizedBox(height: 5),
                            Text(
                              Get.find<AuthController>()
                                      .session
                                      .value
                                      ?.municipality ??
                                  'Farm location',
                              style: const TextStyle(
                                color: AgalColors.muted,
                                fontSize: 12,
                              ),
                            ),
                          ],
                        ),
                      ),
                      SeaweedArt(size: 62),
                    ],
                  ),
                  BatchProgress(status: batch.status),
                ],
              ),
            ),
            const SectionLabel('Batch History'),
            StreamBuilder<List<LocalCustodyEvent>>(
              stream: Get.find<AppDatabase>().watchEventsForBatch(
                widget.batchId,
              ),
              builder: (context, snapshot) {
                final events = snapshot.data ?? [];
                return Column(
                  children: events
                      .map(
                        (e) => IntrinsicHeight(
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.stretch,
                            children: [
                              Column(
                                children: [
                                  Icon(
                                    e.synced
                                        ? Icons.check_circle
                                        : Icons.schedule,
                                    color: AgalColors.mint,
                                    size: 25,
                                  ),
                                  Expanded(
                                    child: Container(
                                      width: 2,
                                      color: const Color(0xFF2C7963),
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(width: 16),
                              Expanded(
                                child: Padding(
                                  padding: const EdgeInsets.only(bottom: 24),
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        custodyEventLabels[e.eventType] ??
                                            e.eventType,
                                        style: const TextStyle(
                                          fontWeight: FontWeight.w600,
                                        ),
                                      ),
                                      const SizedBox(height: 5),
                                      Text(
                                        DateFormat('MMM d, yyyy · h:mm a')
                                            .format(e.occurredAt.toLocal()),
                                        style: const TextStyle(
                                          color: Color(0xFFACC8BD),
                                          fontSize: 12,
                                        ),
                                      ),
                                      const SizedBox(height: 3),
                                      Text(
                                        e.synced
                                            ? 'Synced to Agal'
                                            : 'Saved offline · Pending sync',
                                        style: const TextStyle(
                                          color: Color(0xFFACC8BD),
                                          fontSize: 12,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      )
                      .toList(),
                );
              },
            ),
            if (next != null)
              FilledButton(
                onPressed: _saving ? null : () => _add(next),
                child: Text(
                  _saving
                      ? 'Saving…'
                      : next == CustodyEventType.dryingStarted
                      ? 'Start Drying'
                      : 'Finish Drying · Ready for Pickup',
                ),
              )
            else if (batch.status == 'dried')
              const AgalSurface(
                child: Row(
                  children: [
                    Icon(Icons.local_shipping_outlined),
                    SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'Ready for pickup. Your supplier can verify this batch and confirm receipt.',
                      ),
                    ),
                  ],
                ),
              ),
          ],
        );
      },
    ),
  );
}
