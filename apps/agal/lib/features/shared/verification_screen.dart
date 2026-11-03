import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../core/auth/auth_controller.dart';
import '../../core/routes/app_routes.dart';
import '../../data/remote/agal_api_client.dart';
import 'agal_widgets.dart';

/// The Supplier/Buyer "look this batch up and verify it" tab -- distinct
/// from Home, where they act on batches that are already theirs to act
/// on. This is for checking *any* batch's chain of custody against the
/// live Sepolia record, including one a counterpart just told you about
/// over chat, not only the ones already in your own worklist.
class VerificationScreen extends StatefulWidget {
  const VerificationScreen({super.key});

  @override
  State<VerificationScreen> createState() => _VerificationScreenState();
}

class _VerificationScreenState extends State<VerificationScreen> {
  final _idController = TextEditingController();
  late Future<List<Map<String, dynamic>>> _myBatchesFuture;
  String? _lookupError;

  @override
  void initState() {
    super.initState();
    _myBatchesFuture = _loadMyBatches();
  }

  Future<List<Map<String, dynamic>>> _loadMyBatches() {
    final myId = Get.find<AuthController>().session.value!.userId;
    return Get.find<AgalApiClient>().listBatches(holderId: myId);
  }

  Future<void> _lookUp() async {
    final id = _idController.text.trim();
    setState(() => _lookupError = null);
    if (id.isEmpty) return;
    try {
      await Get.find<AgalApiClient>().getBatch(id);
      if (mounted) Get.toNamed(Routes.batchHistoryPath(id));
    } catch (_) {
      if (mounted)
        setState(() => _lookupError = "Couldn't find a batch with that id.");
    }
  }

  @override
  void dispose() {
    _idController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(title: const Text('Batches & Verification')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          AgalSurface(
            padding: EdgeInsets.zero,
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Look up any batch',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    "Paste a batch ID to check its chain of custody against the live record on Sepolia.",
                    style: TextStyle(
                      fontSize: 13,
                      color: colors.onSurfaceVariant,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _idController,
                          decoration: const InputDecoration(
                            hintText: 'Batch ID',
                          ),
                          onSubmitted: (_) => _lookUp(),
                        ),
                      ),
                      const SizedBox(width: 8),
                      FilledButton(
                        onPressed: _lookUp,
                        child: const Text('Verify'),
                      ),
                    ],
                  ),
                  if (_lookupError != null) ...[
                    const SizedBox(height: 8),
                    Text(
                      _lookupError!,
                      style: TextStyle(color: colors.error, fontSize: 13),
                    ),
                  ],
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),
          Text('Your batches', style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 8),
          FutureBuilder<List<Map<String, dynamic>>>(
            future: _myBatchesFuture,
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const Padding(
                  padding: EdgeInsets.all(24),
                  child: Center(child: CircularProgressIndicator()),
                );
              }
              if (snapshot.hasError) {
                return Padding(
                  padding: const EdgeInsets.all(16),
                  child: Text('Failed to load: ${snapshot.error}'),
                );
              }
              final batches = snapshot.data ?? [];
              if (batches.isEmpty) {
                return Padding(
                  padding: const EdgeInsets.all(16),
                  child: Text(
                    "You don't currently hold any batches.",
                    style: TextStyle(color: colors.onSurfaceVariant),
                  ),
                );
              }
              return Column(
                children: batches
                    .map(
                      (batch) => Padding(
                        padding: const EdgeInsets.only(bottom: 8),
                        child: AgalSurface(
                          padding: EdgeInsets.zero,
                          child: ListTile(
                            title: Text(batch['species'] as String),
                            subtitle: Text(
                              '${batch['estimated_weight_kg']} ${batch['unit']} · ${batch['status']}',
                            ),
                            trailing: const Icon(Icons.chevron_right),
                            onTap: () => Get.toNamed(
                              Routes.batchHistoryPath(batch['id'] as String),
                            ),
                          ),
                        ),
                      ),
                    )
                    .toList(),
              );
            },
          ),
        ],
      ),
    );
  }
}
