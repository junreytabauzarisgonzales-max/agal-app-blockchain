import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:uuid/uuid.dart';

import '../../core/auth/auth_controller.dart';
import '../../core/models/enums.dart';
import '../../core/routes/app_routes.dart';
import '../../data/remote/agal_api_client.dart';
import 'agal_widgets.dart';

class VerifyHandoverScreen extends StatefulWidget {
  const VerifyHandoverScreen({super.key, required this.batchId});
  final String batchId;
  @override
  State<VerifyHandoverScreen> createState() => _VerifyHandoverScreenState();
}

class _VerifyHandoverScreenState extends State<VerifyHandoverScreen> {
  late final Future<Map<String, dynamic>> _batch;
  final _form = GlobalKey<FormState>();
  final _weight = TextEditingController();
  final _remarks = TextEditingController();
  final _gradeId = const Uuid().v4();
  final _transferId = const Uuid().v4();
  String _quality = 'Excellent';
  double _moisture = 22;
  bool _saving = false;
  bool _gradeSaved = false;
  String? _error;
  @override
  void initState() {
    super.initState();
    _batch = Get.find<AgalApiClient>().getBatch(widget.batchId).then((b) {
      _weight.text = '${b['estimated_weight_kg']}';
      return b;
    });
  }

  @override
  void dispose() {
    _weight.dispose();
    _remarks.dispose();
    super.dispose();
  }

  Future<void> _confirm() async {
    if (!_form.currentState!.validate()) return;
    setState(() {
      _saving = true;
      _error = null;
    });
    try {
      final api = Get.find<AgalApiClient>();
      final supplier =
          Get.find<AuthController>().session.value!.role == UserRole.supplier;
      final payload = {
        'verified_weight_kg': double.parse(_weight.text),
        'moisture_percent': _moisture.round(),
        'quality_grade': _quality.toLowerCase(),
        'remarks': _remarks.text.trim(),
      };
      if (!_gradeSaved) {
        await api.createCustodyEvent({
          'id': _gradeId,
          'batch_id': widget.batchId,
          'event_type': 'quality_graded',
          'occurred_at': DateTime.now().toUtc().toIso8601String(),
          'payload': payload,
        });
        _gradeSaved = true;
      }
      await api.createCustodyEvent({
        'id': _transferId,
        'batch_id': widget.batchId,
        'event_type': supplier
            ? 'transferred_to_supplier'
            : 'transferred_to_buyer',
        'occurred_at': DateTime.now().toUtc().toIso8601String(),
        'payload': {
          ...payload,
          'confirmation': 'confirmed_by_receiving_account',
        },
      });
      if (mounted) Get.back(result: true);
    } catch (_) {
      if (mounted)
        setState(
          () => _error = 'Could not confirm the transfer. Check your connection and retry.',
        );
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Verify & Handover')),
    body: FutureBuilder<Map<String, dynamic>>(
      future: _batch,
      builder: (context, snapshot) {
        if (snapshot.hasError)
          return const EmptyState(
            icon: Icons.cloud_off,
            title: 'Could not load batch',
            message: 'Go back and try again when connected.',
          );
        if (!snapshot.hasData)
          return const Center(child: CircularProgressIndicator());
        final b = snapshot.data!;
        final supplier =
            Get.find<AuthController>().session.value!.role == UserRole.supplier;
        final eligible = b['status'] == (supplier ? 'dried' : 'with_supplier');
        return ListView(
          padding: const EdgeInsets.all(18),
          children: [
            AgalSurface(
              child: Form(
                key: _form,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                batchLabel(widget.batchId),
                                style: const TextStyle(
                                  fontWeight: FontWeight.w800,
                                  fontSize: 20,
                                ),
                              ),
                              const SizedBox(height: 8),
                              Text(speciesLabel('${b['species']}')),
                            ],
                          ),
                        ),
                        const SeaweedArt(size: 64),
                      ],
                    ),
                    TextButton.icon(
                      onPressed: () =>
                          Get.toNamed(Routes.batchHistoryPath(widget.batchId)),
                      icon: const Icon(Icons.verified_outlined, size: 18),
                      label: const Text('View provenance & verify on-chain'),
                    ),
                    const SectionLabel('Verified scale weight'),
                    TextFormField(
                      controller: _weight,
                      enabled: !_gradeSaved,
                      keyboardType: const TextInputType.numberWithOptions(
                        decimal: true,
                      ),
                      decoration: const InputDecoration(suffixText: 'kg'),
                      validator: (v) {
                        final n = double.tryParse(v ?? '');
                        return n == null || !n.isFinite || n <= 0
                            ? 'Enter a valid weight'
                            : null;
                      },
                    ),
                    const SectionLabel('Quality rating'),
                    const Text(
                      'Moisture level',
                      style: TextStyle(fontSize: 12),
                    ),
                    Row(
                      children: [
                        Expanded(
                          child: Slider(
                            value: _moisture,
                            min: 0,
                            max: 100,
                            divisions: 100,
                            onChanged: _gradeSaved
                                ? null
                                : (v) => setState(() => _moisture = v),
                          ),
                        ),
                        Text('${_moisture.round()}%'),
                      ],
                    ),
                    const Text(
                      'Overall quality',
                      style: TextStyle(fontSize: 12),
                    ),
                    const SizedBox(height: 10),
                    Wrap(
                      spacing: 8,
                      children: ['Excellent', 'Good', 'Fair']
                          .map(
                            (q) => ChoiceChip(
                              label: Text(q),
                              selected: q == _quality,
                              onSelected: _gradeSaved
                                  ? null
                                  : (_) => setState(() => _quality = q),
                            ),
                          )
                          .toList(),
                    ),
                    const SectionLabel('Remarks (optional)'),
                    TextFormField(
                      controller: _remarks,
                      enabled: !_gradeSaved,
                      maxLines: 3,
                      maxLength: 1000,
                      decoration: const InputDecoration(hintText: 'Add notes…'),
                    ),
                    if (!eligible)
                      const Text(
                        'This batch is no longer available for this transfer.',
                      ),
                    if (_error != null)
                      Text(_error!, style: const TextStyle(color: Colors.red)),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 18),
            FilledButton(
              onPressed: _saving || !eligible ? null : _confirm,
              child: Text(
                _saving
                    ? 'Confirming…'
                    : supplier
                    ? 'Confirm Receipt & Record Transfer'
                    : 'Confirm Purchase & Record Transfer',
              ),
            ),
            const SizedBox(height: 12),
            const Text(
              'Confirmation is recorded under your signed-in account and added to the batch’s audit trail.',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 12, color: Color(0xFFACC8BD)),
            ),
          ],
        );
      },
    ),
  );
}
